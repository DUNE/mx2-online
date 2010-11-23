#!/bin/sh

# Use this script to restart the DataAcquisition manager on the mnvonline or 
# minervatest cluster when running "locally" (either at the terminal or via 
# ssh'ed x-forwarding) and a multi-node DAQ.

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
	echo "No DAQROOT defined.  Sourcing the setup script..."
	source $HOME/mnvdaqrunscripts/setupdaqenv.sh /work/software/mnvonline/mnvdaq
fi


# Check to see if the dispatcher is running.  If it is, kill it.
pushd /work/software/mnvruncontrol/backend >& /dev/null
python DataAcquisitionManager.py stop
popd >& /dev/null

# Start the dispatcher.
pushd /work/software/mnvruncontrol/backend >& /dev/null
python DataAcquisitionManager.py start
popd >& /dev/null

ps -leaf | grep DataAcquisitionManager | grep -v grep
