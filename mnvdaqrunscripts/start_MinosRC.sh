#!/bin/bash

#This is a wrapper script to run the Minos RC. It will kill all old Minos RC
#processes, kinit, then restart the processes. This allows the user to have
#a single command to run to restart the Minos RC, whether it has crashed or not.

echo "Killing any old Minos RC processes...."

./mnvdaqrunscripts/proc_kill_MinosRC.pl

echo "Kinit!  "
~/opt/rms/rms kinit

klist

echo "Restarting RC now...."
~/opt/rms/rms service rc near

###echo "Welcome to Minos Run Control!"


