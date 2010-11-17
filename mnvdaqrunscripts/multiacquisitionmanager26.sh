#!/bin/sh

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
        echo "No DAQROOT defined.  Sourcing the setup script..."
        source $HOME/mnvdaqrunscripts/setupdaqenv.sh /work/software/mnvonline/mnvdaq
fi

# Check to see if the dispatcher is running.  If it is, kill it.
pushd /work/software/mnvruncontrol/backend
python2.6 DataAcquisitionManager.py stop
popd

# Start the dispatcher.
pushd /work/software/mnvruncontrol/backend
python2.6 DataAcquisitionManager.py start
popd

ps -leaf | grep DataAcquisitionManager | grep -v grep
