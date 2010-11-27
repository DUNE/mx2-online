#!/bin/sh

# Use this script to restart the DataAcquisition manager in the WH Control 
# Room when running the DAQ in a "remote console" mode regardless of the 
# number of readout nodes.

. $HOME/mnvdaqrunscripts/defs_crpaths

which python2.6 >& /tmp/pytest.txt
PYV=`perl -ne 'if (/no/) { print "python"; } else { print "python2.6"; }' /tmp/pytest.txt`

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
	echo "No DAQROOT defined.  Sourcing the setup script..."
	source $HOME/mnvdaqrunscripts/setupdaqenv.sh $MULTIDAQ
fi


# Check to see if the dispatcher is running.  If it is, kill it.
pushd ${RCROOT}/backend >& /dev/null
$PYV DataAcquisitionManager.py stop
popd >& /dev/null

# Start the dispatcher.
pushd ${RCROOT}/backend >& /dev/null
$PYV DataAcquisitionManager.py start
popd >& /dev/null

ps -leaf | grep DataAcquisitionManager | grep -v grep
