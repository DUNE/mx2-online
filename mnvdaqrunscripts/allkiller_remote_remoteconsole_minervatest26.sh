#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Here, we have some possible confusion for a remote $HOME.  minervatest machines 
# should always be run using the "minerva" user, with $HOME "/home/minerva" - 
# however, some potential for shenanigans is possible when running from a remote 
# console.  Hence, keeping $HOME for killing "local" things, but using /home/minerva
# for stuff on test03.
MASTERMACH=minervatest03.fnal.gov
SOLDERMACH=minervatest02.fnal.gov
WORKERMACH=minervatest04.fnal.gov
REMDAQACCT=minerva
echo "Going to kill all ET processes..."
`ssh ${REMDAQACCT}@${MASTERMACH} /home/minerva/mnvdaqrunscripts/etkiller.pl`
echo "Waiting..."
sleep 1
echo "Going to kill the Run Control..."
`ssh ${REMDAQACCT}@${MASTERMACH} /home/minerva/mnvdaqrunscripts/rckiller.pl`
echo "Waiting..."
sleep 1
echo "Going to kill the Dispatcher..."
`ssh ${REMDAQACCT}@${MASTERMACH} /home/minerva/mnvdaqrunscripts/rdkiller.pl`
echo "Waiting..."
sleep 1

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh ${REMDAQACCT}@${SOLDERMACH} /home/minerva/mnvdaqrunscripts/allkiller_silent.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} /home/minerva/mnvdaqrunscripts/allkiller_silent.sh`
sleep 2
# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source /home/minerva/mnvdaqrunscripts/multidispatcher.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source /home/minerva/mnvdaqrunscripts/multidispatcher.sh`
sleep 2

# Now, relaunch the RC on the LOCAL machine.
echo "Restarting the Run Control!"
source $HOME/mnvdaqrunscripts/multiruncontrol26.sh

