#!/bin/sh

$HOME/mnvdaqrunscripts/etkiller.pl >& /dev/null
sleep 1
$HOME/mnvdaqrunscripts/daqkiller.pl >& /dev/null
sleep 1
$HOME/mnvdaqrunscripts/rckiller.pl >& /dev/null
sleep 1
$HOME/mnvdaqrunscripts/rdkiller.pl >& /dev/null

