import os
import glob
import time
#import RPi.GPIO as GPIO
import Adafruit_DHT

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')
#device_file = device_folder + '/w1_slave'




class SensorData(object):
	name = None
	temperature = None
	humidity = None
	
	# def __init__(self, name, temperature, humidity):
		# self.name = name
		# self.temperature = temperature
		# self.humidity = humidity
	
class DhtSensors(object):

	name = None
	gpio = None
    
	def __init__(self, name, gpio):
		self.name = name
		self.gpio = gpio

def Read_temp_sensors():

	sensorDataList = []
	
	#### 1-WIRE (DS18B20) Temperature only ####
	for dfolder in device_folder:
		foldername = os.path.basename(dfolder)
		sensorData = SensorData()
		sensorData.name = foldername
		
		f = open(dfolder  + '/w1_slave', 'r')
		rawSensorData = f.readlines()
		f.close()
		
		#while rawSensorData[0].strip()[-3:] != 'YES':
			#time.sleep(0.2)
			#rawSensorData = read_temp_raw()
		#	test = "test"

		equals_pos = rawSensorData[1].find('t=')
		
		if equals_pos != -1:
			temp_string = rawSensorData[1][equals_pos+2:]
			temp_c = float(temp_string) / 1000.0

		sensorData.temperature = round(temp_c,1)
		sensorDataList.append(sensorData)
	
	#### DTH22 Temp + Humidity ####
	
	dhtList = []
	dhtList.append(DhtSensors("DHT22-1",19))
	
	for dhtSensor in dhtList:
		sensorData = SensorData()
		sensorData.name = dhtSensor.name
		humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, dhtSensor.gpio)
		
		sensorData.temperature = round(temperature,1)
		sensorData.humidity = round(humidity,1)
		
		sensorDataList.append(sensorData)

	return sensorDataList
	
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
try:
	if __name__ == "__main__":
		f = 1
		# GPIO.setwarnings(False)
		# GPIO.setmode(GPIO.BCM)
		# GPIO.setup(13, GPIO.OUT)
		# GPIO.setup(16, GPIO.OUT)
		# GPIO.setup(20, GPIO.OUT)
		# GPIO.setup(26, GPIO.OUT)
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
			
		
		while True:
			print "Start Sensor Read"
			for sensor  in Read_temp_sensors():
				print "Sensor ID : " + sensor.name
				print "Sensor Data (temperature) : " + str(sensor.temperature)
				print "Sensor Data (humidity) : " + str(sensor.humidity)
				print
			
			time.sleep(1)
			
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
    a = 1
	# GPIO.cleanup() # cleanup all GPIO
				
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
