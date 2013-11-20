#!/bin/sh
echo "croce_daqenv.sh"
pushd /work/software/croce/minervadaq/minervadaq >& /dev/null
source setupdaqenv.sh
# source setupdaqenv.sh # what is going on...
# source setup.sh # once we upgrade to ET 12, etc.
popd >& /dev/null

