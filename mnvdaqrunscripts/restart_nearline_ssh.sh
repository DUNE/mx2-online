#!/bin/sh

# Kill them all, let God sort them out.
# -------------------------------------
# Assumes a valid kerberos ticket!  (Assumes running from non-control room PC.)

# Restart the nearonline...
`ssh nearonline@mnvnearline1.fnal.gov source /home/nearonline/mnvdaqrunscripts/restart_nearline.sh`

