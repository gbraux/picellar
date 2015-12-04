#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SimpleHTTPServer
import SocketServer
import re
import sqlite3
import datetime
import urlparse
import config
import json


class vlab:
    def __init__(self,label, value):
        self.label = label
        self.value = value

class packet:
    def __init__(self, T1, T2, T3 ):
        self.T1 = T1
        self.T2 = T2
        self.T3 = T3
		
class allDatas:
	def __init__(self, add):
		self.data = add

data = [packet(vlab("ez","fds"),vlab("ez","fds"),vlab("ez","fds")),packet(vlab("ez","fds"),vlab("ez","fds"),vlab("ez","fds")),packet(vlab("ez","fds"),vlab("ez","fds"),vlab("ez","fds"))]
finalClass = allDatas([packet(vlab("ez","fds"),vlab("ez","fds"),vlab("ez","fds")),packet(vlab("ez","fds"),vlab("ez","fds"),vlab("ez","fds")),packet(vlab("ez","fds"),vlab("ez","fds"),vlab("ez","fds"))])

		
print(json.dumps(packet(vlab("ez","fds"),vlab("ez","fds"),vlab("ez","fds")).__dict__, indent=4))	

# data2 = {}
# data2["data"] = []
# data2["data"].append(

test = [{"T1" : {"label" : "blabla", "value" : "12345"}, "T2" : {"label" : "blabla", "value" : "12345"} ,"T3" : {"label" : "blabla", "value" : "12345"}},{"T1" : {"label" : "blabla", "value" : "12345"}, "T2" : {"label" : "blabla", "value" : "12345"} ,"T3" : {"label" : "blabla", "value" : "12345"}}]


print(json.dumps(test, indent=4))
jsonencoded = json.dumps(test)
jsondecoded = json.loads(jsonencoded)

for entry in jsondecoded:
	print entry["T2"]["value"]

# data2["data"]["time"] = {"label" : "blabla", "value" : "12345"}
# data2["data"]["T1"] = {"label" : "blabla", "value" : "12345"}
# data2["data"]["T2"] = {"label" : "blabla", "value" : "12345"}
# data2["data"]["T3"] = {"label" : "blabla", "value" : "12345"}



# data2["data"].append("time").append({"name" : "time", "label" : "blabla", "value" : "12345"});
# data2["data"].append("time").append({"name" : "time", "label" : "blabla", "value" : "12345"});
# data2["data"].append("time").append({"name" : "time", "label" : "blabla", "value" : "12345"});

# data2["data"].append({"time" : {"name" : "time", "label" : "blabla", "value" : "12345"}})
# data2["data"].append({"T1" : {"name" : "time", "label" : "blabla", "value" : "12345"}})
# data2["data"].append({"T2" : {"name" : "time", "label" : "blabla", "value" : "12345"}})
# data2["data"].append({"T3" : {"name" : "time", "label" : "blabla", "value" : "12345"}})


# print(json.dumps(data2, indent=4))