#!/bin/sh

gmake clean
gmake

if [ $# -gt 0 ]; then
 if [ $1 == "v" ]; then
  valgrind -v --log-file-exactly=valtest1.txt ./newReadout -c 1 -h 1 -f 4
 fi
else
./newReadout -c 1 -h 1 -f 4
fi

exit 0
