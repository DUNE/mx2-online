#!/bin/sh

$HOME/mnvdaqrunscripts/remote_nearline_restart.sh
sleep 1
$HOME/mnvdaqrunscripts/allkiller_remote_mnvonline.sh

