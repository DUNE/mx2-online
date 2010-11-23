#!/bin/sh

# Use this script to restart the dispatchers on the mnvonline cluster 
# readout nodes when on the mnvonline cluster master node.  Assumes a 
# valid kerberos ticket!

. $HOME/mnvdaqrunscripts/mnvonline_defs

# Assumes a valid kerberos ticket!
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

