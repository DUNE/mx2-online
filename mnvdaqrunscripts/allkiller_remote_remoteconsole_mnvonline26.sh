#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Here, we have some possible confusion for a remote $HOME.  minervatest machines 
# should always be run using the "minerva" user, with $HOME "/home/minerva" - 
# however, some potential for shenanigans is possible when running from a remote 
# console.  Hence, keeping $HOME for killing "local" things, but using /home/minerva
# for stuff on test03.
MASTERMACH=mnvonlinemaster.fnal.gov
SOLDERMACH=mnvonline0.fnal.gov
WORKERMACH=mnvonline1.fnal.gov
REMDAQACCT=mnvonline
SCRIPTSDIR=/home/mnvonline/mnvdaqrunscripts
echo "Going to kill all ET processes..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/etkiller.pl`
echo "Waiting..."
sleep 1
echo "Going to kill the Run Control..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/rckiller.pl`
echo "Waiting..."
sleep 1
echo "Going to kill the Dispatcher..."
`ssh ${REMDAQACCT}@${MASTERMACH} ${SCRIPTSDIR}/rdkiller.pl`
echo "Waiting..."
sleep 1

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh ${REMDAQACCT}@${SOLDERMACH} ${SCRIPTSDIR}/allkiller_silent.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} ${SCRIPTSDIR}/allkiller_silent.sh`
sleep 2
# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTSDIR}/multidispatcher.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTSDIR}/multidispatcher.sh`
sleep 2

# Now, relaunch the RC on the LOCAL machine using the softlink.
echo "Restarting the Run Control!"
source $HOME/runcontrol.sh

