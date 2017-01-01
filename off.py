#!/usr/bin/python
# Send all 0 to the ledpanel
import probe

buf=bytearray(probe.panel_w * probe.panel_h * 3)
out_file = open("/sys/class/ledpanel/rgb_buffer","w")
out_file.write(buf)
out_file.close()
