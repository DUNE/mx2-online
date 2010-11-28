#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Run this to kill and restart all the DAQ and RC scripts on the minervatest
# cluster when running locally or x-forwarding the RC.  Assumes a valid 
# kerberos ticket!

. $HOME/mnvdaqrunscripts/defs_minervatest

# Kill all the local stuff.
echo "Going to kill local processes..."
source $HOME/mnvdaqrunscripts/proc_kill_ALLDAQRC_silent.sh

# Kill all the remote stuff.
echo "Going to kill remote processes..."
echo "Killing processes on the master node..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
echo "Killing processes on the soldier node..."
`ssh ${REMDAQACCT}@${SOLDERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
echo "Killing processes on the worker node..."
`ssh ${REMDAQACCT}@${WORKERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
echo "Waiting..."
sleep 1

# Restart the dispatchers...
echo "Now restarting the dispatchers..."
echo "Restarting processes on the master node..."
`ssh ${REMDAQACCT}@${MASTERMACH} source ${SCRIPTSDIR}/acquisitionmanager_multi.sh`
echo "Restarting processes on the soldier node..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Restarting processes on the worker node..."
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting..."
sleep 1

# Now, relaunch the RC.
echo "Restarting the Run Control!"
source $HOME/mnvdaqrunscripts/runcontrol_multi.sh 


