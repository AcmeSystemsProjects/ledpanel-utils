from acmepins import GPIO
from time import time


class PushButton(GPIO):
	OFF = 0
	PRESSED = 1

	def __init__(self, name):
		GPIO.__init__(self,name,'INPUT')
		self.status = PushButton.OFF
		self.x = 0.0
		self.set_edge("both",self.event_handler)

	def pressed (self):
		pass

	def released (self):
		pass

	def event_handler(self):
		
		if (self.status == PushButton.OFF):
			
			if self.digitalRead() == 0:
				self.status = PushButton.PRESSED
				self.x = time()
				self.pressed()

		elif (self.status == PushButton.PRESSED):

			if self.digitalRead() == 0:
				self.x = time()
			else:
				if (time() - self.x) > 0.005:
					self.status = PushButton.OFF
					self.released();

		else:
			printf ("Fatal error: status unknown: %d" % self.status)
			
		
	
