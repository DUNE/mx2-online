#!/bin/sh

# Use this script to restart the ReadoutDispatchers on the mnvonline machines 
# remotely via ssh.  
#
# Assumes a valid kerberos ticket!

. $HOME/mnvdaqrunscripts/defs_mnvonline

# Restart the dispatchers...
echo "Now restart dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting two seconds..."
sleep 2

