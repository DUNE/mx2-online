#!/bin/sh

# Checks to see why a subrun stopped early

# Get cluster defs.
. $HOME/mnvdaqrunscripts/defs_mnvonline

# Need to kerberize first. 
. $HOME/mnvdaqrunscripts/Kerberize

echo "Checking logfiles on ${MNVDAQ}..."
ssh ${REMDAQACCT}@${MNVDAQ} 'echo "for crate 0 :" ; grep -B 5 "crate 0" /work/data/logs/MV_*.txt; echo " "; echo "for crate 1 :" ; grep -B 5 "crate 1" /work/data/logs/MV_*.txt'







