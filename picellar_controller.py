# -*- coding: utf-8 -*-
import os
import glob
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import sqlite3
import datetime
import threading
import signal
import sys
import socket
import struct
import picellar_api
import picellar_config
import picellar_sensors
import picellar_sharedData
from subprocess import call


COMPRESSOR_LAST_START_TIME = 0
COMPRESSOR_LAST_STOP_TIME = 0
recoveryOn = 0
lastCompressorEnableTime = 0
wd_started = False
wd_file=0

def setMode(isAuto):
	picellar_sharedData.STATE_MODE_AUTO = isAuto
	print "Changement de mode. IsAuto = " + str(picellar_sharedData.STATE_MODE_AUTO)

def getMode():
	return picellar_sharedData.STATE_MODE_AUTO

def setHeating(toogle):
	if (toogle):
		print "20 Chauffage ON"
		GPIO.output(picellar_config.HEAT_GPIO, 0)
		picellar_sharedData.heatingOn = True
	else:
		print "20 Chauffage OFF"
		GPIO.output(picellar_config.HEAT_GPIO, 1)
		picellar_sharedData.heatingOn = False

def getHeating():
	return picellar_sharedData.heatingOn
		
def setFan(toogle):
	
	if (toogle):
		print "26 Fan ON"
		GPIO.output(picellar_config.FAN_GPIO, 0)
		picellar_sharedData.fanOn = True
	else:
		print "26 Fan OFF"
		GPIO.output(picellar_config.FAN_GPIO, 1)
		picellar_sharedData.fanOn = False
		
def getFan():
	return picellar_sharedData.fanOn
		
def setCooling(toogle):
	
	global COMPRESSOR_LAST_START_TIME
	global COMPRESSOR_LAST_STOP_TIME
	global recoveryOn	
	
	# print("Temp de run restant avant arret de compresseur pour recovery : " + datetime.datetime.fromtimestamp((COMPRESSOR_LAST_START_TIME+picellar_config.COMPRESSOR_TOOGLE_TIME) - int(time.time())).strftime('%H:%M:%S'))
	# print("En format unix : " + str((COMPRESSOR_LAST_START_TIME+picellar_config.COMPRESSOR_TOOGLE_TIME) - int(time.time())))
	# print("Temps de recovery restant : " + datetime.datetime.fromtimestamp((COMPRESSOR_LAST_STOP_TIME+picellar_config.COMPRESSOR_RECOVERY_TIME) - int(time.time())).strftime('%H:%M:%S'))
	# print("En format unix : " + str((COMPRESSOR_LAST_STOP_TIME+picellar_config.COMPRESSOR_RECOVERY_TIME) - int(time.time())))
	# print("Nouvelle Conversion : " + time.strftime('%H:%M:%S', time.gmtime((COMPRESSOR_LAST_STOP_TIME+picellar_config.COMPRESSOR_RECOVERY_TIME) - int(time.time()))))
	
	if (toogle):
	
		
		if ((int(time.time()) > (COMPRESSOR_LAST_START_TIME+picellar_config.COMPRESSOR_TOOGLE_TIME)) & (COMPRESSOR_LAST_START_TIME != 0) & (picellar_sharedData.coolingOn == True)):
			print "Compresseur en activité depuis trop longtemps ... Arret pour recovery"
			print "16 GF OFF"
			GPIO.output(picellar_config.COOL_GPIO, 1)

			COMPRESSOR_LAST_STOP_TIME = int(time.time())
			picellar_sharedData.coolingOn = False
			return
		elif (picellar_sharedData.coolingOn == True):
			print "Temp de run restant avant arret de compresseur pour recovery : " + time.strftime('%H:%M:%S', time.gmtime((COMPRESSOR_LAST_START_TIME+picellar_config.COMPRESSOR_TOOGLE_TIME) - int(time.time())))
	
		
		if ((int(time.time()) < (COMPRESSOR_LAST_STOP_TIME+picellar_config.COMPRESSOR_RECOVERY_TIME)) & (COMPRESSOR_LAST_STOP_TIME != 0)):
			print "Compresseur en recovery ... Démarrage impossible"
			print "Temps de recovery restant : " + time.strftime('%H:%M:%S', time.gmtime((COMPRESSOR_LAST_STOP_TIME+picellar_config.COMPRESSOR_RECOVERY_TIME) - int(time.time())))
			print "16 GF OFF"
			GPIO.output(picellar_config.COOL_GPIO, 1)
			picellar_sharedData.coolingOn = False
			return

			
		print "16 GF ON"
		GPIO.output(picellar_config.COOL_GPIO, 0)
		
		if picellar_sharedData.coolingOn == False:
			COMPRESSOR_LAST_START_TIME = int(time.time())
		
		picellar_sharedData.coolingOn = True
		
	else:
		print "16 GF OFF"
		GPIO.output(picellar_config.COOL_GPIO, 1)
		
		if picellar_sharedData.coolingOn == True:
			COMPRESSOR_LAST_STOP_TIME = int(time.time())
		
		picellar_sharedData.coolingOn = False

def getCooling():
	return picellar_sharedData.coolingOn
	
def hvacControler(current_temp, temp_max, temp_min):
	
	observedTemperature = current_temp
	setTemperatureMax = picellar_config.setTemperatureMax
	setTemperatureMin = picellar_config.setTemperatureMin
	threshold = picellar_config.threshold
	
	#### Regles HVAC v1 ####----------------
	# if(threshold < 0.5):
		# threshold = 0.5
		# print('*** Warning: Threshold too low. Setting to 0.5.')
	#### -----------------------------------
	
	#### Regles HVAC v1 ####----------------
	if(threshold < 0.2):
		threshold = 0.2
		print('*** Warning: Threshold too low. Setting to 0.2.')
	#### -----------------------------------
	
	if((setTemperatureMax <= setTemperatureMin) or ((setTemperatureMax-setTemperatureMin) < (threshold*2))):
		print('*** Error: Overlap between set minimum and maximum temperatures.')
		return
	
	print('Current temperature: '+str(observedTemperature)+' C')
	print('Minimum temperature configured : '+str(setTemperatureMin)+' C')
	print('Maximum temperature configured : '+str(setTemperatureMax)+' C')
	print('Treshold configured : '+str(threshold)+' C')
	print('')
	
	# The A/C (and fan) should be enabled if the observed temperature is warmer than
	# the set temperature, plus the threshold
	
	hotterThanMax = False
	coolerThanMin = False
	
	#### Regles HVAC v1 ####----------------
	
	# Checking to see if it's warmer than the high range (ie. if the A/C should turn on)
	# If the A/C is on right now, it should stay on until it goes past the threshold
	# if(picellar_sharedData.coolingOn and (setTemperatureMax < (observedTemperature+threshold))):
		# hotterThanMax = True
	# If the A/C is not on right now, it should turn on when it hits the threshold
	# if((not picellar_sharedData.coolingOn) and (setTemperatureMax < (observedTemperature-threshold))):
		# hotterThanMax = True

	# Checking to see if it's colder than the low range (ie. if the heater should turn on)
	# If the heater is on right now, it should stay on until it goes past the threshold
	# if(picellar_sharedData.heatingOn and (setTemperatureMin > (observedTemperature-threshold))):
		# coolerThanMin = True
	# If the heater is not on right now, it should turn on when it hits the threshold
	# if((not picellar_sharedData.heatingOn) and (setTemperatureMin > (observedTemperature+threshold))):
		# coolerThanMin = True

	### -------------------------------------
	
	#### Regles HVAC v2 ####----------------
	
	# Checking to see if it's warmer than the high range (ie. if the A/C should turn on)
	# If the A/C is on right now, it should stay on until it goes past the threshold
	if(picellar_sharedData.coolingOn and (observedTemperature > setTemperatureMin)):
		hotterThanMax = True
	# If the A/C is not on right now, it should turn on when it hits the threshold
	if((not picellar_sharedData.coolingOn) and (setTemperatureMax < (observedTemperature-threshold))):
		hotterThanMax = True

	# Checking to see if it's colder than the low range (ie. if the heater should turn on)
	# If the heater is on right now, it should stay on until it goes past the threshold
	if(picellar_sharedData.heatingOn and (observedTemperature < setTemperatureMax)):
		coolerThanMin = True
	# If the heater is not on right now, it should turn on when it hits the threshold
	if((not picellar_sharedData.heatingOn) and (setTemperatureMin > (observedTemperature+threshold))):
		coolerThanMin = True

	### -------------------------------------
	
	if(hotterThanMax and coolerThanMin):
		print('*** Error: Outside of both ranges somehow.')
		return
	
	if((not hotterThanMax) and (not coolerThanMin)):
		print('Temperature is in range, so no compressor necessary.')
		setHeating(False)
		setCooling(False)
		if ((temp_max - temp_min) > picellar_config.fanMaxTempDiff) | (picellar_config.AUTO_FORCE_FAN_ON):
			print('Fan forced ON, or temperature difference too high - Activating fan')
			setFan(True)
		else:
			print('No temperature difference - Disabling Fan')
			setFan(False)
	
	elif(hotterThanMax):
		print('Temperature is too warm and A/C is enabled, activating A/C.')
		if(picellar_sharedData.heatingOn):
			setHeating(False)
		setCooling(True)
		setFan(True);

	elif(coolerThanMin):
		print('Temperature is too cold and heating is enabled, activating heater.')
		if(picellar_sharedData.coolingOn):
			setCooling(False)
		setHeating(True)
		setFan(True);

def initDB():
	conn = sqlite3.connect('tempdb.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	cursor = conn.cursor()
	cursor.execute("""
	CREATE TABLE IF NOT EXISTS celltemp(
		 id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
		 time TIMESTAMP,
		 t1 REAL,
		 t2 REAL,
		 t3 REAL,
		 hum1 REAL,
		 coolingOn INTEGER,
		 heatingOn INTEGER,
		 fanOn INTEGER
	)
	""")
	conn.commit()
	
def writeDB(time, t1, t2, t3, hum1, coolingOn, heatingOn, fanOn):
	conn = sqlite3.connect('tempdb.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	cursor = conn.cursor()
	cursor.execute("""INSERT INTO celltemp(time, t1, t2, t3, hum1, coolingOn, heatingOn, fanOn) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (
	time,
	t1,
	t2,
	t3,
	hum1,
	picellar_sharedData.coolingOn,
	picellar_sharedData.heatingOn,
	picellar_sharedData.fanOn
	))
	conn.commit()
	
def initGPIO():
	
	# GPIO.setwarnings(False)
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(13, GPIO.OUT)
	GPIO.setup(16, GPIO.OUT)
	GPIO.setup(20, GPIO.OUT)
	GPIO.setup(26, GPIO.OUT)
	
	# On eteind tout ! #############
	print
	print "--> Initializing control relays (all off)"
	setCooling(False)
	setHeating(False)
	setFan(False)
	
	print "--> Setting default control relays values"
	setCooling(picellar_config.DEFAULT_STATE_COOLING)
	setHeating(picellar_config.DEFAULT_STATE_HEATING)
	setFan(picellar_config.DEFAULT_STATE_FAN)
	print
	
def signal_term_handler(signal, frame):
	print 'got SIGTERM'
	sys.exit(0)

def mainThread():

	global wd_started
	
	while True:		
	
		# FORCE WATCHDOG JUST BEFORE CRITICAL FUNCTION #########
		if wd_started:
			wd_file.write('a')
			print "\r\n\r\n########### WATCHDOG KEEPALIVE SENT ###########\r\n\r\n"
		##########################
		
		print "\r\n########### STARTING SENSORS & HVAC REFRESH ###########\r\n"
		print "Current Time : " + time.ctime()
		

		
		tmp_sens = picellar_sensors.Read_temp_sensors()
		for sensor  in tmp_sens:
			print
			print "Sensor ID : " + sensor.name
			print "Sensor Data (temperature) : " + str(sensor.temperature)
			print "Sensor Data (humidity) : " + str(sensor.humidity)
			print
			
		temp_moy = (tmp_sens[0].temperature + tmp_sens[1].temperature) / 2
		temp_max = max([tmp_sens[0].temperature,tmp_sens[1].temperature,tmp_sens[2].temperature])
		temp_min = min([tmp_sens[0].temperature,tmp_sens[1].temperature,tmp_sens[2].temperature])
		
		print "Temperature Moyenne : " + str(temp_moy)
		print "Temperature Maxi : " + str(temp_max)
		print "Temperature Mini : " + str(temp_min)
		print "Temperature Difference : " + str(temp_max - temp_min)
		
		print
		
		#print "Current State mode vu par le thread : " + str(picellar_sharedData.STATE_MODE_AUTO)
		
		if (picellar_sharedData.STATE_MODE_AUTO):
			hvacControler(temp_moy, temp_max, temp_min)
		
		# setCooling(True)
		# time.sleep(5)
		# setCooling(False)
		# time.sleep(5)
		# setCooling(True)
		# time.sleep(5)
		# setCooling(False)
		# time.sleep(5)
		# setCooling(True)
		# time.sleep(5)
		# setCooling(False)
		
		
		writeDB(
		datetime.datetime.now(),
		tmp_sens[0].temperature,
		tmp_sens[1].temperature,
		tmp_sens[2].temperature,
		tmp_sens[2].humidity,
		picellar_sharedData.coolingOn,
		picellar_sharedData.heatingOn,
		picellar_sharedData.fanOn)
		

		
		print "\r\n########### SENSORS & HVAC REFRESH ENDED ###########\r\n"
		
		# FORCE WATCHDOG JUST AFTER CRITICAL FUNCTION #########
		if wd_started:
			wd_file.write('a')
			print "\r\n\r\n########### WATCHDOG KEEPALIVE SENT ###########\r\n\r\n"
		##########################
		
		# WATCHDOG #################
		if picellar_config.ENABLE_RPI_WATCHDOG:
			if not wd_started:
				while not wd_started:
					print "\r\n\r\n########### WAITING FOR WD STARTUP ###########\r\n\r\n"
					time.sleep(1)
				
				wd_file.write('a')
				print "\r\n\r\n########### WATCHDOG KEEPALIVE SENT ###########\r\n\r\n"
					
			st = time.time()
			st2 = time.time()
			while time.time() - st < picellar_config.SENSORS_REFRESH_TIME:
				if time.time() - st2 > 5:
					wd_file.write('a')
					print "\r\n\r\n########### WATCHDOG KEEPALIVE SENT ###########\r\n\r\n"
					st2 = time.time()
				time.sleep(1)
				
		############################
		else:			
			time.sleep(picellar_config.SENSORS_REFRESH_TIME)
	
	GPIO.cleanup()
	
def cleanupGPIO():
	print "16 GF OFF"
	GPIO.output(picellar_config.COOL_GPIO, 1)
	
	print "20 CHAUF OFF"
	GPIO.output(picellar_config.HEAT_GPIO, 1)
	
	print "26 Ventil OFF"
	GPIO.output(picellar_config.FAN_GPIO, 1)
	GPIO.cleanup() # cleanup all GPIO

def checkTimeAccuracy():
	try:
		print "\r\n########### CHECHING RPi CLOCK ACCURACY ###########\r\n"
	
		client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		client.settimeout(5)
		data = '\x1b' + 47 * '\0'
		client.sendto( data, ( picellar_config.NTP_SERVER, picellar_config.NTP_PORT ))
		data, address = client.recvfrom( 1024 )
		if data:
			print 'Response received from:', address
			systime = time.time()
			t = struct.unpack( '!12I', data )[10]
			t -= 2208988800L #seconds since Epoch
			print '\tNTP Time=%s' % time.ctime(t)
			print "NTP Time (Unix)    : " + str(t)
			print "System Time (Unix) : " + str(systime)
			print "Time Difference : " + str(abs(t - systime))
			
			if abs(t - systime) > 60:
				print "Clock Not Accurate - Returning False to Main Program\r\n"
				print "###################################################\r\n"
				return False
			else:
				print "Clock is (rather) Accurate - Returning True to Main Program\r\n"
				print "###################################################\r\n"
				return True
	except:
		print "NTP Request Error (DNS ? Network ? ...). Returning False\r\n"
		print "###################################################\r\n"
		return False

try:
	if __name__ == "__main__":

		# SET UNBUFFERED STDOUT ####
		sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
		############################
		
		# START WEB SERVER #########
		server = picellar_api.startThread()
		############################
		
		# TIME ACCURACY CHECK ######
		ntpCount = 0
		while(not checkTimeAccuracy()):
			if ntpCount == 5:
				break
			ntpCount = ntpCount + 1
			time.sleep(10)
		############################
		
		# SQL ######################
		initDB()
		
		# GPIO #####################
		initGPIO()

		signal.signal(signal.SIGTERM, signal_term_handler)
		
		t1 = threading.Thread(target=mainThread)
		t1.daemon = True
		t1.start()
		
		
		
		ct = time.time()
		while True:
			
			# WATCHDOG #################
			if picellar_config.ENABLE_RPI_WATCHDOG:
				
				if (wd_started == False) & (time.time() - ct > 120):
					# Set WD timer to 15sec (C app call)
					call(["./wdt_set_timer"])
					wd_file = open(picellar_config.WATCHDOG_LOCATION, 'r+', 0)
					wd_started = True
					print "\r\n\r\n########### WATCHDOG INITIALIZED - Starting countdown ... ###########\r\n\r\n"
			############################
			# WATCHDOG HACK ? ##########
			#	if (wd_started):
			#		wd_file.write('a')
					#print "\r\n\r\n########### WATCHDOG KEEPALIVE SENT ###########\r\n\r\n"
			############################		

			time.sleep(1)

except (KeyboardInterrupt, SystemExit):
	cleanupGPIO()
	server.shutdown()
	print "--- WEB Server stopped ---"
	
	# WATCHDOG STOP #################
	if picellar_config.ENABLE_RPI_WATCHDOG & wd_started:
		wd_file.write('V')
		wd_file.close()
		print "--- Watchdog Timer stopped ---"
	############################
	sys.exit(0)
