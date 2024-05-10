#!/bin/sh
# Use this script to start the Run Series Configurator GUI.

. $DAQROOT/../mnvdaqrunscripts/defs_mx2paths
echo "PYTHONPATH =" $PYTHONPATH
echo "RCROOT =" $RCROOT

# Now, start the Configurator
pushd ${RCROOT}/frontend
which python
python ${RCROOT}/frontend/RunSeriesConfigurator.py &
popd
