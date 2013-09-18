#!/bin/sh

# Use this script to start the RC remotely without killing the control room 
# runcontrol. It is only for EXPERTS! It doesn't do the proper cleanup
# so normal operations should use the normal start_MinervaRC.sh script 
# which is linked to from the runcontrol.sh script. 

echo "This script is only for experts working from home!! "
#echo "Are you an expert working from home? yes/no:"

#read answer 

#if["$answer"=="yes"]; then 
#    echo "Excellent! Go solve problems!" 
#else
#    echo "Please use the normal start_MinervaRC.sh script" 
#    exit 1
#fi

. $HOME/mnvdaqrunscripts/defs_crpaths

# Need to kerberize first. 
. $HOME/mnvdaqrunscripts/Kerberize

# First, clear any old RC clients...
$HOME/mnvdaqrunscripts/proc_kill_RunCo.pl

#Now clear any leftover tunnels that might be left open. 
#$HOME/mnvdaqrunscripts/proc_kill_tunnels.pl

# Now, start the RC
pushd ${RCROOT}/frontend
python RunControl.py &
popd
echo "If you get a socket binding error, just close the RC and wait a minute and then try again."
echo "If you get a warning about the last subrun not finishing cleanly, just wait for the status "
echo "bar, and then click okay."
echo ""
echo "You may need to exit the run control and run this script again..."
