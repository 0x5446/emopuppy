#!/bin/bash

LOCKFILE="/tmp/emopuppy_monitor.lock"
(
  	flock -n 200 || exit 1
	cd /home/tf/workspace/emopuppy && sox -t alsa hw:2,0 -c 1 -r 16000 -t raw - 2>/dev/null |nc -vvN wakabot.com 8082 | ./monitor.py
) 200>$LOCKFILE

