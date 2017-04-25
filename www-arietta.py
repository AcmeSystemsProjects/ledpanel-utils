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
import Queue

class SlidingMessage(threading.Thread):
	
	def __init__(self, *args, **kwargs):
		super(SlidingMessage, self).__init__(*args, **kwargs)

		self.message="LedPanel"
		self.stop_request_flag=False
		self.sliding_delay=4
		self.red=1
		self.green=1
		self.blue=1
		self.q=Queue.Queue()


	def if_stop_requested(self):
		return self.stop_request_flag

	def stop(self):
		self.stop_request_flag=True
		self.q.put('q')
		
	def set_message(self,message):
		message = message + "              "
		self.message=message
		self.refresh_msg()
		
	def refresh (self):
		font = ImageFont.truetype('fonts/Ubuntu-B.ttf', 32)
		width, height = font.getsize(self.message)
		
		print "refresh_msg: [%s] W: %d H: %d" % (self.message, width, height)
		
		r=self.red   << 4
		g=self.green << 4
		b=self.blue  << 4
		
			
		im = Image.new("RGB", (width, 32), "black")
		draw = ImageDraw.Draw(im)
		draw.fontmode="1" #No antialias
		
		output = StringIO.StringIO()
		
		out_file = open("/tmp/out.ppm","w")
		
		print "refresh_msg: [%s] R: %d G: %d B: %d" % (self.message, r,g,b)
		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		draw.text((0,-1), self.message, (r,g,b), font=font)
		
		output.truncate(0)
		im.save(output, format='PPM')
		buf=output.getvalue()
		
		out_file.seek(0)
		out_file.write(buf)
		
		out_file.close()

		print "refresh_msg: killing subprocess....."
		subprocess.call(["pkill", "rotateppm"])

		subprocess.Popen([
				"/root/led-utils/rotateppm",
				"/tmp/out.ppm",
				"&"
				])
		print "refresh: background process restarted"


	def set_color(self,red,green,blue):
		self.red=red
		self.green=green
		self.blue=blue
		self.refresh_msg()


	def set_sliding_delay(self,sliding_delay):
		self.sliding_delay=sliding_delay+1
		self.refresh_msg()

	def refresh_msg (self):
		self.q.put('r')
	
	def run(self):	
		print "run started: flag: %s" % self.stop_request_flag
		x = 'r'
		while self.stop_request_flag != True:
			print "run: wait on queue: %s [%d]" % (x,self.q.qsize())
			if x == 'r':
				self.refresh()
				x = '.'

			while not self.q.empty():
				x = self.q.get()
				print "run: msg: %s [%d]" % (x,self.q.qsize())
				if x == 'q':
					self.stop_request_flag = True
					break

			if self.q.empty():
				x = self.q.get()

		print "run: exiting"
		return

def format_time():
    d = datetime.now()
    return "{:%H:%M}".format(d)


t = SlidingMessage()


#
# Web Server
#

class set_color(tornado.web.RequestHandler):
	def get(self):
		global t
		red = int(self.get_argument("red", default="0"))
		green = int(self.get_argument("green", default="0"))
		blue = int(self.get_argument("blue", default="0"))
		print "******* set_color: [%s][%s][%s]" % (red,green,blue)
		t.set_color(red,green,blue)

class set_sliding_delay(tornado.web.RequestHandler):
	def get(self):
		global t
		sliding_delay = int(self.get_argument("delay", default="0"))
		t.set_sliding_delay(sliding_delay)
		
class send_message(tornado.web.RequestHandler):
	def get(self):
		global t
		message = self.get_argument("message", default="").encode('raw_unicode_escape')
		print "******* send_message: new message: [%s]" % message
		t.set_message(message)

class do_shutdown(tornado.web.RequestHandler):
	def get(self):
		global t
		t.set_message("Shutdown....")
		subprocess.call([ 
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
		subprocess.call([ 
				"reboot", 
				"&"
				])
												
def signal_handler(signal, frame):
	global t

	print 'You pressed Ctrl+C!'
	t.stop()
	print "signal handler: killing subprocess....."
	subprocess.call(["pkill", "rotateppm"])
	t.join()
	sys.exit(0)


application = tornado.web.Application([
	(r"/send_message", send_message),
	(r"/set_color", set_color),
	(r"/set_sliding_delay", set_sliding_delay),
	(r"/do_shutdown", do_shutdown),
	(r"/do_reboot", do_reboot),
	(r"/(.*)", tornado.web.StaticFileHandler, {"path": ".","default_filename": "index-arietta.html"}),
])

######################################################################

#
# Main program
#

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
	

