#!/usr/bin/python
#
# Show over a sliding text on single 32x32 RGB led panel
# the next bus arriving to a specific bus stop
#
# (c) 2014 Sergio Tanzilli - sergio@tanzilli.com 
# (c) 2016 Andrea Montefusco - andrew@montefusco.com
#

import time
import sys
import os
from datetime import datetime
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import StringIO
import atac

def get_color (tim):
	#
	# assign the right color according
	#
	if tim < 0:
		return (0,0,1)
	if tim < 4:
		return (20,0,0)
	if tim < 7:
		return (0,20,0)
	if (tim < 10):
		return (20,10,0)
	else:
		return (20,0,0)

def get_text_color ():
	closer_m, closer_s, n_stop, msg = atac.get_time_of_arrival_2 ()
	if closer_m < 0:
		if closer_s == -1 and len(msg):
			return (msg, (0,20,0))
		else:
			return ("no data for %s" % atac.get_line (), get_color(closer_m) )
	else:	
		return ("%s in %d min" % (atac.get_line (), closer_m), get_color(closer_m) )


	
if __name__ == '__main__':
	
	if len(sys.argv) < 2:
		print "Syntax:"
		print "  $s line pole" % (sys.argv[0])
		print
		quit()

	# initialize atac module
	atac.set_line (sys.argv[1])
	atac.set_pole (sys.argv[2])

	# load font
	font = ImageFont.truetype('../fonts/Ubuntu-B.ttf', 32)
		
	# create the image canvas	
	im = Image.new("RGB", (32, 32), "black")
	draw = ImageDraw.Draw(im)
	draw.fontmode="1" #No antialias
	
	# open the device driver 
	out_file = open("/sys/class/ledpanel/rgb_buffer","w")
	
	# initialize the buffer for raw data
	output = StringIO.StringIO()

	# initialize the x coordinate (for a screen 32x32)
	x = 32
	
	while True:
		if x == 32:
			# 
			# get updated text from real time data 
			#
			text, color = get_text_color()			
			width, height = font.getsize(text)
	
		x=x-1
	
		if x < -(width):
			x = 32
	
		# blank the screen image
		draw.rectangle((0, 0, 31, height), outline=0, fill=0)
		# draw text
		draw.text((x, -1), text, color, font=font)
		# clear the output buffer
		output.truncate(0)
		# dump the image into output buffer
		im.save(output, format='PPM')
		buf=output.getvalue()
		# reset device driver buffer
		out_file.seek(0)
		# write into device skipping the header of PPM format 
		out_file.write(buf[13:])
	
	
	# never reaches this point
	out_file.close()
	
