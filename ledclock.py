#!/usr/bin/python
# Sliding digital clock on RGB led panel

import time
import sys
import os
from datetime import datetime
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import StringIO
import probe

if len(sys.argv)<2 or len(sys.argv)>4:
	print "Syntax:"
	print "  %s r g b" % (sys.argv[0])
	quit()

font = ImageFont.truetype('fonts/Ubuntu-B.ttf', 25)

r=int(sys.argv[1])
g=int(sys.argv[2])
b=int(sys.argv[3])
  
im = Image.new("RGB", (probe.panel_w, probe.panel_h), "black")
draw = ImageDraw.Draw(im)
draw.fontmode="1" #No antialias
width, height = font.getsize("88:88:88")
 
def format_time():
    d = datetime.now()
    return "{:%H:%M:%S}".format(d)
 
#message = format_time()


out_file = open("/sys/class/ledpanel/rgb_buffer","w")
output = StringIO.StringIO()

while True:
	message = format_time()

	draw.rectangle((0, 0, probe.panel_w - 1, height), outline=0, fill=0)
	draw.text((0, -1), message, (r<<5,g<<5,b<<5), font=font)
	
	output.truncate(0)
	im.save(output, format='PPM')
	buf=output.getvalue()
	
	out_file.seek(0)
	out_file.write(buf[13:])
	
	time.sleep(1)

out_file.close()
