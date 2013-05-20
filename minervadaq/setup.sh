#!/bin/sh

export LOCALE=FNAL

SETUP_DIR=`dirname ${BASH_SOURCE[0]}`
export DAQROOT=`readlink -f ${SETUP_DIR}`
export DAQSCRIPT=${DAQROOT}/setupdaqenv.sh
export CODA_HOME=${DAQROOT}/et-12.0
source $DAQSCRIPT $DAQROOT
