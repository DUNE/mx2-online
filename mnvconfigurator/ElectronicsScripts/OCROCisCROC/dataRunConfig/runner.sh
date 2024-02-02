#!/bin/sh

VOLTAGE=38000
ENABLE=1

if [ $# -eq 2 ] 
then
	VOLTAGE=$1
	ENABLE=$2
fi

WFEB=10
EFEB=9

CROC=1
./dataRunConfig -c $CROC -h 1 -f 1 -v $VOLTAGE -e $ENABLE  

exit 0
