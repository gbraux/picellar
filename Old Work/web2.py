from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import re
import sqlite3

class Handler(BaseHTTPRequestHandler):
    
	def do_GET(self):
			print self.path
			if None != re.search('/vinocell/api/v1/getdata/*', self.path):
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
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('192.168.11.63', 8080), Handler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()