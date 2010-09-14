#!/bin/sh

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh mnvonline@mnvonline0.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
`ssh mnvonline@mnvonline1.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
echo "Waiting two seconds..."
sleep 2

# Assumes a valid kerberos ticket!
echo "Now restart dispatchers..."
`ssh mnvonline@mnvonline0.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
`ssh mnvonline@mnvonline1.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
echo "Waiting two seconds..."
sleep 2

