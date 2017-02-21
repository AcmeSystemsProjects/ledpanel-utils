#!/usr/bin/python
# Draw a text as bitmap in ppm format
# (c) 2017 Andrea Montefusco
#

import time
import sys
import os

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import StringIO


if len(sys.argv)<4 or len(sys.argv)>5:
	print "Syntax (%d):" % len(sys.argv)
	print "  %s text r g b" % (sys.argv[0])
	print
	quit()
	
font = ImageFont.truetype('fonts/Ubuntu-B.ttf', 32)
width, height = font.getsize(sys.argv[1])


text=sys.argv[1]
r=int(sys.argv[2])
g=int(sys.argv[3])
b=int(sys.argv[4])

	
im = Image.new("RGB", (width, 32), "black")
draw = ImageDraw.Draw(im)
draw.fontmode="1" # No antialias

output = StringIO.StringIO()

# draw the background
draw.rectangle((0, 0, width, height), outline=0, fill=0)
# draw the text
draw.text((0,-1), text, (r,g,b), font=font)

# save the bitmap in output buffer
output.truncate(0)
im.save(output, format='PPM')

# save the bitmap into disk file
out_file = open("out.ppm","w")
out_file.seek(0)
out_file.write(output.getvalue())
out_file.close()

