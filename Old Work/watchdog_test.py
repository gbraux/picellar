import threading
import time
import sec_module
import shared_module
import array, fcntl, struct, termios, os
from subprocess import call


run = True
i = 0
f = 0

try:
	if __name__ == "__main__":

		#sec_module.startThread()
		
		# f = open('/dev/watchdog', 'r+', 0)
		
		# while run:
			# print(i)
			
			# if (i==5):
				# f.write('a')
				# print("WD reset sent")
				# i = 0
			
			# i += 1
			# time.sleep(1)
			
		#print(fcntl.WDIOC_SETTIMEOUT)
		call(["./wdt_set_timer"])

except (KeyboardInterrupt):
	print("Exiting ...")
	# f.write('V')
	# f.close()
		
	
		
	