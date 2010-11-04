#!/bin/sh

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh minerva@minervatest02.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
`ssh minerva@minervatest04.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
echo "Waiting two seconds..."
sleep 2

# Assumes a valid kerberos ticket!
echo "Now restart dispatchers..."
`ssh minerva@minervatest02.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
`ssh minerva@minervatest04.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
echo "Waiting two seconds..."
sleep 2

