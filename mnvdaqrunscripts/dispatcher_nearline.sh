#!/bin/sh

source /scratch/nearonline/mirror/mnvdaq/setupdaqenv.sh

# set up the MINERvA framework & condor, then the DaqRecv package
source $HOME/scripts/setup_nearline_software.sh 
pushd /home/nearonline/cmtuser/Minerva_${MINERVA_RELEASE}/Tools/DaqRecv/cmt/ >& /dev/null
source ./setup.sh
popd >& /dev/null

export PATH=/scratch/nearonline/mirror/python/bin:$PATH     # newer version of Python
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH      # for log4cpp
export PYTHONPATH=/scratch/nearonline/mirror:$PYTHONPATH    # so that mnvruncontrol shows up as a package in Python


#  The following lines kill any old dispatchers, 
#  clear any leftover subprocesses, and start a new dispatcher.

# is there still a dispatcher going?
if [ -e "/tmp/om_dispatcher.pid" ]; then
	dispatcher_pid=$(cat /tmp/om_dispatcher.pid)
fi

# stop the dispatcher if it's still going
pushd /scratch/nearonline/mirror/mnvruncontrol/backend
python ./MonitorDispatcher.py stop

# check -- did it REALLY stop?
# if not, force the issue.
if `kill -0 $dispatcher_pid`; then
	kill -9 $dispatcher_pid
fi

# now start a fresh dispatcher.
python ./MonitorDispatcher.py start
popd
