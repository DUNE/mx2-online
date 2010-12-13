#!/bin/sh

# Use this script to restart the dispatchers on the readout nodes on the minervatest 
# cluster when running remotely but away from the control room (i.e., a valid kerberos 
# principal is assumed by this script).

# Get cluster defs.
. $HOME/mnvdaqrunscripts/defs_mnvonline

# Restart the dispatchers...
echo "Now restarting the dispatchers..."
echo "Restarting processes on the soldier node..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Restarting processes on the worker node..."
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting..."
sleep 1
echo "Waiting..."
sleep 1
echo "Restarting processes on the master node..."
source ${SCRIPTSDIR}/acquisitionmanager_multi.sh

