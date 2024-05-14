#!/bin/bash

LOCKFILE="/tmp/emopuppy_record.lock"
(
  	flock -n 200 || exit 1
	cd /home/tf/workspace/emopuppy && ./record.py
) 200>$LOCKFILE

