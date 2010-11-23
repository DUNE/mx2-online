#!/bin/sh

. $HOME/mnvdaqrunscripts/defs_nearlinepaths

lines=20

if [ $# -gt 0 ]; then
	lines=$1
fi

tail -n ${lines} ${OMLOGSROOT}/om_dispatcher.log
