#!/bin/sh

# Kill them all, let God sort them out.
echo "Going to kill all ET processes..."
$HOME/mnvdaqrunscripts/etkiller.pl
echo "Waiting..."
sleep 1
echo "Going to kill the Run Control..."
$HOME/mnvdaqrunscripts/rckiller.pl
echo "Waiting..."
sleep 1
echo "Going to kill the Dispatcher..."
$HOME/mnvdaqrunscripts/rdkiller.pl
echo "Waiting..."
sleep 1

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh minerva@minervatest02.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
`ssh minerva@minervatest04.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
sleep 2
# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh minerva@minervatest02.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
`ssh minerva@minervatest04.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
sleep 2

# Now, relaunch the RC
echo "Restarting the Run Control!"
source $HOME/mnvdaqrunscripts/multiruncontrol.sh

