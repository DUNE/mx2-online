export LOCALE=NEARLINE
export DIM_DNS_NODE=mnvnearline1.fnal.gov

#### ATTENTION: this script needs to be updated for new framework versions!!!

source /scratch/nearonline/mnvdaq/setupdaqenv.sh
source /home/nearonline/cmtuser/setup.sh		# do this from /scratch/nearonline
#pushd /scratch/nearonline/software_releases/v7r2/minerva/MINERVA/MINERVA_v7r2/DaqRecv/cmt
source /scratch/nearonline/software_releases/v7r2/setup.sh

pushd /home/nearonline/cmtuser/Minerva_v7r2/DaqRecv/cmt/
source ./setup.sh
popd

export PATH=/scratch/nearonline/python/bin:$PATH		# newer version of Python
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH		# for log4cpp
export PYTHONPATH=/scratch/nearonline:$PYTHONPATH		# so that mnvruncontrol shows up as a package in Python

# start the dispatcher here.
