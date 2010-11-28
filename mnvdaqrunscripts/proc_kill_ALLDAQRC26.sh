#!/bin/sh

echo "Going to kill all ET processes..."
$HOME/mnvdaqrunscripts/proc_kill_ET.pl
echo "Waiting..."
sleep 1
echo "Going to kill all DAQ processes..."
$HOME/mnvdaqrunscripts/proc_kill_mnvdaq.pl
echo "Waiting..."
sleep 1
echo "Going to kill the Run Control..."
$HOME/mnvdaqrunscripts/proc_kill_RunCo26.pl
echo "Waiting..."
sleep 1
echo "Going to kill the Dispatcher..."
$HOME/mnvdaqrunscripts/proc_kill_ReadDisp.pl
echo "Waiting..."
sleep 1
echo "Going to kill the AcquisitionManager..."
$HOME/mnvdaqrunscripts/proc_kill_AcqMan26.pl
echo "Waiting..."
sleep 1

