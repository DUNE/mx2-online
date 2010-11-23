#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Use this script to restart all the DAQ components running on the minervatest cluster 
# when running the RC locally and actually using client-server features of the RC.
# ASSUMES A VALID KERBEROS TICKET!

. $HOME/mnvdaqrunscripts/defs_minervatest

echo "Going to kill all remote ET processes..."
`ssh ${REMDAQACCT}@${MASTERMACH} $SCRIPTSDIR/etkiller.pl`
echo "Waiting 1..."
sleep 1

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh ${REMDAQACCT}@${SOLDERMACH} $SCRIPTSDIR/allkiller_silent.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} $SCRIPTSDIR/allkiller_silent.sh`
echo "Waiting 2..."
sleep 2
# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source $SCRIPTSDIR/dispatcher_multi.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source $SCRIPTSDIR/dispatcher_multi.sh`
echo "Waiting 2..."
sleep 2

# Restart the local acquisition manager, just in case.
source $HOME/mnvdaqrunscripts/acquistionmanager_multi.sh 

# Now, relaunch the RC on the LOCAL machine.
echo "Restarting the Run Control!"
source $HOME/mnvdaqrunscripts/runcontrol_multi26.sh

