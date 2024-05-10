#!/bin/sh
#
# Filename: compiler.sh
#
# 11/01/2014 Geoff Savage
# Build file for complete minerva daq.
# Use this the first time you build in an area.
#
# 1. Based on LOCALE or hostname copy the correct file from options
#    to Make.options.  For the SLF6 computer at test beam and
#    underground I am going to use options files based on hostname.
# 2. Build ET.
# 3. Build Everything else.
#
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
    echo "Warning: I don't see a customized .options file in options for your hostname: $hostname.  Using NuMI defaults!" 1>&2;
    echo "If you don't want them, add the file: ${DAQROOT}/options/${hostname}.opts with the right Makefile macros." 1>&2;
    cp ${DAQROOT}/options/numidaq.opts $DAQROOT/Make.options
  fi
fi

# First build et.
# 11/01/2014 Geoff Savage  This is not correct.
# The version of ET to build should be by LOCALE.
pushd ${DAQROOT}/et_16.5/
gmake install
popd

# Build everything else.
if [ $# -gt 0 ]; then
 gmake all
else
 gmake relink
fi
