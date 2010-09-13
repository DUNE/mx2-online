#!/bin/sh

$HOME/mnvdaqrunscripts/etkiller.pl
sleep 1
$HOME/mnvdaqrunscripts/daqkiller.pl
sleep 1
$HOME/mnvdaqrunscripts/rckiller.pl
sleep 1
$HOME/mnvdaqrunscripts/rdkiller.pl

