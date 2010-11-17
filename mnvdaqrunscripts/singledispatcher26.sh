#!/bin/sh

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
        echo "No DAQROOT defined.  Sourcing the setup script..."
        source $HOME/mnvdaqrunscripts/setupdaqenv.sh /work/software/mnvsingle/mnvdaq
fi

# Check to see if the dispatcher is running.  If it is, kill it.
pushd /work/software/mnvruncontrol/backend
python2.6 ReadoutDispatcher.py stop
popd

# Start the dispatcher.
# Defaults to local host as the master.
pushd /work/software/mnvruncontrol/backend
python2.6 ReadoutDispatcher.py start 
popd

ps -leaf | grep ReadoutDispatcher | grep -v grep
