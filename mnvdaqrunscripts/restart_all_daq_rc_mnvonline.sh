#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Run this to kill and restart all the DAQ and RC scripts on the mnvonline 
# cluster when running locally or x-forwarding the RC.  Assumes a valid 
# kerberos ticket!

. $HOME/mnvdaqrunscripts/defs_mnvonline

# Kill all the remote stuff.
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

# Restart acquisition manager.
$HOME/mnvdaqrunscripts/proc_kill_AcqMan.pl
source $HOME/mnvdaqrunscripts/acquistionmanager_multi.sh

# Now, relaunch the RC.
echo "Restarting the Run Control!"
source $HOME/mnvdaqrunscripts/runcontrol_multi.sh 


