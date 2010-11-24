#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
. $HOME/mnvdaqrunscripts/defs_minervatest

# Need to kerberize first. 
source $HOME/mnvdaqrunscripts/Kerberize

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

# Now blow away kerberos ticket. (?)
kdestroy -c $KRB5CCNAME

# Restart acquisition manager - handled in whcr_runcontrol26.sh
# Now, relaunch the RC on the LOCAL machine using the softlink.
echo "Restarting the Run Control!"
source $HOME/mnvdaqrunscripts/whcr_runcontrol26.sh

