#!/usr/bin/kivy
# -*- coding: utf-8 -*-
'''
Touch Tracer Line Drawing Demonstration
=======================================

This demonstrates tracking each touch registered to a device. You should
see a basic background image. When you press and hold the mouse, you
should see cross-hairs with the coordinates written next to them. As
you drag, it leaves a trail. Additional information, like pressure,
will be shown if they are in your device's touch.profile.

This program specifies an icon, the file icon.png, in its App subclass.
It also uses the particle.png file as the source for drawing the trails which
are white on transparent. The file Picellar.kv describes the application.

The file android.txt is used to package the application for use with the
Kivy Launcher Android application. For Android devices, you can
copy/paste this directory into /sdcard/kivy/Picellar on your Android device.

'''
__version__ = '1.0'

import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Point, GraphicException
from random import random
from math import sqrt
from kivy.clock import Clock, mainthread
from kivy.properties import ObjectProperty, StringProperty

import GetTemp
import Adafruit_DHT
import threading
import time 
import sys



#Controle des threads
appStart = True


class Picellar(FloatLayout):

	txt = ObjectProperty(None)
	deg = ObjectProperty(None)
	hum = ObjectProperty(None)
	tempTargetW = ObjectProperty(None)
	humTargetW = ObjectProperty(None)
	humTarget = 60
	tempTarget = 12
	globalSd = None
	

	def _workerThread(self):
		i = 0
		while appStart:
			
			# self.deg.text = "JFDKLJLKFD"
			
			if self.globalSd is not None:
			
				if self.tempTarget - 2 > self.globalSd[4].temperature:
					self.deg.color = [0, 0, 1, 1]
					print "too low"
				elif self.tempTarget + 2 < self.globalSd[4].temperature:
					self.deg.color = [1, 0, 0, 1]
					print "too high"
				else:
					self.deg.color = [1, 1, 1, 1]
					print "temp ok"
					
				print "OK"
				print "TempTarget " + str(self.tempTarget)

			#print "OK"
			time.sleep(0.5)
	
	
	#@mainthread
	def update_temp(self,sd):
		self.txt.text = ""
		myText = ""
		self.globalSd = sd
		i = 0
		
		for sensorData in sd:
			# print sensorData.name
			# print sensorData.temperature
			# print sensorData.humidity
			
			myText += "Capteur : " + sensorData.name
			myText += "\n"
			myText += "Température : [b]" + str(sensorData.temperature) + " °C[/b]"
			myText += "\n"
			myText += "Humidité : [b]" + str(sensorData.humidity) + " %[/b]"
			
			if i+1 < len(sd):
				myText += "\n\n"
			
			i = i+1
				
			if (sensorData.name == "DHT22-1"):
				self.deg.text = "[i][b]" + str(sensorData.temperature) + " °C[/b][/i]"
				self.hum.text = "[i][b]" + str(sensorData.humidity) + " %[/b][/i]"
				
			
		self.txt.text = myText
		print "Updated !"
		
	def GetSensorThread(self, dt):
		t = threading.Thread(target=self._updateSensors)
		t.start()
		
	def _updateSensors(self):
		sd = GetTemp.Read_temp_sensors()
		print "Sensor Updated !"
		self.update_temp(sd)
		
	def Init(self):
		self.SetNewTargets(self.tempTarget,self.humTarget)
		t = threading.Thread(target=self._workerThread)
		t.start()
		Clock.schedule_interval(self.GetSensorThread, 5)
		
		
	def ChangeTargets(self,target):
		print "Target Change Request : " + str(target)
		
		if target == 1:
			self.tempTarget = self.tempTarget - 1
		if target == 2:
			self.tempTarget = self.tempTarget + 1
		if target == 3:
			self.humTarget = self.humTarget - 1
		if target == 4:
			self.humTarget = self.humTarget + 1
			
			
		self.SetNewTargets(self.tempTarget,self.humTarget)
		
	def SetNewTargets(self, temp, hum):
		self.tempTarget = temp
		self.humTarget = hum
		self.tempTargetW.text = str(temp) + " °C"
		self.humTargetW.text = str(hum) + " %"
		
		
class PicellarApp(App):
    title = 'Picellar'
    icon = 'icon.png'

    def build(self):
		app = Picellar()
		app.Init()
		return app

    def on_pause(self):
        return True

try:
	if __name__ == '__main__':
		PicellarApp().run()

except:		
#except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
	print "Unexpected error:", sys.exc_info()[0]
	appStart = False