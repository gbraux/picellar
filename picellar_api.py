#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SimpleHTTPServer
import SocketServer
import re
import sqlite3
import datetime
import urlparse
import json
import threading
import time
import sys
import signal
import logging
import cgi
import picellar_controller
import picellar_config
import BaseHTTPServer



def dbRowToDict(date, t1, t2, t3, hum1, coolingOn, heatingOn, fanOn):
	dataDict = {"date" : {"label" : picellar_config.lDate, "value" : str(date)},
	"t1" : {"label" : picellar_config.lT1, "value" : t1},
	"t2" : {"label" : picellar_config.lT2, "value" : t2},
	"t3" : {"label" : picellar_config.lT3, "value" : t3},
	"hum1" : {"label" : picellar_config.lHum1, "value" : hum1},
	"coolingOn" : {"label" : picellar_config.lCoolingOn, "value" : coolingOn},
	"heatingOn" : {"label" : picellar_config.lHeatingOn, "value" : heatingOn},
	"fanOn" : {"label" : picellar_config.lFanOn, "value" : fanOn}
	}
	
	return dataDict
	
def getModeJson():
	dataDict = {"isauto" : {"label" : picellar_config.lIsAuto, "value" : picellar_controller.getMode()},
	"coolingOn" : {"label" : picellar_config.lCoolingOn, "value" : picellar_controller.getCooling()},
	"heatingOn" : {"label" : picellar_config.lHeatingOn, "value" : picellar_controller.getHeating()},
	"fanOn" : {"label" : picellar_config.lFanOn, "value" : picellar_controller.getFan()}
	}
	
	if picellar_config.HTTP_STDOUT_LOGS:
		print dataDict
	
	return json.dumps(dataDict)

def getDataJson(isGoogleChart, startDate, endDate):
	
	conn = sqlite3.connect('tempdb.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	cursor = conn.cursor()

	# Commande buggé ?
	#sqlCommand = "SELECT time, AVG(t1), AVG(t2),  AVG(t3), AVG(hum1), AVG(coolingOn), AVG(heatingOn), AVG(fanOn) FROM celltemp WHERE time > datetime('" + startDate.strftime('%Y-%m-%d %H:%M:%S') + "') AND time < datetime('" + endDate.strftime('%Y-%m-%d %H:%M:%S') + "') GROUP BY (Id - 1) / (((SELECT Count(*) FROM celltemp) + 4) / 300)"
	
	sqlCommand = "SELECT time, AVG(t1), AVG(t2),  AVG(t3), AVG(hum1), AVG(coolingOn), AVG(heatingOn), AVG(fanOn) FROM celltemp WHERE time > datetime('" + startDate.strftime('%Y-%m-%d %H:%M:%S') + "') AND time < datetime('" + endDate.strftime('%Y-%m-%d %H:%M:%S') + "') GROUP BY (Id - 1) / (((SELECT Count(*) FROM celltemp WHERE time > datetime('" + startDate.strftime('%Y-%m-%d %H:%M:%S') + "') AND time < datetime('" + endDate.strftime('%Y-%m-%d %H:%M:%S') + "')) + 4) / 300)"
	if picellar_config.HTTP_STDOUT_LOGS:
		print sqlCommand
	
	cursor.execute(sqlCommand)
	
	if isGoogleChart:
		data = "["
		data += "[{\"type\": \"datetime\", \"label\": \"" + picellar_config.lDate + "\"},\"" + picellar_config.lT1 + "\", \"" + picellar_config.lT3 + "\", \"" + picellar_config.lT2 + "\", \"" + picellar_config.lHum1 + "\", \"" + picellar_config.lCoolingOn + "\", \"" + picellar_config.lHeatingOn + "\", \"" + picellar_config.lFanOn + "\"]"
	#else:
	#	data += "[\"time\", \"t1\", \"t2\", \"t3\", \"hum1\", \"coolingOn\", \"heatingOn\", \"fanOn\"]"
	
		for row in cursor:
			data += ",["
		
	#	if isGoogleChart:
			# Javascript Month Hack for GChart (Javascript Month is 0-11, not 1-12)
			jsMonth = row[0].month - 1
			badDate = row[0].strftime('"Date(%Y,month,%d,%H,%M,%S)"')
			goodDate = badDate.replace("month", str(jsMonth))
	
			#data += row[0].strftime('"Date(%Y,%m,%d,%H,%M,%S)"') + "," + str(row[1]) + "," + str(row[3]) + "," + str(row[2]) + "," + str(row[4]) + "," + str(row[5]) + "," + str(row[6]) + "," + str(row[7])
			data += goodDate + "," + str(row[1]) + "," + str(row[3]) + "," + str(row[2]) + "," + str(row[4]) + "," + str(row[5]) + "," + str(row[6]) + "," + str(row[7])

	#	else:
	#		data += str(row[0]) + "," + str(row[1]) + "," + str(row[2]) + "," + str(row[3]) + "," + str(row[4]) + "," + str(row[5]) + "," + str(row[6]) + "," + str(row[7])
		
			data += "]"
		data += "]"
		
	else:
		dictArray = []
		
		for row in cursor:
			dictArray.append(dbRowToDict(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

		data = json.dumps(dictArray)
		
		
		
	
	
	return data

def getLastDataJson(isGoogleChart):
	conn = sqlite3.connect('tempdb.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
	cursor = conn.cursor()
	sqlCommand = "SELECT time, t1, t2, t3, hum1, coolingOn, heatingOn, fanOn FROM celltemp ORDER BY time DESC LIMIT 1"

	cursor.execute(sqlCommand)
	row = cursor.fetchone()
	

	if (isGoogleChart):
		data = "["
		data += "[\"" + picellar_config.lDate + "\",\"" + picellar_config.lT1 + "\", \"" + picellar_config.lT3 + "\", \"" + picellar_config.lT2 + "\", \"" + picellar_config.lHum1 + "\", \"" + picellar_config.lCoolingOn + "\", \"" + picellar_config.lHeatingOn + "\", \"" + picellar_config.lFanOn + "\"]"
		
		#for row in cursor:
		data += ",["
		data +=  "\"" + str(row[0])+ "\"" + "," + str(row[1]) + "," + str(row[3]) + "," + str(row[2]) + "," + str(row[4]) + "," + str(row[5]) + "," + str(row[6]) + "," + str(row[7])
		
		data += "]"
		data += "]"
	
	else:
		data = json.dumps(dbRowToDict(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
	
	return data
	
def startThread():
	
	
	server = ThreadedHTTPServer(('0.0.0.0', 8080), MyRequestHandler)
	print 'Starting server, use <Ctrl-C> to stop'
	#server.serve_forever()
	
	# --- CAN BE DELETED AFTER SUCESSFULL THREADING TEST ---
	# Handler = MyRequestHandler
	# SocketServer.TCPServer.allow_reuse_address = True
	# server = SocketServer.TCPServer(('0.0.0.0', 8080), Handler)
	
	#server.serve_forever() --> VRAIEMENT COMMENTE ...
	
	thread = threading.Thread(target = server.serve_forever)
	thread.deamon = True
	thread.start()
	# -------------------------------------------------------
	
	print "--- WEB Server started (8080) ---"
	return server


	
class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""
	
class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
	
		####### !!!!!! FOR GOOGLE CHART HACK !!!!!! #######
	
		if None != re.search('/picellar/api/v1/getdata/gchart/last', self.path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			self.wfile.write(getLastDataJson(True))
		
		elif None != re.search('/picellar/api/v1/getdata/gchart/range', self.path):

			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()

			query_components = urlparse.parse_qs(urlparse.urlparse(self.path).query)
			
			startDate = datetime.datetime.fromtimestamp(float(query_components["startDate"][0]))
			endDate = datetime.datetime.fromtimestamp(float(query_components["endDate"][0]))
			data = getDataJson(True,startDate,endDate)
			self.wfile.write(data)

		elif None != re.search('/picellar/api/v1/getdata/gchart/', self.path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			
			data = getDataJson(True,datetime.datetime.now() - datetime.timedelta(days=1),datetime.datetime.now())
			self.wfile.write(data)
		
		###### STANDARD JSON ######
		elif None != re.search('/picellar/api/v1/getdata/last', self.path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			self.wfile.write(getLastDataJson(False))
			
		elif None != re.search('/picellar/api/v1/getdata/range', self.path):

			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()

			query_components = urlparse.parse_qs(urlparse.urlparse(self.path).query)
			
			startDate = datetime.datetime.fromtimestamp(float(query_components["startDate"][0]))
			endDate = datetime.datetime.fromtimestamp(float(query_components["endDate"][0]))
			data = getDataJson(False,startDate,endDate)
			self.wfile.write(data)
			
		elif None != re.search('/picellar/api/v1/getmode/', self.path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			self.wfile.write(getModeJson())

		else:
			return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

	def do_POST(self):
	
		if None != re.search('/picellar/api/v1/setmode/', self.path):
			self.send_response(200)
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			
			content_len = int(self.headers.getheader('content-length', 0))
			post_body = self.rfile.read(content_len)
			
			modeDatas = json.loads(post_body)
			if (modeDatas["isauto"]):
				picellar_controller.setMode(True)
			else:
				picellar_controller.setMode(False)
				#picellar_controller.STATE_MODE_AUTO = False;
				
				picellar_controller.setHeating(modeDatas["heatingOn"])
				picellar_controller.setCooling(modeDatas["coolingOn"])
				picellar_controller.setFan(modeDatas["fanOn"])
		
	def log_message(self, format, *args):
		if picellar_config.HTTP_STDOUT_LOGS:
			sys.stdout.write("%s --> [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))
