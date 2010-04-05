export LOCALE=NEARLINE
export DIM_DNS_NODE=mnvnearline1.fnal.gov
export UTGID=NEARONLINE

source /scratch/nearonline/mnvdaq/setupdaqenv.sh
source /home/nearonline/cmtuser/setup.sh
pushd /scratch/nearonline/software_releases/v7r2/minerva/MINERVA/MINERVA_v7r2/DaqRecv/cmt
source ./setup.sh
popd

export PATH=/scratch/nearonline/python/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/scratch/nearonline:$PYTHONPATH

