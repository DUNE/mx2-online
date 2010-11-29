#!/bin/sh

# Use this script when using the Run Control in the Wilson Hall CR to restart the 
# dispatchers on the readout nodes on the minervatest cluster.

# Get cluster defs.
. $HOME/mnvdaqrunscripts/defs_minervatest

# Need to kerberize first. 
. $HOME/mnvdaqrunscripts/Kerberize

# Restart the dispatchers...
echo "Now restarting the dispatchers..."
echo "Restarting processes on the soldier node..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Restarting processes on the worker node..."
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting 2..."
sleep 2
echo "Restarting processes on the master node..."
`ssh ${REMDAQACCT}@${MASTERMACH} source ${SCRIPTSDIR}/acquisitionmanager_multi.sh`

