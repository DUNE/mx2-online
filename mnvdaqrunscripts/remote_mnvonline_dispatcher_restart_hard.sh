#!/bin/sh

# Use this script to restart the dispatchers on the mnvonline cluster 
# readout nodes when on the mnvonline cluster master node.  Assumes a 
# valid kerberos ticket!

. $HOME/mnvdaqrunscripts/defs_mnvonline

# Nuke all the other DAQ stuff...
echo "Going to kill remote processes..."
`ssh ${REMDAQACCT}@${SOLDERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
echo "Waiting 2..."
sleep 2
# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting 2..."
sleep 2

