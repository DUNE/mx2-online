#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Run this to kill and restart all the DAQ and RC scripts on the minervatest 
# cluster when running locally or x-forwarding the RC.  Assumes a valid 
# kerberos ticket!

# Restart the nearonline... assume the test stand nearonline machine.
`ssh nearonline@mnvnearline0.fnal.gov source /home/nearonline/mnvdaqrunscripts/restart_nearline.sh`
 
# Restart the DAQ/RC...
source $HOME/mnvdaqrunscripts/restart_daq_rc_minervatest26.sh

