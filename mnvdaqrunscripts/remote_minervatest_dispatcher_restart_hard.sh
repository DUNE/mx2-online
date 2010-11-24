#!/bin/sh

# Use this script to restart the ReadoutDispatchers on the minervatest machines 
# remotely via ssh.  Will also nuke all DAQ processes.
#
# Assumes a valid kerberos ticket!

. $HOME/mnvdaqrunscripts/defs_minervatest

# First kill all DAQ stuff (it is useless w/o the dispatchers anyway).
echo "Going to kill remote processes..."
`ssh ${REMDAQACCT}@${SOLDERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
sleep 2
# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
sleep 2

