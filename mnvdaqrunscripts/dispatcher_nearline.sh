#!/bin/sh

# sets up all the various pieces of software 
source $HOME/scripts/setup_nearline_software.sh 

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