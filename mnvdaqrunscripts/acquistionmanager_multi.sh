#!/bin/sh

# Use this script to restart the DataAcquisition manager on the mnvonline or 
# minervatest cluster when running "locally" (either at the terminal or via 
# ssh'ed x-forwarding) and a multi-node DAQ.

. $HOME/mnvdaqrunscripts/defs_standardpaths

which python2.6 >& /tmp/pytest.txt
PYV=`perl -ne 'if (/no/) { print "python"; } else { print "python2.6"; }' /tmp/pytest.txt`

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
	echo "No DAQROOT defined.  Sourcing the setup script..."
	source $HOME/mnvdaqrunscripts/setupdaqenv.sh $MULTIDAQ
fi


# Check to see if the acquisition manager is running.  If it is, stop/kill it.
pushd ${RCROOT}/backend >& /dev/null
$PYV DataAcquisitionManager.py stop
popd >& /dev/null

# Start the dispatcher.
pushd ${RCROOT}/backend >& /dev/null
$PYV DataAcquisitionManager.py start
popd >& /dev/null

ps -leaf | grep DataAcquisitionManager | grep -v grep
