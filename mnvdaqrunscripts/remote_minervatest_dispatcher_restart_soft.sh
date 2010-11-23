#!/bin/sh

# Use this script to restart the ReadoutDispatchers on the minervatest machines 
# remotely via ssh.
#
# Assumes a valid kerberos ticket!

. $HOME/mnvdaqrunscripts/defs_minervatest

# Restart the dispatchers only...

echo "Now restart dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting two seconds..."
sleep 2

