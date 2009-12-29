#!/bin/sh

gmake clean
gmake

if [ $# -gt 0 ]; then
 if [ $1 == "v" ]; then
  valgrind -v --log-file-exactly=valtest1.txt ./lightLeakConfig -c 1
 fi
else
./lightLeakConfig -c 1
fi

exit 0
