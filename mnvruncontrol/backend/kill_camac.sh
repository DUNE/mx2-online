#kill `ps -leaf | grep CAMACDAQ_DR | grep -v grep | awk '{ print $4 }'`
#kill `ps -leaf | grep camacMinerva | grep -v grep | awk '{ print $4 }'`
kill `ps -leaf | grep camac_daq | grep -v grep | awk '{ print $4 }'`