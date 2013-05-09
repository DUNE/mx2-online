#!/bin/sh

#./euler10 &
#MYPID=echo $!
#echo $MYPID

MYPID=$1

while [ -e /proc/$MYPID ] ; do
  sleep 60
done
echo "Process done" | mail -s " crate0 finished" mcgivern@fnal.gov
