#!/bin/sh

gmake clean
gmake

if [ $# -gt 0 ]; then
 if [ $1 == "v" ]; then
  valgrind -v --log-file-exactly=valtest1.txt ./newReadout -croc 1 -crim 224 -g
 fi
else
./newReadout -croc 1 -crim 224 -g
fi

exit 0
