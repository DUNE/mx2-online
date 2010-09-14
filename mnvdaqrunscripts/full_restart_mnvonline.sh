#!/bin/sh

echo "Logging onto mnvnearline1 and killing and restarting all nearline processes!"
$HOME/mnvdaqrunscripts/remote_nearline_restart.sh
sleep 1
echo "Killing and restarting all DAQ processes on the mnvonline cluster!" 
$HOME/mnvdaqrunscripts/allkiller_remote_mnvonline.sh

