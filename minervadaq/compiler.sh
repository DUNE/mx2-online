#!/bin/sh

if   [ "$LOCALE" == "WH14TESTSTAND" ]; then
  echo "Setting up Wilson Hall 14 SXO Test stand..."
  cp ${DAQROOT}/options/wh14teststand.opts $DAQROOT/Make.options
elif [ "$LOCALE" == "D0TESTSTAND" ]; then
  echo "Setting up Wilson Hall 14 SXO Test stand..."
  cp ${DAQROOT}/options/d0teststand.opts $DAQROOT/Make.options
else
  hostname=${HOSTNAME/.fnal.gov/}
  if [ -e "${DAQROOT}/options/$hostname.opts" ]; then
    echo "Setting up options for host: $hostname"
    cp "${DAQROOT}/options/$hostname.opts" "${DAQROOT}/Make.options"
  else
    echo "Warning: I don't see a customized .options file in options/ for your hostname: $HOSTNAME.  Using NuMI defaults!" 1>&2;
    echo "If you don't want them, add the file: ${DAQROOT}/options/${hostname}.opts with the right Makefile macros." 1>&2;
    cp ${DAQROOT}/options/numidaq.opts $DAQROOT/Make.options
  fi
fi

pushd ${DAQROOT}/et_9.0/
gmake install
popd

if [ $# -gt 0 ]; then
 gmake all
else
 gmake relink
fi
