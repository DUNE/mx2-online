#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Run this to kill and restart all the nearline processes on the 
# mnvnearline cluster when logged into the cluster.  Obviously, 
# assumes a valid kerberos ticket!

. $HOME/mnvdaqrunscripts/defs_nearlinepaths

# Kill all the stuff...
#  First kill event builders, Gaudi stuff...
$SCRIPTSDIR/proc_kill_MinNearline.pl
#  Now kill the dispatcher...
$SCRIPTSDIR/proc_kill_MonDisp.pl

# Restart the dispatcher, etc.
source $SCRIPTSDIR/dispatcher_nearline.sh


