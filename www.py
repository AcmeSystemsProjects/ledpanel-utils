#!/usr/bin/python

import tornado.ioloop
import tornado.web
import time
import sys
import os
from datetime import datetime
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import StringIO
import thread
import threading
import signal
import commands
import probe

class SlidingMessage(threading.Thread):
	message="LedPanel"
	stop_request_flag=False
	sliding_delay=0
	red=0
	green=0
	blue=1

	# setup font
	font1 = ImageFont.truetype('fonts/Ubuntu-B.ttf',30)
	text_w, text_h = font1.getsize(message)	
	# access device driver input buffer
	out_file = open("/sys/class/ledpanel/rgb_buffer","w")
	output = StringIO.StringIO()
	# setup image cache
	imgs = {}
	
	def if_stop_requested(self):
		return self.stop_request_flag

	def stop(self):
		self.stop_request_flag=True
		
	def set_message(self,message):
		self.message=message
		self.imgs = {}  # empty images cache

	def set_color(self,red,green,blue):
		self.red=red
		self.green=green
		self.blue=blue
		self.imgs = {}  # empty images cache 

	def set_sliding_delay(self,sliding_delay):
		self.sliding_delay=sliding_delay
	
	def run(self):	

		if self.message=="":
			output.truncate(0)
			im.save(output, format='PPM')
			buf=output.getvalue()

			out_file.seek(0)
			out_file.write(buf[13:])
			out_file.close()

			while True:
				time.sleep(60)
		
		x = probe.panel_w
		while True:
			x = x - 1
			im = None
			
			self.text_w, self.text_h = self.font1.getsize(self.message)
			
			if x < -(self.text_w):
				x = probe.panel_w
				continue
				
			if (x in self.imgs.keys()):
				im = self.imgs [x]  # image already in cache
			else:
				# generate the image at x coordinate
				im = Image.new("RGB", (probe.panel_w, probe.panel_h), "black")
				draw = ImageDraw.Draw(im)
				draw.fontmode="1" #No antialias
				draw.rectangle((0, 0, probe.panel_w - 1, probe.panel_h - 1), outline=0, fill=0)
	
				color_set=(self.red,self.green,self.blue)
				draw.text((x,-4), self.message, color_set, font=self.font1)
				# cache update
				self.imgs[x] = im
	
			self.output.truncate(0)
			im.save(self.output, format='PPM')
			buf=self.output.getvalue()
	
			self.out_file.seek(0)
			self.out_file.write(buf[13:])

			if self.if_stop_requested():
				break;

			if self.sliding_delay > 0 :
				time.sleep(self.sliding_delay/100.0)

		out_file.close()
		return

def format_time():
    d = datetime.now()
    return "{:%H:%M}".format(d)

class set_color(tornado.web.RequestHandler):
	def get(self):
		red = int(self.get_argument("red", default="0"))
		green = int(self.get_argument("green", default="0"))
		blue = int(self.get_argument("blue", default="0"))
		t.set_color(red,green,blue)

class set_sliding_delay(tornado.web.RequestHandler):
	def get(self):
		sliding_delay = int(self.get_argument("delay", default="0"))
		t.set_sliding_delay(sliding_delay)
		
class send_message(tornado.web.RequestHandler):
	def get(self):
		global t
		message = self.get_argument("message", default="")
		t.set_message(message)

def signal_handler(signal, frame):
	global sliding_message

	print 'You pressed Ctrl+C!'
	t.stop()
	t.join()
	sys.exit(0)


application = tornado.web.Application([
	(r"/send_message", send_message),
	(r"/set_color", set_color),
	(r"/set_sliding_delay", set_sliding_delay),
	(r"/(.*)", tornado.web.StaticFileHandler, {"path": ".","default_filename": "index.html"}),
])

t=SlidingMessage()

if __name__ == "__main__":	

	ips = commands.getoutput("ifconfig | grep -i inet | grep -iv inet6 | " +
							"grep -iv 127.0.0.1 | grep -iv 192.168.10.10 |" +
							"awk {'print $2'} | sed -ne 's/addr\:/ /p'")  
	iplist=ips.splitlines()
	t.set_message ("myIP" + " -".join(iplist))
	
	t.start()
	
	signal.signal(signal.SIGINT, signal_handler)
	print 'Press Ctrl+C to exit'
	
	application.listen(8080,"0.0.0.0")
	tornado.ioloop.IOLoop.instance().start() 
	

