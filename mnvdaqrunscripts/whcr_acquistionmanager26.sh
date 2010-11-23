#!/bin/sh

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
	echo "No DAQROOT defined.  Sourcing the setup script..."
	source /home/minerva/mnvdaqrunscripts/setupdaqenv.sh /home/minerva/wx_support/mnvdaq
fi


# Check to see if the dispatcher is running.  If it is, kill it.
pushd /home/minerva/mnvruncontrol/backend >& /dev/null
python2.6 DataAcquisitionManager.py stop
popd >& /dev/null

# Start the dispatcher.
pushd /home/minerva/mnvruncontrol/backend >& /dev/null
python2.6 DataAcquisitionManager.py start
popd >& /dev/null

ps -leaf | grep DataAcquisitionManager | grep -v grep
