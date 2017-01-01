#!/usr/bin/python
# Fill with a r g b color

import sys
import probe

if len(sys.argv)<4 or len(sys.argv)>4:
	print "Syntax:"
	print "  %s r g b" % (sys.argv[0])
	print
	print "Example:"
	print "  %s 10 0 0" % (sys.argv[0])
	quit()

R=int(sys.argv[1])
G=int(sys.argv[2])
B=int(sys.argv[3])

#Turn on all the led with the same color
buf = bytearray()
for i in range(probe.panel_w * probe.panel_h):   # 1024
	buf.append(R)
	buf.append(G)
	buf.append(B)

out_file = open("/sys/class/ledpanel/rgb_buffer","w")
out_file.write(buf)
out_file.close()
