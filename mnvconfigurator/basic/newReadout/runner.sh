#!/bin/sh

gmake clean
gmake
rm /work/data/logs/newReadout.txt

#WH14B
./newReadout -c 1 -h 1 -f 4

