#!/bin/sh

# Use this script to restart the RunControl GUI in the WH Control 
# Room when running the DAQ in a "remote console" mode. 

. $HOME/mnvdaqrunscripts/defs_crpaths

if test -z "$DAQROOT"
then
	echo "No DAQROOT defined.  Sourcing the setup script..."
	source $HOME/mnvdaqrunscripts/setupdaqenv.sh $MULTIDAQ
fi

# First, clear any old RC clients...
$HOME/mnvdaqrunscripts/proc_kill_RunCo26.pl

# Now, start the RC
pushd ${RCROOT}/frontend
python2.6 RunControl.py &
popd
echo "If you get a socket binding error, just close the RC and wait a minute and then try again."
echo "If you get a warning about the last subrun not finishing cleanly, just wait for the status "
echo "bar, and then click okay."
echo ""
echo "You may need to exit the run control and run this script again..."

