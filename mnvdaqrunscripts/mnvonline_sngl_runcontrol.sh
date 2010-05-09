#!/bin/sh

if test -z "$DAQROOT"
then
	echo "No DAQROOT defined.  Sourcing the setup script..."
	source $HOME/mnvdaqrunscripts/setupdaqenv.sh /work/software/mnvsingle/mnvdaaq
fi

pushd /work/software/mnvruncontrol/frontend
python RunControl.py &
popd
