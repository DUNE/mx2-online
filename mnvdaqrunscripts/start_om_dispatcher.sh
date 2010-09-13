export LOCALE=NEARLINE
export DIM_DNS_NODE=mnvnearline1.fnal.gov
export UTGID=NEARONLINE

export SOFTREL=v7r6

source /scratch/nearonline/mnvdaq/setupdaqenv.sh

#### ATTENTION: this script needs to be updated for new framework versions!!!
source /scratch/nearonline/software_releases/${SOFTREL}/setup.sh ${SOFTREL} /scratch/nearonline/software_releases/${SOFTREL}
pushd /home/nearonline/cmtuser/Minerva_${SOFTREL}/DaqRecv/cmt/
source ./setup.sh
popd

export PATH=/scratch/nearonline/python/bin:$PATH		# newer version of Python
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH		# for log4cpp
export PYTHONPATH=/scratch/nearonline:$PYTHONPATH		# so that mnvruncontrol shows up as a package in Python


#  The following lines kill any old dispatchers, 
#  clear any leftover subprocesses, and start a new dispatcher.

# first, find out if there are any leftover processes.
# if there are, they will have the same session ID as the dispatcher.
if [ -e "/tmp/om_dispatcher.pid" ]; then
	dispatcher_pid=$(cat /tmp/om_dispatcher.pid)
	processes=$(ps --sid $(ps -o sid $dispatcher_pid | grep -oE "[[:digit:]]+") -o pid | grep -oE "[[:digit:]]+")
fi

pushd /scratch/nearonline/mnvruncontrol/backend
#python ./MonitorDispatcher.py stop		# first clear any old copies  

# kill all processes in the same process group as the dispatcher.
# this should prevent any leftover processes from hanging on to the socket.
if [ -n "$processes" ]; then
	for process in $processes
	do
		# if this is still alive (determined by sending signal 0),
		# kill it.
		kill -s 0 $process > /dev/null 2>&1
	        if [ $? -eq 0 ]; then
        	        echo $process
	        fi
	done
fi
# stop the dispatcher if it's still going
python ./MonitorDispatcher.py stop
# now start a fresh dispatcher.
python ./MonitorDispatcher.py start
popd
