#!/bin/sh

#if [ $# -eq 1 ]
#then
#	VWINDOW=$1
#fi

./runner_1.sh &
./runner_2.sh &
./runner_3.sh &
./runner_4.sh &
./runner_5.sh &
./runner_6.sh &
./runner_7.sh &
./runner_8.sh &

exit 0
