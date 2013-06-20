#!/bin/sh

# Default to NuMI Setup
cp ${DAQROOT}/options/numidaq.opts $DAQROOT/Make.options

if   [ $LOCALE == "WH14TESTSTAND" ]; then
  echo "Setting up Wilson Hall 14 SXO Test stand..."
  cp ${DAQROOT}/options/wh14teststand.opts $DAQROOT/Make.options
elif [ $LOCALE == "D0TESTSTAND" ]; then
  echo "Setting up Wilson Hall 14 SXO Test stand..."
  cp ${DAQROOT}/options/d0teststand.opts $DAQROOT/Make.options
fi

# nearline builds 
if [ "$HOSTNAME" == "mnvonlinelogger.fnal.gov" ]; then
  cp ${DAQROOT}/options/mnvonlinelogger.opts $DAQROOT/Make.options
fi

 pushd ${DAQROOT}/et_9.0/
 gmake install
 popd

 if [ $# -gt 0 ]; then
   gmake all
 else
   gmake relink
 fi




