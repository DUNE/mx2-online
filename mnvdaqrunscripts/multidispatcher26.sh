#!/bin/sh

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
        echo "No DAQROOT defined.  Sourcing the setup script..."
        source $HOME/mnvdaqrunscripts/setupdaqenv.sh /work/software/mnvonline/mnvdaq
fi

# Check to see if the dispatcher is running.  If it is, kill it.
pushd /work/software/mnvruncontrol/backend >& /dev/null
python2.6 ReadoutDispatcher.py stop
popd >& /dev/null

# Start the dispatcher.
pushd /work/software/mnvruncontrol/backend >& /dev/null
python2.6 ReadoutDispatcher.py start
popd >& /dev/null

ps -leaf | grep ReadoutDispatcher | grep -v grep
