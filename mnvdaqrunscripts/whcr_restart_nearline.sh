#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Need to kerberize first. 
source $HOME/mnvdaqrunscripts/Kerberize

# Restart the nearonline...
`ssh nearonline@mnvonlinelogger.fnal.gov source /scratch/nearonline/mirror/mnvdaqrunscripts/restart_nearline.sh`
