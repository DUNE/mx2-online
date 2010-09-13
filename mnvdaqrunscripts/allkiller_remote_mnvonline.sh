#!/bin/sh

# Scorched earth.
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
`ssh mnvonline@mnvonline0.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`
`ssh mnvonline@mnvonline1.fnal.gov $HOME/mnvdaqrunscripts/allkiller_silent.sh`

# Assumes a valid kerberos ticket!
echo "Now restart dispatchers..."
`ssh mnvonline@mnvonline0.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`
`ssh mnvonline@mnvonline1.fnal.gov source $HOME/mnvdaqrunscripts/multidispatcher.sh`

