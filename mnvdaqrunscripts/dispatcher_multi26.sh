#!/bin/sh

# Use this script to restart the ReadoutDispatcher on the mnvonline or 
# minervatest cluster when running "locally" (either at the terminal or via 
# ssh'ed x-forwarding) and a multi-node DAQ.

. $HOME/mnvdaqrunscripts/defs_standardpaths

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
        echo "No DAQROOT defined.  Sourcing the setup script..."
        source $HOME/mnvdaqrunscripts/setupdaqenv.sh $MULTIDAQ
fi

# Check to see if the dispatcher is running.  If it is, kill it.
pushd ${RCROOT}/backend >& /dev/null
python2.6 ReadoutDispatcher.py stop
popd >& /dev/null

# Start the dispatcher.
pushd ${RCROOT}/backend >& /dev/null
python2.6 ReadoutDispatcher.py start
popd >& /dev/null

ps -leaf | grep ReadoutDispatcher | grep -v grep
