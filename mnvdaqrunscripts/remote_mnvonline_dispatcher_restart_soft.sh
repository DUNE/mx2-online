#!/bin/sh

# Assumes a valid kerberos ticket!
echo "Now restart dispatchers..."
`ssh mnvonline@mnvonline0.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
`ssh mnvonline@mnvonline1.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
echo "Waiting two seconds..."
sleep 2

