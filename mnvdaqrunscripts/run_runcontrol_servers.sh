#!/bin/sh

# Use this script to start/restart the ReadoutDispatcher and DataAcquisition 
# managers on the mnvonline or # minervatest cluster when running "locally" 
# (either at the terminal or via ssh'ed x-forwarding).

. $HOME/mnvdaqrunscripts/defs_standardpaths

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
        echo "No DAQROOT defined.  Sourcing the setup script..."
        source $HOME/croce_daqenv.sh
fi

# Get Python version.
which python2.6 >& /tmp/pytest.txt
PYV=`perl -ne 'if (/no/) { print "python"; } else { print "python2.6"; }' /tmp/pytest.txt`

# Check to see if the dispatcher is running.  If it is, stop/kill it.
pushd ${RCROOT}/backend >& /dev/null
$PYV ReadoutDispatcher.py stop
popd >& /dev/null

# Start the dispatcher.
pushd ${RCROOT}/backend >& /dev/null
$PYV ReadoutDispatcher.py start 
popd >& /dev/null

# Check to see if the acquisition manager is running.  If it is, stop/kill it.
pushd ${RCROOT}/backend >& /dev/null
$PYV DataAcquisitionManager.py stop
popd >& /dev/null

# Start the dispatcher.
pushd ${RCROOT}/backend >& /dev/null
$PYV DataAcquisitionManager.py start
popd >& /dev/null

ps -leaf | grep ReadoutDispatcher | grep -v grep
ps -leaf | grep DataAcquisitionManager | grep -v grep

## Now, start the RC.
#pushd ${RCROOT}/frontend
#$PYV RunControl.py &
#popd
#echo "If you get a socket binding error, just close the RC and wait a minute and then try again."
#echo "If you get a warning about the last subrun not finishing cleanly, just wait for the status "
#echo "bar, and then click okay."
#echo ""
#echo "You may need to exit the run control and run this script again..."
