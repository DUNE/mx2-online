#!/bin/sh

# Use this script when using the Run Control in the Wilson Hall CR to restart the 
# dispatchers on the readout nodes on the mnvonline cluster.

# Get cluster defs.
. $HOME/mnvdaqrunscripts/defs_mnvonline

# Need to kerberize first. 
. $HOME/mnvdaqrunscripts/Kerberize

# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting 2..."
sleep 2

# Now blow away kerberos ticket. (?)
kdestroy -c $KRB5CCNAME


