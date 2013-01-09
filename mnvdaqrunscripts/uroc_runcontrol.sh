#!/bin/sh

# Use this script to restart the RunControl GUI on a UROC.

. $HOME/mnvdaqrunscripts/defs_crpaths

# Need to kerberize first. 
. $HOME/mnvdaqrunscripts/Kerberize

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

