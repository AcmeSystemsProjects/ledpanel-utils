#!/bin/bash

LINE="715"
POLE="78636"

HBEGIN="14"
HEND="19"

DBEGIN="1"   # 0=SUNDAY 1 = MONDAY ... 5=FRIDAY 6=SATURDAY
DEND="6"

/bin/date

while true; do

	hh=$(/bin/date +"%-H")
	dd=$(/bin/date +"%w")

	if [[ $hh -ge $HBEGIN &&  $hh -le $HEND ]] && [[ $dd -ge $DBEGIN && $dd -le $DEND ]] ; then

		#/bin/date

		/usr/bin/timeout 600 /bin/sh -c "/usr/bin/python atac-panel.py $LINE $POLE"

		# blanks the panel
		cd ..
		/usr/bin/python text.py "AA" 0 0 0 1
		cd atac
	else
		/bin/sleep 60
	fi
done
