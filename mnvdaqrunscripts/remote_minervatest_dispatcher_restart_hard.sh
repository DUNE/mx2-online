#!/bin/sh

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh minerva@minervatest2.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
`ssh minerva@minervatest4.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
echo "Waiting two seconds..."
sleep 2

# Assumes a valid kerberos ticket!
echo "Now restart dispatchers..."
`ssh minerva@minervatest2.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
`ssh minerva@minervatest4.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
echo "Waiting two seconds..."
sleep 2

