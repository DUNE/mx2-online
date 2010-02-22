#!/bin/sh

VWINDOW=60

if [ $# -eq 1 ]
then
	VWINDOW=$1
fi

CROC=1
./hvCheck -c $CROC -h 1 -f 4 -w $VWINDOW
./hvCheck -c $CROC -h 2 -f 3 -w $VWINDOW 

exit 0
