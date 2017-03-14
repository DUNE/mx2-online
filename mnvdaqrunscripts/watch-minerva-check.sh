#!/bin/bash
#
#  Watch dog cron script to check for running minerva-check.py scrit 
#  and restart it if necessary
#

checkScript="$HOME/mnvdaqrunscripts/minerva-check.py"
pid=$(ps -wwwfu minerva | grep -v grep | grep -v watch-minerva-check | grep "python $checkScript" | grep -G -o -m 1 '[1-9][0-9]*' | head -1)
echo $pid

if [ -z $pid ]; then
  echo "Restarting minerva-check.py"
  echo "`date` `hostname` restarting minerva-check.py" | mail -n -s "`date` `hostname` restarting minerva-check.py" badgett@fnal.gov, finer@fnal.gov, hbudd@fnal.gov, nur@fnal.gov
  python $checkScript >& /work/logs/minerva-check.log < /dev/null &
else
  echo "found it!"
fi
