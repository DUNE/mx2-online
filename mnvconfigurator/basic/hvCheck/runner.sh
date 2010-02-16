#!/bin/sh

WFEB=10
EFEB=9
VWINDOW=60

if [ $# -eq 1 ]
then
	VWINDOW=$1
fi

CROC=3
./hvCheck -c $CROC -h 2 -f $WFEB -w $VWINDOW
./hvCheck -c $CROC -h 3 -f $WFEB -w $VWINDOW 
./hvCheck -c $CROC -h 4 -f $WFEB -w $VWINDOW 
CROC=4
./hvCheck -c $CROC -h 2 -f $EFEB -w $VWINDOW
./hvCheck -c $CROC -h 3 -f $EFEB -w $VWINDOW
./hvCheck -c $CROC -h 4 -f $EFEB -w $VWINDOW
CROC=5
./hvCheck -c $CROC -h 1 -f $WFEB -w $VWINDOW
./hvCheck -c $CROC -h 2 -f $WFEB -w $VWINDOW
./hvCheck -c $CROC -h 3 -f $WFEB -w $VWINDOW
CROC=6
./hvCheck -c $CROC -h 1 -f $EFEB -w $VWINDOW
./hvCheck -c $CROC -h 2 -f $EFEB -w $VWINDOW
./hvCheck -c $CROC -h 3 -f $EFEB -w $VWINDOW

exit 0
