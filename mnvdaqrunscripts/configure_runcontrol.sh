#!/bin/sh

echo "PYTHONPATH =" $PYTHONPATH
echo "RCROOT =" $RCROOT

# Use this script to start the Run Control Configurator GUI.

. $DAQROOT/../mnvdaqrunscripts/defs_mx2paths

# Now, start the Configurator
pushd ${RCROOT}/frontend
echo "PYTHONPATH =" $PYTHONPATH
which python
python  ${RCROOT}/frontend/RunControlConfiguration.py &
popd
