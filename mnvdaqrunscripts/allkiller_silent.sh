#!/bin/sh

$HOME/mnvdaqrunscripts/proc_kill_ET.pl >& /dev/null
sleep 1
$HOME/mnvdaqrunscripts/proc_kill_mnvdaq.pl >& /dev/null
sleep 1
$HOME/mnvdaqrunscripts/proc_kill_RunCo.pl >& /dev/null
sleep 1
$HOME/mnvdaqrunscripts/proc_kill_ReadDisp.pl >& /dev/null
sleep 1

