#!/bin/sh

MASTER=minervatest03.fnal.gov
DISPAF=/work/conditions/readout_dispatcher.pid
if [ $# -gt 0 ]; then
	$MASTER=$1
fi

# Setup environment for LinDAQ.
if test -z "$DAQROOT"
then
        echo "No DAQROOT defined.  Sourcing the setup script..."
        source $HOME/mnvdaqrunscripts/setupdaqenv.sh /work/software/mnvonline/mnvdaaq
fi

# Check to see if the dispatcher is running.  If it is, kill it.
pushd /work/software/mnvruncontrol/backend
python RunControlDispatcher.py -m ${MASTER} stop
popd

# Start the dispatcher.
pushd /work/software/mnvruncontrol/backend
python RunControlDispatcher.py -m ${MASTER} start &
popd


