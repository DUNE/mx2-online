#!/bin/sh

gmake clean
gmake

VOLTAGE=25000
ENABLE=0

if [ $# -eq 2 ] 
then
	VOLTAGE=$1
	ENABLE=$2
fi

if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then
#WH14T
	./lightLeakConfig -c 1 -h 3 -f 1 -v $VOLTAGE -e $ENABLE  
fi

if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then
#WH14B
	./lightLeakConfig -c 1 -h 1 -f 1 -v $VOLTAGE -e $ENABLE
	./lightLeakConfig -c 1 -h 2 -f 2 -v $VOLTAGE -e $ENABLE
#	./lightLeakConfig -c 1 -h 3 -f 1 -v $VOLTAGE -e $ENABLE
#	./lightLeakConfig -c 5 -h 4 -f 2 -v $VOLTAGE -e $ENABLE
	./lightLeakConfig -c 5 -h 4 -f 1 -v $VOLTAGE -e $ENABLE
	echo " "
fi


WFEB=10
EFEB=9

CROC=1
CROC=3
#./lightLeakConfig -c $CROC -h 2 -f $WFEB -v $VOLTAGE -e $ENABLE  
#./lightLeakConfig -c $CROC -h 3 -f $WFEB -v $VOLTAGE -e $ENABLE  
#./lightLeakConfig -c $CROC -h 4 -f $WFEB -v $VOLTAGE -e $ENABLE  
CROC=4
#./lightLeakConfig -c $CROC -h 2 -f $EFEB -v $VOLTAGE -e $ENABLE   
#./lightLeakConfig -c $CROC -h 3 -f $EFEB -v $VOLTAGE -e $ENABLE   
#./lightLeakConfig -c $CROC -h 4 -f $EFEB -v $VOLTAGE -e $ENABLE   
CROC=5
#./lightLeakConfig -c $CROC -h 1 -f $WFEB -v $VOLTAGE -e $ENABLE
#./lightLeakConfig -c $CROC -h 2 -f $WFEB -v $VOLTAGE -e $ENABLE
#./lightLeakConfig -c $CROC -h 3 -f $WFEB -v $VOLTAGE -e $ENABLE
CROC=6
#./lightLeakConfig -c $CROC -h 1 -f $EFEB -v $VOLTAGE -e $ENABLE
#./lightLeakConfig -c $CROC -h 2 -f $EFEB -v $VOLTAGE -e $ENABLE
#./lightLeakConfig -c $CROC -h 3 -f $EFEB -v $VOLTAGE -e $ENABLE

exit 0
