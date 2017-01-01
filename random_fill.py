#!/usr/bin/python
# Fill random

import random
import probe

buf=bytearray(probe.panel_w * probe.panel_h * 3)

while True:
	i=0
	for row in range (0,probe.panel_h):
		for col in range (0,probe.panel_w):
				buf[i+0]=random.randint(0,15)
				buf[i+1]=random.randint(0,15)
				buf[i+2]=random.randint(0,15)
				i=i+3

	out_file = open("/sys/class/ledpanel/rgb_buffer","w")
	out_file.write(buf)
	out_file.close()

