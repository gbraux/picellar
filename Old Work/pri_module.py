import threading
import time
import sec_module
import shared_module


def setGlobal(value):
	shared_module.sharedVariable = value
	
def readShared():
	while True:
		print "As see by main module : "+ shared_module.sharedVariable
		time.sleep(5)

if __name__ == "__main__":

	#sec_module.startThread()
	
	while True:
	
		t1 = threading.Thread(target=readShared)
		t1.daemon = True
		t1.start()
		
		sec_module.startThread()
		#print shared_module.sharedVariable
		
		while True:
			time.sleep(1)
	