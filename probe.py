#
# Probe panel size
# In case the 1.0 driver is installed assume a single 32 x 32 module
#

try:
	f=open('/sys/module/ledpanel/parameters/width')
	panel_w=int(f.read())
	f.close()
except:
	panel_w = 32

try:
	f=open('/sys/module/ledpanel/parameters/height')
	panel_h=int(f.read())
	f.close()
except:
	panel_h = 32

if __name__ == "__main__":	
	print "Panel size: %d x %d\n" % (panel_w, panel_h)
