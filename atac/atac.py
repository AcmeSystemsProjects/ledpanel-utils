import base64
import urllib
from urllib import unquote, splittype, splithost
try:
  # Python 2 import
  from xmlrpclib import Server
except ImportError:
  # Python 3 import
  from xmlrpc.client import Server

from pprint import pprint
import os

import xmlrpclib

class UrllibTransport(xmlrpclib.Transport):
    def set_proxy(self, proxy):
        self.proxyurl = proxy

    def request(self, host, handler, request_body, verbose=0):
        type, r_type = splittype(self.proxyurl)
        phost, XXX = splithost(r_type)

        puser_pass = None
        if '@' in phost:
            user_pass, phost = phost.split('@', 1)
            if ':' in user_pass:
                user, password = user_pass.split(':', 1)
                puser_pass = base64.encodestring('%s:%s' % (unquote(user),
                                                unquote(password))).strip()

        urlopener = urllib.FancyURLopener({'http':'http://%s'%phost})
        if not puser_pass:
            urlopener.addheaders = [('User-agent', self.user_agent)]
        else:
            urlopener.addheaders = [('User-agent', self.user_agent),
                                    ('Proxy-authorization', 'Basic ' + puser_pass) ]

        host = unquote(host)
        f = urlopener.open("http://%s%s"%(host,handler), request_body)

        self.verbose = verbose
        return self.parse_response(f)

DEV_KEY = os.environ['ATAC_DEV_KEY']

#
# global data
#
linea = ''
palina = 0
token = 0

# define a proxy
try:
	proxy = os.environ['ATAC_PROXY']
	p = UrllibTransport()
	p.set_proxy(proxy)
except:
	p = None

print "Atac module connecting to the server..........."

try:
   s1 = Server('http://muovi.roma.it/ws/xml/autenticazione/1', transport=p)
   s2 = Server('http://muovi.roma.it/ws/xml/paline/7', transport=p)
except:
   print ("Data error")
   exit (254)	


try:
   token = s1.autenticazione.Accedi(DEV_KEY, '')
except:
   print ("Communication error")
   exit (255)	


def set_line (nl):
	global linea
	linea = nl

def set_pole (np):
	global palina
	palina = np

def get_line ():
	global linea
	return linea

def get_pole ():
	global palina
	return palina


def ListStops (line):
	####
	#
	# list all bus stop for the line
	#
	line_d = s2.paline.Percorsi(token, line, 'it')
	#print ("##### line %s:" % line)
	#pprint(line_d)
	
	percorsi = line_d['risposta']['percorsi']
	np = len(percorsi)
	
	pid = []
	
	for p in percorsi:
		pprint(p)
		pid.append(p['id_percorso'])
	
	print ("##### percorsi: %d: %s" % (np, pid))
	
	for id in pid:
		p = s2.paline.Percorso(token, id, '', '', 'it')
		pprint(p)
		stops = p['risposta']['fermate']
		print ("################ PATH: %s" % id)
		for s in stops:
			print ("%s.%s" % (s['id_palina'], s['nome']))
	
####


#
# https://bitbucket.org/agenziamobilita/muoversi-a-roma/wiki/paline.Previsioni
#

def get_time_of_arrival ():

	arrivi = s2.paline.Previsioni(token, palina, 'it')
	##pprint (arrivi)
	lista_arrivi = arrivi['risposta']['arrivi']

	#print ("##### lista arrivi palina %d:" % palina)
	#pprint (lista_arrivi)

	closer = -1

	if len(lista_arrivi) > 0:
		for item in lista_arrivi:
			#print ("%s: %d" % (item['linea'], item['tempo_attesa'] ))
			t = item['tempo_attesa']
			if (closer < 0 or t < closer): closer = t
		
		
	### print "%d" % closer

	return closer
	
	
def get_time_of_arrival_2 ():

	arrivi = s2.paline.Previsioni(token, palina, 'it')
	##pprint (arrivi)
	lista_arrivi = arrivi['risposta']['arrivi']

	#print ("##### lista arrivi palina %d:" % palina)
	#pprint (lista_arrivi)

	closer_m = -1
	closer_s = -1
	n_stop = -1
	msg = ""

	if len(lista_arrivi) > 0:
		for item in lista_arrivi:
			#print ("%s: %d" % (item['linea'], item['tempo_attesa'] ))
			t = item['tempo_attesa']
			if (closer_m < 0 or t < closer_m):
				closer_m = t
				n_stop = item['distanza_fermate']
				closer_s = item['tempo_attesa_secondi']
				msg = item['annuncio']

	#print "%d %d %s .%s." % (closer_m, closer_s, n_stop, msg)

	return closer_m, closer_s, n_stop, msg


import threading
import time

class QueryThread(threading.Thread):
	def __init__(self,line, palina):
		super(QueryThread, self).__init__()
		self.line = line
		self.palina = palina
		self.closer = 9999
		self.stop_f = False

	def get_time_of_arrival(self):
		arrivi = s2.paline.Previsioni(token, self.palina, 'it')
		#pprint (arrivi)
		lista_arrivi = arrivi['risposta']['arrivi']
	
		#print ("##### lista arrivi palina %d:" % palina)
		#pprint (lista_arrivi)

		closer = 99999
	
		if len(lista_arrivi) > 0:
			for item in lista_arrivi:
				print ("TT -> %s: %d" % (item['linea'], item['tempo_attesa'] ))
				t = item['tempo_attesa']
				if (t < closer): closer = t
			
		self.closer = closer
		print "TT closer -> %d" % self.closer
	
		return self.closer
		 
		 
	def run(self):
		i = 0
		while (1):
			self.get_time_of_arrival ()

			if self.stop_f == True:
				print "Thread stopped, exiting..."
				return
			else:
				time.sleep (60)
				i = i + 1
		
	def get_arrival(self):
		return self.closer

	def stop(self):
		self.stop_f = True
		self.join()
		
		
thread1	= QueryThread('715', 78636)
		
def start():	
	thread1.start() # This actually causes the thread to run	

def stop():	
	thread1.stop() # This actually causes the thread to run	
	
print "Atac class initialized."	
	
if __name__ == '__main__':
	print "Starting...."
	start ()
	
	print "Entering in loop"
	x = 0
	while (x < 2000):
		print "MT >>>>>>>>>>> %d" % thread1.get_arrival()
		time.sleep (10)
		x = x + 1
		
	stop()
		

	
	
