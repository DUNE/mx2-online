#!/bin/sh

gmake clean
gmake

if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then
#WH14T
	./chginj -c 1 -h 1 -f 1
	./chginj -c 1 -h 2 -f 1
	./chginj -c 1 -h 3 -f 1
fi

if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then
#WH14B
	./chginj -c 1 -h 1 -f 1 
	./chginj -c 1 -h 2 -f 2
	./chginj -c 1 -h 3 -f 1
	./chginj -c 5 -h 4 -f 2
	echo " "
	#echo "croc 5, most of 1 commented out now..."
fi

