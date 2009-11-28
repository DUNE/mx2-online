#!/bin/sh

make clean
make

if [ $# -gt 0 ]; then
 if [ $1 == "v" ]; then
  valgrind -v --log-file-exactly=valtest1.txt ./chginjlog
 fi
else
./chginjlog
fi

exit 0
