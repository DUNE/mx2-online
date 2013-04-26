#!/bin/sh

export LOCALE=FNAL

SETUP_DIR=`dirname ${BASH_SOURCE[0]}`
export DAQROOT=`readlink -f ${SETUP_DIR}`
export DAQROOT=${HOME}/minervadaq/minervadaq
export DAQSCRIPT=${DAQROOT}/setupdaqenv.sh
source $DAQSCRIPT $DAQROOT
