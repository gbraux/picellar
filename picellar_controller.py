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
import picellar_api
import picellar_config
import picellar_sensors
import picellar_sharedData

COOL_GPIO = 16
HEAT_GPIO = 20
FAN_GPIO = 26
RECOVERY_TIME = 10
LAST_COOLER_TOOGLE = 0
TEMP_THRESHOLD = 1
TEMP_THRESHOLD_MAX = 2
COMPRESSOR_TOOGLE_TIME = 1800
COMPRESSOR_RECOVERY_TIME = 600

#COMPRESSOR_TOOGLE_TIME = 30
#COMPRESSOR_RECOVERY_TIME = 30

COMPRESSOR_LAST_START_TIME = 0
COMPRESSOR_LAST_STOP_TIME = 0
recoveryOn = 0
lastCompressorEnableTime = 0

def setMode(isAuto):
	picellar_sharedData.STATE_MODE_AUTO = isAuto
	print "Changement de mode. IsAuto = " + str(picellar_sharedData.STATE_MODE_AUTO)

def getMode():
	return picellar_sharedData.STATE_MODE_AUTO

def setHeating(toogle):
	if (toogle):
		print "20 Chauffage ON"
		GPIO.output(20, 0)
		picellar_sharedData.heatingOn = True
	else:
		print "20 Chauffage OFF"
		GPIO.output(20, 1)
		picellar_sharedData.heatingOn = False

def getHeating():
	return picellar_sharedData.heatingOn
		
def setFan(toogle):
	
	if (toogle):
		print "26 Fan ON"
		GPIO.output(26, 0)
		picellar_sharedData.fanOn = True
	else:
		print "26 Fan OFF"
		GPIO.output(26, 1)
		picellar_sharedData.fanOn = False
		
def getFan():
	return picellar_sharedData.fanOn
		
def setCooling(toogle):
	
	global COMPRESSOR_TOOGLE_TIME
	global COMPRESSOR_RECOVERY_TIME
	global COMPRESSOR_LAST_START_TIME
	global COMPRESSOR_LAST_STOP_TIME
	global recoveryOn	
	
	
	
	if (toogle):
	
		
		if ((int(time.time()) > (COMPRESSOR_LAST_START_TIME+COMPRESSOR_TOOGLE_TIME)) & (COMPRESSOR_LAST_START_TIME != 0) & (picellar_sharedData.coolingOn == True)):
			print "Compresseur en activité depuis trop longtemps ... Arret pour recovery"
			print "16 GF OFF"
			GPIO.output(16, 1)

			COMPRESSOR_LAST_STOP_TIME = int(time.time())
			picellar_sharedData.coolingOn = False
			return
		elif (picellar_sharedData.coolingOn == True):
			print "Temp de run restant avant arret de compresseur pour recovery : " + datetime.datetime.fromtimestamp((COMPRESSOR_LAST_START_TIME+COMPRESSOR_TOOGLE_TIME) - int(time.time())).strftime('%H:%M:%S')
	
		
		if ((int(time.time()) < (COMPRESSOR_LAST_STOP_TIME+COMPRESSOR_RECOVERY_TIME)) & (COMPRESSOR_LAST_STOP_TIME != 0)):
			print "Compresseur en recovery ... Démarrage impossible"
			print "Temps de recovery restant : " + datetime.datetime.fromtimestamp((COMPRESSOR_LAST_STOP_TIME+COMPRESSOR_RECOVERY_TIME) - int(time.time())).strftime('%H:%M:%S')
			print "16 GF OFF"
			GPIO.output(16, 1)
			picellar_sharedData.coolingOn = False
			return

			
		print "16 GF ON"
		GPIO.output(16, 0)
		
		if picellar_sharedData.coolingOn == False:
			COMPRESSOR_LAST_START_TIME = int(time.time())
		
		picellar_sharedData.coolingOn = True
		
	else:
		print "16 GF OFF"
		GPIO.output(16, 1)
		
		if picellar_sharedData.coolingOn == True:
			COMPRESSOR_LAST_STOP_TIME = int(time.time())
		
		picellar_sharedData.coolingOn = False

def getCooling():
	return picellar_sharedData.coolingOn
	
def hvacControler(current_temp, temp_max, temp_min):

	global COMPRESSOR_STICK_TIME
	global lastCompressorEnableTime
	
	# This function is called if the compressor is in heat, cool or auto mode.
	# First check the current temperature, set temperature, and threshold.
	
	# If the compressor is in the "stuck" period, just return.
	# currentTime = int(time.time());
	# if(currentTime < (lastCompressorEnableTime+COMPRESSOR_STICK_TIME)):
		# print('Compressor currently stuck, so no change.');
		# return;
	
	observedTemperature = current_temp
	
	setTemperatureMax = picellar_config.setTemperatureMax
	setTemperatureMin = picellar_config.setTemperatureMin
	threshold = picellar_config.threshold
	
	if(threshold < 0.5):
		threshold = 0.5
		print('*** Warning: Threshold too low. Setting to 0.5.')
	
	if((setTemperatureMax <= setTemperatureMin) or ((setTemperatureMax-setTemperatureMin) < (threshold*2))):
		print('*** Error: Overlap between set minimum and maximum temperatures.')
		return
	
	print('Current temperature: '+str(observedTemperature)+' C')
	print('Set minimum temperature: '+str(setTemperatureMin)+' C')
	print('Set maximum temperature: '+str(setTemperatureMax)+' C')
	print('')
	
	# The A/C (and fan) should be enabled if the observed temperature is warmer than
	# the set temperature, plus the threshold
	
	hotterThanMax = False
	coolerThanMin = False
	
	# Checking to see if it's warmer than the high range (ie. if the A/C should turn on)
	# If the A/C is on right now, it should stay on until it goes past the threshold
	if(picellar_sharedData.coolingOn and (setTemperatureMax < (observedTemperature+threshold))):
		hotterThanMax = True
	# If the A/C is not on right now, it should turn on when it hits the threshold
	if((not picellar_sharedData.coolingOn) and (setTemperatureMax < (observedTemperature-threshold))):
		hotterThanMax = True

	# Checking to see if it's colder than the low range (ie. if the heater should turn on)
	# If the heater is on right now, it should stay on until it goes past the threshold
	if(picellar_sharedData.heatingOn and (setTemperatureMin > (observedTemperature-threshold))):
		coolerThanMin = True
	# If the heater is not on right now, it should turn on when it hits the threshold
	if((not picellar_sharedData.heatingOn) and (setTemperatureMin > (observedTemperature+threshold))):
		coolerThanMin = True

	
	if(hotterThanMax and coolerThanMin):
		print('*** Error: Outside of both ranges somehow.')
		return
	
	if((not hotterThanMax) and (not coolerThanMin)):
		print('Temperature is in range, so no compressor necessary.')
		setHeating(False)
		setCooling(False)
		if (temp_max - temp_min) > 1:
			print('Temperature difference too high - Activating fan')
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
		#setFan(True)
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

	while True:		
	
		print "----------------------------------"
		tmp_sens = picellar_sensors.Read_temp_sensors()
		for sensor  in tmp_sens:
			print
			print "Sensor ID : " + sensor.name
			print "Sensor Data (temperature) : " + str(sensor.temperature)
			print "Sensor Data (humidity) : " + str(sensor.humidity)
			print
			
		temp_moy = (tmp_sens[0].temperature + tmp_sens[1].temperature + tmp_sens[2].temperature) / 3
		temp_max = max([tmp_sens[0].temperature,tmp_sens[1].temperature,tmp_sens[2].temperature])
		temp_min = min([tmp_sens[0].temperature,tmp_sens[1].temperature,tmp_sens[2].temperature])
		
		print "Temperature Moyenne : " + str(temp_moy)
		print "Temperature Maxi : " + str(temp_max)
		print "Temperature Mini : " + str(temp_min)
		print "Temperature Diff : " + str(temp_max - temp_min)
		
		print
		
		print "State mode vu par le thread : " + str(picellar_sharedData.STATE_MODE_AUTO)
		
		if (picellar_sharedData.STATE_MODE_AUTO):
			hvacControler(temp_moy, temp_max, temp_min)
		
		
		writeDB(
		datetime.datetime.now(),
		tmp_sens[0].temperature,
		tmp_sens[1].temperature,
		tmp_sens[2].temperature,
		tmp_sens[2].humidity,
		picellar_sharedData.coolingOn,
		picellar_sharedData.heatingOn,
		picellar_sharedData.fanOn)
		
		# cursor.execute("""INSERT INTO celltemp(time, t1, t2, t3, hum1, picellar_sharedData.coolingOn, picellar_sharedData.heatingOn, picellar_sharedData.fanOn) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (
		# datetime.datetime.now(),
		# tmp_sens[0].temperature,
		# tmp_sens[1].temperature,
		# tmp_sens[2].temperature,
		# tmp_sens[2].humidity,
		# picellar_sharedData.coolingOn,
		# picellar_sharedData.heatingOn,
		# picellar_sharedData.fanOn
		# ))
		# conn.commit()
		
		print
		
		time.sleep(60)
	
	GPIO.cleanup()
	
def cleanupGPIO():
	print "16 GF OFF"
	GPIO.output(16, 1)
	
	print "20 CHAUF OFF"
	GPIO.output(20, 1)
	
	print "26 Ventil OFF"
	GPIO.output(26, 1)
	GPIO.cleanup() # cleanup all GPIO

try:
	if __name__ == "__main__":
		
		# SQL ######################
		initDB()
		# GPIO #####################
		initGPIO()
		
		signal.signal(signal.SIGTERM, signal_term_handler)
		#mainThread()
		
		t1 = threading.Thread(target=mainThread)
		t1.daemon = True
		t1.start()
		
		server = picellar_api.startThread()
		
		while True:
			time.sleep(1)

except (KeyboardInterrupt, SystemExit):
	cleanupGPIO()
	# server.shutdown()
	print "--- WEB Server stopped ---"
	sys.exit(0)