#!/bin/sh

# Use this script to start the RunControl GUI on the mnvonline or minervatest cluster 
# when running "locally" (either at the terminal or via ssh'ed x-forwarding) and a multi-node DAQ.

. $HOME/mnvdaqrunscripts/defs_standardpaths

if test -z "$DAQROOT"
then
	echo "No DAQROOT defined.  Sourcing the setup script..."
	source $HOME/mnvdaqrunscripts/setupdaqenv.sh $MULTIDAQ
fi

# First, clear any old RC clients...
$HOME/mnvdaqrunscripts/rckiller.pl

# Now, start the RC
pushd ${RCROOT}/frontend >& /dev/null
python RunControl.py &
popd >& /dev/null
echo "If you get a socket binding error, just close the RC and wait a minute and then try again."
echo "If you get a warning about the last subrun not finishing cleanly, just wait for the status "
echo "bar, and then click okay."
echo ""
echo "You may need to exit the run control and run this script again..."

