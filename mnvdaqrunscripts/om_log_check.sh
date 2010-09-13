#!/bin/sh

lines=20

if [ $# -gt 0 ]; then
	lines=$1
fi

tail -n ${lines} /scratch/nearonline/logs/om_dispatcher.log
