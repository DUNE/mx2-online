#!/bin/sh

# Use this script to restart the RunControl on the mnvonline or minervatest cluster when 
# running "locally" (either at the terminal or via ssh'ed x-forwarding) and a single-node DAQ.

. $HOME/mnvdaqrunscripts/defs_standardpaths

if test -z "$DAQROOT"
then
	echo "No DAQROOT defined.  Sourcing the setup script..."
	source $HOME/mnvdaqrunscripts/setupdaqenv.sh $SINGLEDAQ
fi

# First, clear any old RC clients...
$HOME/mnvdaqrunscripts/proc_kill_RunCo.pl

# Now, start the RC
pushd ${RCROOT}/frontend
python RunControl.py &
popd
echo "If you get a socket binding error, just close the RC and wait a minute and then try again."
echo "If you get a warning about the last subrun not finishing cleanly, just wait for the status "
echo "bar, and then click okay."
echo ""
echo "You may need to exit the run control and run this script again..."
