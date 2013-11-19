#!/bin/sh

# THIS SCRIPT IS A CANDIDATE FOR REMOVAL...

# Kill them all, let God sort them out.
# -------------------------------------
# Run this to kill and restart all the DAQ and RC scripts on the mnvonline1 
# and mnvonlinelogger when running locally or x-forwarding the RC.  

# Get cluster defs.
. $HOME/mnvdaqrunscripts/defs_mnvonline

# Need to kerberize first. 
. $HOME/mnvdaqrunscripts/Kerberize

# Kill and Restart the processes on mnvonline1...
echo "Killing processes on ${MNVDAQ}..."
`ssh  ${REMDAQACCT}@${MNVDAQ} source ${SCRIPTSDIR}/proc_kill_ALLDAQRC.sh` 
echo "Wait for it....."
sleep 5
echo "Restarting processes on ${MNVDAQ}..."
`ssh  ${REMDAQACCT}@${MNVDAQ} source ${SCRIPTSDIR}/run_runcontrol_servers.sh`
echo "Wait for it....."
sleep 5 

# Restart the RC...
echo "Restarting runcontrol..."
# Clear any old RC clients.
$HOME/mnvdaqrunscripts/proc_kill_RunCo.pl
sleep 5
. runcontrol.sh



