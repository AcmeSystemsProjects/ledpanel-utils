from gpio_classes import PushButton
from time import sleep


class MyButton(PushButton):
	def __init(self, name):
		PushButton.__init(self, name)
		
	def pressed (self):
		print ">>>>>>>>>>>>>"
		
	def released (self):
		print "<<<<<<<<<<<<<"
		

button = MyButton('PC17')

i=0
while True:
	print button.status, i
	i=i+1
	sleep(0.5)
	
