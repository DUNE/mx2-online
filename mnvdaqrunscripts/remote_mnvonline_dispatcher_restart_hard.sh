#!/bin/sh

# Here, we have some possible confusion for a remote $HOME.  
MASTERMACH=mnvonlinemaster.fnal.gov
SOLDERMACH=mnvonline0.fnal.gov
WORKERMACH=mnvonline1.fnal.gov
REMDAQACCT=mnvonline
SCRIPTDIR=/home/mnvonline/mnvdaqrunscripts

# Assumes a valid kerberos ticket!
echo "Going to kill remote processes..."
`ssh ${REMDAQACCT}@${SOLDERMACH} ${SCRIPTDIR}/allkiller_silent.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} ${SCRIPTDIR}/allkiller_silent.sh`
sleep 2
# Restart the dispatchers...
echo "Now restarting the dispatchers..."
`ssh ${REMDAQACCT}@${SOLDERMACH} source ${SCRIPTDIR}/multidispatcher.sh`
`ssh ${REMDAQACCT}@${WORKERMACH} source ${SCRIPTDIR}/multidispatcher.sh`
sleep 2

