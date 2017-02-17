#!/usr/bin/python
# Show a sliding text on RGB led panel
# (c) 2014 Sergio Tanzilli - sergio@tanzilli.com 
# multiple panel capability added by A.Montefusco 2017, 
# requires ledpanel.ko 2.0

import time
import sys
import os
from datetime import datetime
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import StringIO


if len(sys.argv)<4 or len(sys.argv)>5:
	print "Syntax (%d):" % len(sys.argv)
	print "  %s text r g b" % (sys.argv[0])
	print
	quit()
	
#panel_w = int(sys.argv[4])
#panel_h = int(sys.argv[5])

#print "Panel size: %d x %d\n" % (panel_w, panel_h)

font = ImageFont.truetype('fonts/Ubuntu-B.ttf', 32)
width, height = font.getsize(sys.argv[1])


text=sys.argv[1]
r=int(sys.argv[2])
g=int(sys.argv[3])
b=int(sys.argv[4])

	
im = Image.new("RGB", (width, 32), "black")
draw = ImageDraw.Draw(im)
draw.fontmode="1" #No antialias

output = StringIO.StringIO()
 
out_file = open("out.ppm","w")

draw.rectangle((0, 0, width, height), outline=0, fill=0)
draw.text((0,-1), text, (r,g,b), font=font)



output.truncate(0)
im.save(output, format='PPM')
buf=output.getvalue()

out_file.seek(0)
out_file.write(buf)

out_file.close()

