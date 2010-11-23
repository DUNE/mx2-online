#!/bin/sh

# Kill them all, let God sort them out.

# Get cluster defs.
. $HOME/mnvdaqrunscripts/mnvonline_defs

# Need to kerberize first. 
. $HOME/mnvdaqrunscripts/Kerberize

echo "Going to kill all ET processes..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/etkiller.pl`
echo "Waiting 1..."
sleep 1
echo "Going to kill the Dispatcher..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/rdkiller.pl`
echo "Waiting 1..."
sleep 1
echo "Going to kill remote processes..."
`ssh ${REMDAQACCT}@${SOLDERMACH} ${SCRIPTSDIR}/allkiller_silent.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} ${SCRIPTSDIR}/allkiller_silent.sh`
echo "Waiting 2..."
sleep 2

# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/multidispatcher.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/multidispatcher.sh`
echo "Waiting 2..."
sleep 2

# Now, relaunch the RC on the LOCAL machine using the softlink.
echo "Restarting the Run Control!"
source $HOME/runcontrol.sh

