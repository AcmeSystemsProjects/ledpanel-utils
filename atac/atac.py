try:
  # Python 2 import
  from xmlrpclib import Server
except ImportError:
  # Python 3 import
  from xmlrpc.client import Server

from pprint import pprint
import os


DEV_KEY = os.environ['ATAC_DEV_KEY']

token = 0

print "Atac module connecting to the server..."

try:
   s1 = Server('http://muovi.roma.it/ws/xml/autenticazione/1')
   s2 = Server('http://muovi.roma.it/ws/xml/paline/7')
except:
   print ("Data error")
   exit (254)	


try:
   token = s1.autenticazione.Accedi(DEV_KEY, '')
except:
   print ("Communication error")
   exit (255)	


linea = '715'
palina = 78636


#res = s2.paline.Previsioni(token, '70101', 'it')
#pprint(res)
#x = s2.paline.PalinaLinee (token, '70101', 'it');
#pprint(x)

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
		##pprint (arrivi)
		lista_arrivi = arrivi['risposta']['arrivi']
	
		#print ("##### lista arrivi palina %d:" % palina)
		#pprint (lista_arrivi)
	
		self.closer = 99999
	
		if len(lista_arrivi) > 0:
			for item in lista_arrivi:
				#print ("%s: %d" % (item['linea'], item['tempo_attesa'] ))
				t = item['tempo_attesa']
				if (t < self.closer): self.closer = t
			
			
		### print "%d" % closer
	
		return self.closer
		 
		 
	def run(self):
		i = 0
		while (1):
			if i % 60:
				try:
					get_time_of_arrival ()
				except:
					self.closer = 9999
				
			if self.stop_f == True:
				print "Thread stopped, exiting..."
				return
			else:
				time.sleep (1)
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
	while (x < 2):
		print ">>> %d" % thread1.get_arrival()
		time.sleep (10)
		x = x + 1
		
	stop()
		

	
	
