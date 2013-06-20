#!/bin/sh

hostname=${HOSTNAME/.fnal.gov/}
if [ -e "${DAQROOT}/options/$hostname.opts" ]; then
  cp "${DAQROOT}/options/$hostname.opts" "${DAQROOT}/Make.options"
else
  echo "Warning: I don't see a customized .options file in options/ for your hostname: $HOSTNAME.  You'll get the defaults in Make.options!" 1>&2;
  echo "If you don't want them, add the file: ${DAQROOT}/options/${hostname}.opts with the right Makefile macros."
fi

 pushd ${DAQROOT}/et_9.0/
 gmake install
 popd

 if [ $# -gt 0 ]; then
   gmake all
 else
   gmake relink
 fi
