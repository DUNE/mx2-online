#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
. $HOME/mnvdaqrunscripts/defs_mnvonline

# Need to kerberize first. 
source $HOME/mnvdaqrunscripts/Kerberize

# Restart the nearonline...
#`ssh nearonline@mnvonlinelogger.fnal.gov source /home/nearonline/mnvdaqrunscripts/restart_nearline.sh`

# Kill all the remote stuff.
echo "Going to kill remote processes..." 
#echo "Killing processes on the master node..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
#echo "Killing processes on the soldier node..."
`ssh ${REMDAQACCT}@${SOLDERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
#echo "Killing processes on the worker node..."
#`ssh ${REMDAQACCT}@${WORKERMACH} ${SCRIPTSDIR}/proc_kill_ALLDAQRC_silent.sh`
echo "Waiting..."
sleep 1

# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/dispatcher_multi.sh`
#echo "Restarting processes on the soldier node..."
#`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
#echo "Restarting processes on the worker node..."
#`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/dispatcher_multi.sh`
echo "Waiting..."
sleep 1
echo "Waiting..."
sleep 1
echo "Restarting processes on the master node..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/acquisitionmanager_multi.sh`

# Have to keep ticket around in order to allow RC to function...
# Now, relaunch the RC on the LOCAL machine using the softlink.
echo "Restarting the Run Control!"
source $HOME/mnvdaqrunscripts/uroc_runcontrol.sh 


