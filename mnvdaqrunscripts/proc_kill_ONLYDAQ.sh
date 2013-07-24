#!/bin/sh

echo "Going to kill all ET processes..."
$HOME/mnvdaqrunscripts/proc_kill_ET.pl
echo "Waiting..."
sleep 1
echo "Going to kill all DAQ processes..."
$HOME/mnvdaqrunscripts/proc_kill_mnvdaq.pl
echo "Waiting..."
sleep 1

