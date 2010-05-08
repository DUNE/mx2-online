#!/bin/sh

gmake clean
gmake
rm /work/data/logs/newReadout.txt

#WH14B
#./newReadout -croc 1 -crim 224 -g
./newReadout -croc 1 -crim 224 

