#!/bin/sh

gmake clean
gmake
rm /work/data/logs/newReadout.txt

#WH14B
#./newReadout -crim 224 -g
./newReadout -crim 224 

