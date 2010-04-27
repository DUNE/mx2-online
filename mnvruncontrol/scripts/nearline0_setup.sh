export LOCALE=NEARLINE
export DIM_DNS_NODE=mnvnearline1.fnal.gov

source /work/mnvdaq/setupdaqenv.sh
source /home/nearonline/cmtuser/setup.sh
pushd /home/nearonline/cmtuser/Minerva_v7r2/DaqRecv/cmt/
source ./setup.sh
popd

export PATH=/work/python/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/work:$PYTHONPATH
export CORAL_AUTH_PATH=/home/nearonline/private
export DIM_DNS_NODE=localhost
