#!/bin/bash

LOCKFILE="/tmp/emopuppy_monitor.lock"
(
  	flock -n 200 || exit 1
	cd /home/tf/workspace/emopuppy && sox -t alsa hw:2,0 -c 1 -r 16000 -t raw - 2>/dev/null |nc -vvN 81.70.190.164 8082 | ./monitor.py
) 200>$LOCKFILE

