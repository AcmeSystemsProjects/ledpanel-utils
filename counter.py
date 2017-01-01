#!/usr/bin/python
# 2*n digit counter example for RGB led panel

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import StringIO
import time
import probe

#Panel size
size = probe.panel_w, probe.panel_h
print size

#Load a TTF font
font = ImageFont.truetype("fonts/Ubuntu-B.ttf", 26)

# compute how many digits have to be displayed
nd = (probe.panel_w / 32) * 2
# compute start count
max_n = pow(10,nd) -1
# compute format
frmt = "%d" % nd
frmt = '%0' + frmt + 'd'

#print frmt
#print nd
#print max_n

# Count backwards
for i in range(max_n,-1,-1):
	
	#Create a black image  
	im=Image.new("RGB",size,"black")

	#Create a draw object to draw primitives on the new image 
	draw = ImageDraw.Draw(im)
	draw.fontmode="1" #No antialias
	
	#Format the counter in 2 digit
	counter=frmt % i
	
	#Draw counter text on the panel 
	draw.text((0,0), counter, (0,0,1<<5), font=font)
	del draw

	#Generate a PPM image (a format very similar to byte array RGB we need)
	output = StringIO.StringIO()
	im.save(output, format='PPM')
	buf=output.getvalue()

	#Discard the first 13 bytes of header and save the rest (the
	#RGB array) on the ledpanel driver output buffer
	out_file = open("/sys/class/ledpanel/rgb_buffer","w")
	out_file.write(buf[13:])
	out_file.close()
	del im
	time.sleep(1)
