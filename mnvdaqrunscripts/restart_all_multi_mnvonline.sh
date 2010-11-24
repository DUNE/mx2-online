#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Run this script on mnvonlinemaster to restart everything on the mnvonline cluster.
# ASSUMES VALID KERBEROS!

# Get cluster defs.
. $HOME/mnvdaqrunscripts/defs_mnvonline

echo "Going to kill all ET processes on local master..."
$SCRIPTSDIR/proc_kill_ET.pl
echo "Waiting 1..."
sleep 1
echo "Going to kill all minervadaq processes on local master..."
$SCRIPTSDIR/proc_kill_mnvdaq.pl
echo "Waiting 1..."
sleep 1
echo "Going to kill the Run Control on local master..."
$SCRIPTSDIR/proc_kill_RunCo.pl
echo "Waiting 1..."
sleep 1

# Assumes a valid kerberos ticket!
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

# Restart the acquisition manager, just in case.
source $SCRIPTSDIR/acquistionmanager_multi.sh 

# Now, relaunch the RC
echo "Restarting the Run Control!"
source $SCRIPTSDIR/runcontrol_multi.sh

