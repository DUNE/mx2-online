#!/bin/sh

echo "Going to kill all ET processes..."
$HOME/mnvdaqrunscripts/etkiller.pl
echo "Waiting..."
sleep 1
echo "Going to kill the Run Control..."
$HOME/mnvdaqrunscripts/rckiller.pl
echo "Waiting..."
sleep 1
echo "Going to kill the Dispatcher..."
$HOME/mnvdaqrunscripts/rdkiller.pl
echo "Waiting..."
sleep 1

