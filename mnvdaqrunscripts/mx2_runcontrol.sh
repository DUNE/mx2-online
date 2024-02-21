#!/bin/sh

echo "PYTHONPATH =" $PYTHONPATH

# Use this script to restart the RunControl GUI on a UROC.

. $DAQROOT/../mnvdaqrunscripts/defs_mx2paths

# Need to kerberize first. 
. $DAQROOT/../mnvdaqrunscripts/Kerberize

# First, clear any old RC clients...
$DAQROOT/../mnvdaqrunscripts/proc_kill_RunCo.pl

# Now, start the RC
pushd ${RCROOT}/frontend
echo "PYTHONPATH =" $PYTHONPATH
which python
python RunControl.py &
popd
echo "If you get a socket binding error, just close the RC and wait a minute and then try again."
echo "If you get a warning about the last subrun not finishing cleanly, just wait for the status "
echo "bar, and then click okay."
echo ""
echo "You may need to exit the run control and run this script again..."

