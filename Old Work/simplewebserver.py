from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import cgi
import sqlite3
import json
 
class LocalData(object):
	records = {}
 
class HTTPRequestHandler(BaseHTTPRequestHandler):
 
	def do_POST(self):
		if None != re.search('/api/v1/addrecord/*', self.path):
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'application/json':
				length = int(self.headers.getheader('content-length'))
				data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
				recordID = self.path.split('/')[-1]
				LocalData.records[recordID] = data
				print "record %s is added successfully" % recordID
			else:
				data = {}
				self.send_response(200)
				self.end_headers()
		else:
			self.send_response(403)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()

		return

	def do_GET(self):
		if None != re.search('/api/v1/getrecord/*', self.path):
			recordID = self.path.split('/')[-1]
			# if LocalData.records.has_key(recordID):
			if True:
				self.send_response(200)
				self.send_header('Content-Type', 'application/json')
				self.send_header('Access-Control-Allow-Origin', '*')
				self.end_headers()
				
				
				conn = sqlite3.connect('tempdb.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
				cursor = conn.cursor()
				cursor.execute("""SELECT time, t1, t2, t3, hum1, coolingOn, heatingOn, fanOn FROM celltemp""")
				liste = []
				liste.append(["time", "t1", "t2", "t3", "hum1", "coolingOn", "heatingOn", "fanOn"])
				
				data = "["
				data += "[{\"type\": \"datetime\", \"label\": \"Season Start Date\"}, \"t1\", \"t2\", \"t3\", \"hum1\", \"coolingOn\", \"heatingOn\", \"fanOn\"]"
				#{type: 'datetime', label: 'Season Start Date'}
				
				for row in cursor:
					data += ",["
					data += row[0].strftime('"Date(%Y,%m,%d,%H,%M,%S)"') + "," + str(row[1]) + "," + str(row[2]) + "," + str(row[3]) + "," + str(row[4]) + "," + str(row[5]) + "," + str(row[6]) + "," + str(row[7])
					data += "]"
					
					# liste.append([row[0].strftime('Date(%Y,%m,%d,%H,%M,%S)'), row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
					
				data += "]"	
				# liste.append([123456, 1, 2, 3, 4, 5, 6, 7])
				# liste.append([5678, 1, 2, 3, 4, 5, 6, 7])
				
				
				#self.wfile.write(json.dumps(liste))
				self.wfile.write(data)
			else:
				self.send_response(400, 'Bad Request: record does not exist')
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
		else:
			self.send_response(403)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()

		return
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	allow_reuse_address = True

	def shutdown(self):
		self.socket.close()
		HTTPServer.shutdown(self)
 
class SimpleHttpServer():
	def __init__(self, ip, port):
		self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
 
	def start(self):
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.daemon = True
		self.server_thread.start()
 
	def waitForThread(self):
		self.server_thread.join()

	def addRecord(self, recordID, jsonEncodedRecord):
		LocalData.records[recordID] = jsonEncodedRecord

	def stop(self):
		self.server.shutdown()
		self.waitForThread()

# try:		
	# if __name__=='__main__':
		# parser = argparse.ArgumentParser(description='HTTP Server')
		# parser.add_argument('port', type=int, help='Listening port for HTTP Server')
		# parser.add_argument('ip', help='HTTP Server IP')
		# args = parser.parse_args()

		# server = SimpleHttpServer(args.ip, args.port)
		# print 'HTTP Server Running...........'
		# server.start()
		# server.waitForThread()
		
# except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
	# server.stop()
 
 
def main():
	try:
		parser = argparse.ArgumentParser(description='HTTP Server')
		parser.add_argument('port', type=int, help='Listening port for HTTP Server')
		parser.add_argument('ip', help='HTTP Server IP')
		args = parser.parse_args()

		server = SimpleHttpServer(args.ip, args.port)
		print 'HTTP Server Running...........'
		server.start()
		server.waitForThread()
	except KeyboardInterrupt:
		print '^C received, shutting down server'
		server.stop()

if __name__ == '__main__':
	main()