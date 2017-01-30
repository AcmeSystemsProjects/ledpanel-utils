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
import subprocess

class SlidingMessage(threading.Thread):
	message="LedPanel"
	stop_request_flag=False
	sliding_delay=4
	red=0
	green=0
	blue=1

	# setup font
	#font1 = ImageFont.truetype('fonts/Ubuntu-B.ttf',30)
	#text_w, text_h = font1.getsize(message)	
	#output = StringIO.StringIO()
	
	def if_stop_requested(self):
		return self.stop_request_flag

	def stop(self):
		self.stop_request_flag=True
		
	def set_message(self,message):
		message = message + "        "
		self.message=message
		self.refresh_msg()
		
	def refresh_msg (self):
		font = ImageFont.truetype('fonts/Ubuntu-B.ttf', 32)
		width, height = font.getsize(self.message)
		
		print "[%s] W: %d H: %d" % (self.message, width, height)
		
		r=self.red << 4
		g=self.green << 4
		b=self.blue << 4
		
			
		im = Image.new("RGB", (width, 32), "black")
		draw = ImageDraw.Draw(im)
		draw.fontmode="1" #No antialias
		
		output = StringIO.StringIO()
		
		out_file = open("/tmp/out.ppm","w")
		
		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		draw.text((0,-1), self.message, (r,g,b), font=font)
		
		output.truncate(0)
		im.save(output, format='PPM')
		buf=output.getvalue()
		
		out_file.seek(0)
		out_file.write(buf)
		
		out_file.close()

		subprocess.call(["sudo", "pkill", "demo"])


	def set_color(self,red,green,blue):
		self.red=red
		self.green=green
		self.blue=blue
		self.refresh_msg()


	def set_sliding_delay(self,sliding_delay):
		self.sliding_delay=sliding_delay+1
		self.refresh_msg()
	
	def run(self):	

		while True:
			subprocess.call(["sudo", 
					"/home/pi/rpi-rgb-led-matrix/examples-api-use/demo", 
					"--led-chain=10",  
					"-t 10000000000", 
					"-D 1", 
					"-m %d" % self.sliding_delay, 
					"/tmp/out.ppm",
					"&"
					])

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

class do_shutdown(tornado.web.RequestHandler):
	def get(self):
		global t
		t.set_message("Shutdown....")
		subprocess.call(["sudo", 
				"shutdown", 
				"-H",  
				"-h", 
				"now", 
				"&"
				])		
						
class do_reboot(tornado.web.RequestHandler):
	def get(self):
		global t
		t.set_message("Reboot....")
		subprocess.call(["sudo", 
				"reboot", 
				"&"
				])
												
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
	(r"/do_shutdown", do_shutdown),
	(r"/do_reboot", do_reboot),
	(r"/(.*)", tornado.web.StaticFileHandler, {"path": ".","default_filename": "index-rpi.html"}),
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
	

