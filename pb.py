#
# Arietta G25 push button management
#
# When the push button is hit, a command is executed
# This program takes two arguments:
#
# delay:    push button keydown period in seconds
# command:  what has to be executed when the pressing is detected
#

import time
import sys
import os


if len(sys.argv) != 3:
	print "Syntax:"
	print "  %s delay command" % (sys.argv[0])
	quit()

# activate GPIO
exp_file = open('/sys/class/gpio/export', "w")
exp_file.write ("81\n")
exp_file.close()


# setup the sys interface
keyfile = open('/sys/class/gpio/pioC17/value', "r")

c = 0

while True:
	time.sleep(1)
	# read the push button status (0 = pressed)
        keyfile.seek(0)
        val = int(keyfile.read().strip())

	# key hit
	if ( val == 0 ): c = c + 1
	
	# if counter is over threshold, exit
	if c > int(sys.argv[1]): break

# houskeeping
keyfile.close()

# remove GPIO
exp_file = open('/sys/class/gpio/unexport', "w")
exp_file.write ("81\n")
exp_file.close()


os.system(sys.argv[2])  

