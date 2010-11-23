#!/bin/sh


# mnvtbonline0 - Single node DAQ with hardware.
if [ $HOSTNAME == "mnvtbonline0.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/singledaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/allkiller.sh $HOME/allkiller.sh
fi

# mnvtbonline1 - Single node DAQ with hardware.
if [ $HOSTNAME == "mnvtbonline1.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/singledaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/dispatcher.sh
fi

# mnvtbonline2 - Testbeam DAQ with hardware / Testbeam Control room machine / H. Budd's desktop.
# 	Uses "new" wxPython install method - have to use python2.6
if [ $HOSTNAME == "mnvtbonline2.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/rcc26.sh $HOME/rcc.sh
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_multi26.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/acquistionmanager_multi26.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/remote_restart_all_multi_minervatest.sh $HOME/hard_daq_restart.sh
	ln -sf $HOME/mnvdaqrunscripts/remote_minervatest_dispatcher_restart_hard.sh $HOME/hard_dispatcher_restart.sh
	ln -sf $HOME/mnvdaqrunscripts/remote_minervatest_dispatcher_restart_soft.sh $HOME/soft_dispatcher_restart.sh
fi

# minervatest01 - Single node DAQ with hardware.
#  Not supporting minervatest01 as a MINERvA DAQ PC right now...
if [ $HOSTNAME == "minervatest01.fnal.gov" ]; then
	echo "Not supporting minervatest01 as a MINERvA DAQ PC right now..."
#	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
#	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/runcontrol.sh
#	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
#	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/singledaqenv.sh
#	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/dispatcher.sh
#	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
#	ln -sf $HOME/mnvdaqrunscripts/allkiller.sh $HOME/allkiller.sh
fi

# minervatest02 - Single & multi-node DAQ with hardware.  
if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then
	echo "Setting up single and multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/acquistionmanager_single.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/multi_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_multi.sh $HOME/multi_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/allkiller.sh $HOME/allkiller.sh
	ln -sf $HOME/mnvdaqrunscripts/singleacquisitionmanager.sh $HOME/acquisitionmanager.sh
fi

# minervatest03 - Multi-node DAQ with no hardware.
if [ $HOSTNAME == "minervatest03.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_multi.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/acquistionmanager_multi.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_all_multi_minervatest.sh $HOME/hard_daq_restart.sh
	ln -sf $HOME/mnvdaqrunscripts/remote_minervatest_dispatcher_restart_hard.sh $HOME/hard_dispatcher_restart.sh
	ln -sf $HOME/mnvdaqrunscripts/remote_minervatest_dispatcher_restart_soft.sh $HOME/soft_dispatcher_restart.sh
fi

# minervatest04 - Single & multi-node DAQ with hardware. 
if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then
	echo "Setting up single and multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/acquistionmanager_single.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_multi.sh $HOME/multi_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/multi_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/allkiller.sh $HOME/allkiller.sh
	ln -sf $HOME/mnvdaqrunscripts/singleacquisitionmanager.sh $HOME/acquisitionmanager.sh
fi

# mnvonline0 - Multi-node DAQ with hardware.  
# Also single node now.
if [ $HOSTNAME == "mnvonline0.fnal.gov" ]; then
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_multi.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/allkiller.sh $HOME/allkiller.sh
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
fi

# mnvonline1 - Multi-node DAQ with hardware.  
# Also single node now.
if [ $HOSTNAME == "mnvonline1.fnal.gov" ]; then
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_multi.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/allkiller.sh $HOME/allkiller.sh
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
fi

# mnvonline2 - Multi-node DAQ with hardware.  
if [ $HOSTNAME == "mnvonline2.fnal.gov" ]; then
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_multi.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/allkiller.sh $HOME/allkiller.sh
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
fi

# minerva-rc - Main MINERvA Control Room PC in WH12.
if [ $HOSTNAME == "minerva-rc.fnal.gov" ]; then
	echo "Setting up scripts for primary Run Control on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/whcr_dispatcher_restart_hard_mnvonline.sh $HOME/dispatcher_restart.sh
	ln -sf $HOME/mnvdaqrunscripts/whcr_runcontrol26.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/whcr_acquistionmanager26.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh

	ln -sf $HOME/mnvdaqrunscripts/restart_all_multi_mnvonline.sh $HOME/hard_restart_daq.sh
	ln -sf $HOME/mnvdaqrunscripts/remote_nearline_restart.sh $HOME/hard_restart_monitoring.sh
	ln -sf $HOME/mnvdaqrunscripts/whcr_allkiller_mnvonline26.sh $HOME/hard_restart_all.sh

fi

# mnvonlinemaster - Multi-node DAQ with no hardware.
if [ $HOSTNAME == "mnvonlinemaster.fnal.gov" -o $HOSTNAME == "mnvonlinebck1.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_multi.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_all_multi_mnvonline.sh $HOME/hard_daq_restart.sh
	ln -sf $HOME/mnvdaqrunscripts/remote_nearline_restart.sh $HOME/hard_nearline_restart.sh
	ln -sf $HOME/mnvdaqrunscripts/full_restart_mnvonline.sh $HOME/hard_restart.sh
	ln -sf $HOME/mnvdaqrunscripts/remote_mnvonline_dispatcher_restart_hard.sh $HOME/dispatcher_restart.sh
#	ln -sf $HOME/mnvdaqrunscripts/remote_mnvonline_dispatcher_restart_soft.sh $HOME/soft_dispatcher_restart.sh
fi

# mnvonlinebck1 - Multi-node DAQ with no hardware.
#if [ $HOSTNAME == "mnvonlinebck1.fnal.gov" ]; then
#	echo "Setting up multi-node scripts on ${HOSTNAME}..."
#	ln -sf $HOME/mnvdaqrunscripts/runcontrol_multi.sh $HOME/runcontrol.sh
#	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
#	ln -sf $HOME/mnvdaqrunscripts/runcheck.sh $HOME/runcheck.sh
#	ln -sf $HOME/mnvdaqrunscripts/allkiller.sh $HOME/allkiller.sh
#fi

# mnvnearline1 - Nearonline machine with no DAQ hardware.
if [ $HOSTNAME == "mnvnearline1.fnal.gov" ]; then
	echo "Setting up nearline scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/check_dispatcher.sh $HOME/check_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/om_log_check.sh $HOME/om_log_check.sh
	ln -sf $HOME/mnvdaqrunscripts/start_om_dispatcher.sh $HOME/start_om_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/find_om_processes.sh $HOME/find_om_processes.sh
	ln -sf $HOME/mnvdaqrunscripts/nearlinekiller.pl $HOME/kill_all.pl
	ln -sf $HOME/mnvdaqrunscripts/cvs_setup.sh $HOME/cvs_setup.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_all_nearline.sh $HOME/hard_restart.sh
fi



