#!/bin/sh

# Assumes a valid kerberos ticket!
echo "Now restart dispatchers..."
`ssh minerva@minervatest2.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
`ssh minerva@minervatest4.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
echo "Waiting two seconds..."
sleep 2

