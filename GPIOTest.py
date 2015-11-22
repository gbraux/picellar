# -*- coding: utf-8 -*-

import os
import glob
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import GetTemp
import sqlite3
import datetime

COOL_GPIO = 16
HEAT_GPIO = 20
FAN_GPIO = 26
RECOVERY_TIME = 10
LAST_COOLER_TOOGLE = 0
TEMP_THRESHOLD = 1
TEMP_THRESHOLD_MAX = 2
CURRENT_STATE = 0
COMPRESSOR_TOOGLE_TIME = 1800
COMPRESSOR_RECOVERY_TIME = 600

#COMPRESSOR_TOOGLE_TIME = 30
#COMPRESSOR_RECOVERY_TIME = 30

COMPRESSOR_LAST_START_TIME = 0
COMPRESSOR_LAST_STOP_TIME = 0
recoveryOn = 0
heatingOn = 0
coolingOn = 0
fanOn = 0
lastCompressorEnableTime = 0



def setHeating(toogle):
	
	global heatingOn	
	
	if (toogle):
		print "20 Chauffage ON"
		GPIO.output(20, 0)
		heatingOn = True
	else:
		print "20 Chauffage OFF"
		GPIO.output(20, 1)
		heatingOn = False

def setFan(toogle):
	
	global fanOn	
	
	if (toogle):
		print "26 Fan ON"
		GPIO.output(26, 0)
		fanOn = True
	else:
		print "26 Fan OFF"
		GPIO.output(26, 1)
		fanOn = False
		
def setCooling(toogle):
	
	global COMPRESSOR_TOOGLE_TIME
	global COMPRESSOR_RECOVERY_TIME
	global COMPRESSOR_LAST_START_TIME
	global COMPRESSOR_LAST_STOP_TIME
	global coolingOn	
	global recoveryOn	
	
	
	
	if (toogle):
	
		
		if ((int(time.time()) > (COMPRESSOR_LAST_START_TIME+COMPRESSOR_TOOGLE_TIME)) & (COMPRESSOR_LAST_START_TIME != 0) & (coolingOn == True)):
			print "Compresseur en activité depuis trop longtemps ... Arret pour recovery"
			print "16 GF OFF"
			GPIO.output(16, 1)

			COMPRESSOR_LAST_STOP_TIME = int(time.time())
			
			coolingOn = False
			return
		elif (coolingOn == True):
			print "Temp de run restant avant arret de compresseur pour recovery : " + datetime.datetime.fromtimestamp((COMPRESSOR_LAST_START_TIME+COMPRESSOR_TOOGLE_TIME) - int(time.time())).strftime('%H:%M:%S')
	
		
		if ((int(time.time()) < (COMPRESSOR_LAST_STOP_TIME+COMPRESSOR_RECOVERY_TIME)) & (COMPRESSOR_LAST_STOP_TIME != 0)):
			print "Compresseur en recovery ... Démarrage impossible"
			print "Temps de recovery restant : " + datetime.datetime.fromtimestamp((COMPRESSOR_LAST_STOP_TIME+COMPRESSOR_RECOVERY_TIME) - int(time.time())).strftime('%H:%M:%S')
			print "16 GF OFF"
			GPIO.output(16, 1)
			coolingOn = False
			return

			
		print "16 GF ON"
		GPIO.output(16, 0)
		
		if coolingOn == False:
			COMPRESSOR_LAST_START_TIME = int(time.time())
		
		coolingOn = True
		
	else:
		print "16 GF OFF"
		GPIO.output(16, 1)
		
		if coolingOn == True:
			COMPRESSOR_LAST_STOP_TIME = int(time.time())
		
		coolingOn = False

def hvacControler(current_temp):

	global COMPRESSOR_STICK_TIME
	global heatingOn
	global coolingOn	
	global lastCompressorEnableTime
	
	setFan(True)
	
	# This function is called if the compressor is in heat, cool or auto mode.
	# First check the current temperature, set temperature, and threshold.
	
	# If the compressor is in the "stuck" period, just return.
	# currentTime = int(time.time());
	# if(currentTime < (lastCompressorEnableTime+COMPRESSOR_STICK_TIME)):
		# print('Compressor currently stuck, so no change.');
		# return;
	
	observedTemperature = current_temp
	setTemperatureMax = 13
	setTemperatureMin = 11
	threshold = 0.5
	
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
	if(coolingOn and (setTemperatureMax < (observedTemperature+threshold))):
		hotterThanMax = True
	# If the A/C is not on right now, it should turn on when it hits the threshold
	if((not coolingOn) and (setTemperatureMax < (observedTemperature-threshold))):
		hotterThanMax = True

	# Checking to see if it's colder than the low range (ie. if the heater should turn on)
	# If the heater is on right now, it should stay on until it goes past the threshold
	if(heatingOn and (setTemperatureMin > (observedTemperature-threshold))):
		coolerThanMin = True
	# If the heater is not on right now, it should turn on when it hits the threshold
	if((not heatingOn) and (setTemperatureMin > (observedTemperature+threshold))):
		coolerThanMin = True

	
	if(hotterThanMax and coolerThanMin):
		print('*** Error: Outside of both ranges somehow.')
		return
	
	if((not hotterThanMax) and (not coolerThanMin)):
		print('Temperature is in range, so no compressor necessary.')
		setHeating(False)
		setCooling(False)
		# if(settings['fan_mode']=='auto')
			# setFan(False);
	
	elif(hotterThanMax):
		print('Temperature is too warm and A/C is enabled, activating A/C.')
		#setFan(True)
		if(heatingOn):
			setHeating(False)
		setCooling(True)

	elif(coolerThanMin):
		print('Temperature is too cold and heating is enabled, activating heater.')
		#setFan(True)
		if(coolingOn):
			setCooling(False)
		setHeating(True)

		
try:
	if __name__ == "__main__":
		
		temp_target = 9;
		
		# SQL ######################
		
		conn = sqlite3.connect('tempdb.db')
		cursor = conn.cursor()
		cursor.execute("""
		CREATE TABLE IF NOT EXISTS celltemp(
			 id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
			 time INTEGER,
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
	
		# GPIO.setwarnings(False)
		GPIO.cleanup()
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(13, GPIO.OUT)
		GPIO.setup(16, GPIO.OUT)
		GPIO.setup(20, GPIO.OUT)
		GPIO.setup(26, GPIO.OUT)
		
		# On eteind tout ! #############
		print "16 GF OFF"
		GPIO.output(16, 1)
		
		time.sleep(0.5)
		
		print "20 CHAUF OFF"
		GPIO.output(20, 1)
		
		time.sleep(0.5)
		
		print "26 Ventil OFF"
		GPIO.output(26, 1)
		
		time.sleep(0.5)
		#################################
		
		# On allume ventilation
		# print "26 VENTILATION ON"
		# GPIO.output(26, 0)
		
		# time.sleep(0.5)
		
		# print "20 CHAUFFAGE ON"
		# GPIO.output(20, 0)
			
		# time.sleep(0.5)
		
		###############################
		
		while True:
			print "----------------------------------"
			tmp_sens = GetTemp.Read_temp_sensors()
			for sensor  in tmp_sens:
				print
				print "Sensor ID : " + sensor.name
				print "Sensor Data (temperature) : " + str(sensor.temperature)
				print "Sensor Data (humidity) : " + str(sensor.humidity)
				print
				

			
			
			temp_moy = (tmp_sens[1].temperature + tmp_sens[2].temperature) / 2
			
			# if temp_moy > temp_target + THRESHOLD:
			
			print "Temperature Moyenne : " + str(temp_moy)
			
			print
			
			hvacControler(temp_moy)
			
			
			cursor.execute("""INSERT INTO celltemp(time, t1, t2, t3, hum1, coolingOn, heatingOn, fanOn) VALUES(CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?)""", (
			tmp_sens[0].temperature,
			tmp_sens[1].temperature,
			tmp_sens[2].temperature,
			tmp_sens[2].humidity,
			coolingOn,
			heatingOn,
			fanOn
			))
			conn.commit()
			
			# A REECRIRE POUR EVITER LE BAGOTTEMENT
			
			# if (CURRENT_STATE == 0):
				# if (temp_moy > temp_target + TEMP_THRESHOLD):
					# print "Faut refroidir !"
					# CURRENT_STATE = 1
					# setCooler(1)
					
				# if (temp_moy < temp_target + TEMP_THRESHOLD):
					# print "Faut rechauffer !"
					# CURRENT_STATE = 2
					# setHeater(1)
				
			# if (CURRENT_STATE == 1):
				# if (temp_moy > temp_target + TEMP_THRESHOLD):
					# print "Faut refroidir !"
					# CURRENT_STATE = 1
					# setCooler(1)
					
				# if (temp_moy < temp_target + TEMP_THRESHOLD):
					# print "Faut rechauffer !"
					# CURRENT_STATE = 2
					# setHeater(1)
			
			
			
			# if temp_moy > temp_target + 1:
				# print "20 CHAUFFAGE OFF"
				# GPIO.output(20, 1)
				# print "16 GF ON"
				# GPIO.output(16, 0)
				# print "26 VENTILATION ON"
				# GPIO.output(26, 0)
				
			# elif temp_moy < temp_target -1:
				# print "20 CHAUFFAGE ON"
				# GPIO.output(20, 0)
				# print "16 GF OFF"
				# GPIO.output(16, 1)
				# print "26 VENTILATION ON"
				# GPIO.output(26, 0)
			# else:
				# print "20 CHAUFFAGE OFF"
				# GPIO.output(20, 1)
				# print "16 GF OFF"
				# GPIO.output(16, 1)
				# print "26 VENTILATION OFF"
				# GPIO.output(26, 1)
			
			print
			
			time.sleep(60)
		
		# while True:

			
			# print "16 GF OFF"
			# GPIO.output(16, 1)
			
			# time.sleep(2)
			
			# print "20 CHAUF OFF"
			# GPIO.output(20, 1)
			
			# time.sleep(2)
			
			# print "26 Ventil OFF"
			# GPIO.output(26, 1)
			
			# time.sleep(2)
			
			

			
			# print "16  GF ON"
			# GPIO.output(16, 0)
			
			# time.sleep(2)
			
			# print "20 CHAUF ON"
			# GPIO.output(20, 0)
			
			# time.sleep(2)
			
			# print "26 VENTI ON"
			# GPIO.output(26, 0)
			
			# time.sleep(2)
		
		GPIO.cleanup()
		
		# GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		# # GPIO.cleanup();
		# # GPIO.setmode(GPIO.BCM)
		# # GPIO.setup(20, GPIO.OUT)
		
		# start = False;
		# GPIO.setup(20, start)
		# tickCount = 0
		# startTime = time.time()
		
		# p = GPIO.PWM(20, 50)  # channel=12 frequency=50Hz
		# p.start(100)
		
		# while True:
			# a = 1
			# # for dc in range(0, 101, 5):
				# # p.ChangeDutyCycle(dc)
				# # time.sleep(0.1)
			# # for dc in range(100, -1, -5):
				# # p.ChangeDutyCycle(dc)
				# # time.sleep(0.1)
			# # print GPIO.input(26)
			# # GPIO.output(20,True)
			# # print "True"
			# # time.sleep(0.3)
			# # GPIO.output(20,False)
			# # print "False"
			# # time.sleep(0.3)
			
		
		# while True:
			# print "Start Sensor Read"
			# for sensor  in Read_temp_sensors():
				# print "Sensor ID : " + sensor.name
				# print "Sensor Data (temperature) : " + str(sensor.temperature)
				# print "Sensor Data (humidity) : " + str(sensor.humidity)
				# print
			
			# time.sleep(1)
			
			# # start = not start
			# # print start
			# # if start:
				# # GPIO.setup(20, start)
			# # else:
				# # GPIO.setup(20, start)
			

			# if GPIO.input(26) == False:
				# tickCount = tickCount + 1
			
			# delay = time.time() - startTime
			# # print time.time()
			# if delay > 1:
				# rpm = tickCount
				# print str(rpm) + "RPM"
				# print "Delay : " + str(delay)
				# tickCount = 0
				# startTime = time.time()
			# # time.sleep(1)
				

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
	print "16 GF OFF"
	GPIO.output(16, 1)
	
	time.sleep(0.5)
	
	print "20 CHAUF OFF"
	GPIO.output(20, 1)
	
	time.sleep(0.5)
	
	print "26 Ventil OFF"
	GPIO.output(26, 1)
	
	time.sleep(0.5)
	
	GPIO.cleanup() # cleanup all GPIO

	
				
# base_dir = '/sys/bus/w1/devices/'
# device_folder = glob.glob(base_dir + '28*')[0]
# device_file = device_folder + '/w1_slave'

# def read_temp_raw():

# for SensorFolder in

	# f = open(device_file, 'r')
	# lines = f.readlines()
	# f.close()
	# return lines
	
# def read_temp(sensor_num):
	
	# lines = read_temp_raw()
	# while lines[0].strip()[-3:] != 'YES':
		# time.sleep(0.2)
		# lines = read_temp_raw()
	# equals_pos = lines[1].find('t=')
	# if equals_pos != -1:
		# temp_string = lines[1][equals_pos+2:]
		# temp_c = float(temp_string) / 1000.0
		# temp_f = temp_c * 9.0 / 5.0 + 32.0
		# return round(temp_c,1)

# if __name__ == "__main__":
	# while True:
		# print(read_temp())
		# time.sleep(1)
