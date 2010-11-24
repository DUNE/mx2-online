#!/bin/sh

# Use this script to restart the dispatchers on the readout nodes on the mnvonline 
# cluster when running remotely but away from the control room (i.e., a valid kerberos 
# principal is assumed by this script).

# Get cluster defs.
. $HOME/mnvdaqrunscripts/defs_mnvonline

# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting 2..."
sleep 2

