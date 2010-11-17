#!/bin/sh

# Here, we have some possible confusion for a remote $HOME.  
MASTERMACH=minervatest03.fnal.gov
SOLDERMACH=minervatest02.fnal.gov
WORKERMACH=minervatest04.fnal.gov
REMDAQACCT=minerva

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh ${REMDAQACCT}@${SOLDERMACH} /home/minerva/mnvdaqrunscripts/allkiller_silent.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} /home/minerva/mnvdaqrunscripts/allkiller_silent.sh`
sleep 2
# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source /home/minerva/mnvdaqrunscripts/multidispatcher.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source /home/minerva/mnvdaqrunscripts/multidispatcher.sh`
sleep 2

