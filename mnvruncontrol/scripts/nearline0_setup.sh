export LOCALE=NEARLINE
export DIM_DNS_NODE=mnvnearline1.fnal.gov
export UTGID=NEARONLINE

source /work/mnvdaq/setupdaqenv.sh
source /home/nearonline/cmtuser/setup.sh
pushd /work/mnvsoft/v7r2/minerva/MINERVA/MINERVA_v7r2/DaqRecv/cmt
source ./setup.sh
popd

export PATH=/work/python/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/work:$PYTHONPATH

