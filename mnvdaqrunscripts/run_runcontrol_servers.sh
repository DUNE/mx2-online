#!/bin/sh

# Use this script to start/restart the correct run control servers 
# on the mnvonline or # minervatest cluster when running "locally" 
# (either at the terminal or via ssh'ed x-forwarding).

MASTER_NODE="mnvonline1.fnal.gov"
LI_NODE="mnvonline0.fnal.gov"
OM_NODE="mnvonlinelogger.fnal.gov"

. $HOME/mnvdaqrunscripts/defs_standardpaths

DAQ_MGR=false
RC_DISPATCHER=false

# determine which servers to run
case "$HOSTNAME" in
	${MASTER_NODE})
		DAQ_MGR=true
		RC_DISPATCHER=true
		;;
	
	${LI_NODE})
		RC_DISPATCHER=true
		;;

	${OM_NODE})
		echo "Please use the '~/dispatcher_nearline.sh' script to start the run control elements on this node instead of this one.  Thank you!"
		exit 1
		;;

	*)
		echo "I don't recognize your hostname: $HOSTNAME.  Not doing anything."
		exit 1
		;;
esac

# Setup environment for LinDAQ.
if [ -z "$DAQROOT" -a $RC_DISPATCHER ]
then
        echo "No DAQROOT defined.  Sourcing the setup script..."
	source $HOME/croce_daqenv.sh
fi

# Get Python version.
which python2.6 >& /tmp/pytest.txt
PYV=`perl -ne 'if (/no/) { print "python"; } else { print "python2.6"; }' /tmp/pytest.txt`

if [ $RC_DISPATCHER ]; then
	echo "Starting the run control's ReadoutDispatcher..."

	# Check to see if the dispatcher is running.  If it is, stop/kill it.
	pushd ${RCROOT}/backend >& /dev/null
	$PYV ReadoutDispatcher.py stop
	popd >& /dev/null

	# Start the dispatcher.
	pushd ${RCROOT}/backend >& /dev/null
	$PYV ReadoutDispatcher.py start 
	popd >& /dev/null

	echo " ... done."

	ps -leaf | grep ReadoutDispatcher | grep -v grep
fi

if [ $DAQ_MANAGER ]; then
	echo "Starting the data acquisition manager..."

	# Check to see if the acquisition manager is running.  If it is, stop/kill it.
	pushd ${RCROOT}/backend >& /dev/null
	$PYV DataAcquisitionManager.py stop
	popd >& /dev/null

	# Start the dispatcher.
	pushd ${RCROOT}/backend >& /dev/null
	$PYV DataAcquisitionManager.py start
	popd >& /dev/null

	echo " ... done."

	ps -leaf | grep DataAcquisitionManager | grep -v grep
fi

