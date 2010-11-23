#!/bin/sh

# Run this script while logged in to a nearonline machine to kill all 
# monitoring processes and restart the dispatcher.

/home/nearonline/mnvdaqrunscripts/nearlinekiller.pl
/home/nearonline/mnvdaqrunscripts/start_om_dispatcher.sh

