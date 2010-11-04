#!/bin/sh

# Assumes a valid kerberos ticket!
echo "Now restart dispatchers..."
`ssh minerva@minervatest02.fnal.gov source /home/minerva/mnvdaqrunscripts/multidispatcher.sh`
`ssh minerva@minervatest04.fnal.gov source /home/minerva/mnvdaqrunscripts/multidispatcher.sh`
echo "Waiting two seconds..."
sleep 2

