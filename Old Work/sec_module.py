import threading
import time
import pri_module


	

def update_pri_module_global():
	
	while True:
		#pri_module.setGlobal("Modified by sec_module thread")
		pri_module.setGlobal("Modified by sec_module thread")
		print "Global Updated by sec_module"
		time.sleep(1)
	
def startThread():
	t2 = threading.Thread(target=update_pri_module_global)
	t2.daemon = True
	t2.start()