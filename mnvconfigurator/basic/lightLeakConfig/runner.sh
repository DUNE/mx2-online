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

CROC=3
./lightLeakConfig -c $CROC -h 2 -f $WFEB -v $VOLTAGE -e $ENABLE  
./lightLeakConfig -c $CROC -h 3 -f $WFEB -v $VOLTAGE -e $ENABLE  
./lightLeakConfig -c $CROC -h 4 -f $WFEB -v $VOLTAGE -e $ENABLE  
CROC=4
./lightLeakConfig -c $CROC -h 2 -f $EFEB -v $VOLTAGE -e $ENABLE   
./lightLeakConfig -c $CROC -h 3 -f $EFEB -v $VOLTAGE -e $ENABLE   
./lightLeakConfig -c $CROC -h 4 -f $EFEB -v $VOLTAGE -e $ENABLE   
CROC=5
./lightLeakConfig -c $CROC -h 1 -f $WFEB -v $VOLTAGE -e $ENABLE
./lightLeakConfig -c $CROC -h 2 -f $WFEB -v $VOLTAGE -e $ENABLE
./lightLeakConfig -c $CROC -h 3 -f $WFEB -v $VOLTAGE -e $ENABLE
CROC=6
./lightLeakConfig -c $CROC -h 1 -f $EFEB -v $VOLTAGE -e $ENABLE
./lightLeakConfig -c $CROC -h 2 -f $EFEB -v $VOLTAGE -e $ENABLE
./lightLeakConfig -c $CROC -h 3 -f $EFEB -v $VOLTAGE -e $ENABLE

exit 0