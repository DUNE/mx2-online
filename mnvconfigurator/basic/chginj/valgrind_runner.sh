#!/bin/sh

gmake clean
gmake

rm grindtest1.txt

#if [ $# -gt 0 ]; then
# if [ $1 == "v" ]; then
#  valgrind -v --log-file-exactly=valtest1.txt ./chginj
# fi
#else
#./chginj
#fi

if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then
#WH14T
	valgrind -v --log-file-exactly=grindtest1.txt ./chginj -c 1 -h 1 -f 1
	#./chginj -c 1 -h 2 -f 1
	#./chginj -c 1 -h 3 -f 1
	#echo " "
fi

if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then
#WH14B
	valgrind -v --log-file-exactly=grindtest1.txt ./chginj -c 1 -h 1 -f 1 
	#./chginj -c 1 -h 2 -f 2
	#./chginj -c 1 -h 3 -f 1
	#./chginj -c 5 -h 4 -f 2
	#echo " "
fi

