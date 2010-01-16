#!/bin/sh

gmake clean
gmake

if [ $# -gt 0 ]; then
 if [ $1 == "v" ]; then
  valgrind -v --log-file-exactly=valtest1.txt ./logTest
 fi
else
 ./logTest
fi

exit 0
