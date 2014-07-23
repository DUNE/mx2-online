#!/bin/sh

# Use this script to start/restart the correct run control servers 
# on the mnvonline or # minervatest cluster when running "locally" 
# (either at the terminal or via ssh'ed x-forwarding).

MASTER_NODE="mnvonline1.fnal.gov"

. $HOME/mnvdaqrunscripts/defs_standardpaths

# Need to kerberize first. 
. $HOME/mnvdaqrunscripts/Kerberize

RC_DISPATCHER=true

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
        echo "PYV =" $PYV "RCROOT =" $RCROOT
        echo "PYTHONPATH =" $PYTHONPATH

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
