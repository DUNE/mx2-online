#!/bin/sh

Help()
{
	echo  "Usage : lightLeakCopier -d <data file:REQUIRED>  -p <path:default=/minerva/data/users/mnvonline>"
}

if [ $# -eq 0 ]
then
	Help
	exit 1
fi

ANAFILE=testme.dat
ANAPATH=/minerva/data/users/mnvonline

while [ $# -gt 0 ]
do
	case $1 in
		-d)	ANAFILE=$2
			shift 2 
           		;;
		-p)	ANAPATH=$2
			shift 2
			;;
	esac
done


echo "Attempting to copy: $ANAFILE to $ANAPATH" 

scp /work/data/rawdata/$ANAFILE mnvonline@if04.fnal.gov:$ANAPATH
