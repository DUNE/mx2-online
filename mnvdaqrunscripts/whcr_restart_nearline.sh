#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Need to kerberize first. 
source $HOME/mnvdaqrunscripts/Kerberize

# Restart the nearonline...
`ssh nearonline@mnvnearline1.fnal.gov source /home/nearonline/mnvdaqrunscripts/restart_nearline.sh`
