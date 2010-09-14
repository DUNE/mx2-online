#!/bin/bash

# kill all processes in the same process group as the dispatcher.
processes=$(ps --sid $(ps -o sid $(cat /tmp/om_dispatcher.pid) | grep -oE "[[:digit:]]+") -o pid | grep -oE "[[:digit:]]+")

for process in $processes
do
	kill -s 0 "$process"
	if [ $? -eq 0 ]; then
		echo $process
	fi
done
