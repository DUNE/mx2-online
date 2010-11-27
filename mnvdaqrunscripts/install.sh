#!/bin/sh


# mnvtbonline0 - Single node DAQ with hardware.  MTest DAQ.
#  (We still need some scripting for the test beam DAQ PC.)
# mnvtbonline1 - Single node DAQ with hardware.  Lab F PMT X-Talk DAQ; MTest Backup DAQ.
if [ $HOSTNAME == "mnvtbonline0.fnal.gov" -o $HOSTNAME == "mnvtbonline1.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/singledaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/proc_kill_ALLDAQRC.sh $HOME/kill_all_daqrc.sh
fi

# mnvtbonline2 - Testbeam DAQ with hardware / Testbeam Control room machine / H. Budd's desktop.
# 	Uses "new" wxPython install method - have to use python2.6
if [ $HOSTNAME == "mnvtbonline2.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_multi26.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/acquistionmanager_multi26.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_all_minervatest26.sh $HOME/hard_restart_all.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_daq_rc_minervatest26.sh $HOME/hard_restart_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_minervatest_ssh.sh $HOME/hard_restart_dispatchers.sh
fi

# minervatest01 - Single node DAQ with hardware.
#  Not supporting minervatest01 as a MINERvA DAQ PC right now...
if [ $HOSTNAME == "minervatest01.fnal.gov" ]; then
	echo "Not supporting ${HOSTNAME} as a MINERvA DAQ PC right now..."
fi

# minervatest02 - Single & multi-node DAQ with hardware.  WH14 Test Stand DAQ.  (Single & Soldier)
# minervatest04 - Single & multi-node DAQ with hardware.  WH14 Test Stand DAQ.  (Single & Worker)
if [ $HOSTNAME == "minervatest02.fnal.gov" -o $HOSTNAME == "minervatest04.fnal.gov" ]; then
	echo "Setting up single and multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/acquistionmanager_single.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/multi_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_multi.sh $HOME/multi_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/proc_kill_ALLDAQRC.sh $HOME/kill_all_daqrc.sh
fi

# minervatest03 - Multi-node DAQ with no hardware.  WH14 Test Stand DAQ.  (Master)
if [ $HOSTNAME == "minervatest03.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_multi.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/acquistionmanager_multi.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_all_minervatest.sh $HOME/hard_restart_all.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_daq_rc_minervatest.sh $HOME/hard_restart_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_minervatest_ssh.sh $HOME/hard_restart_dispatchers.sh
fi

# mnvonline0 - Multi-node DAQ with hardware.  MINERvA Online Cluster.  (Single & Soldier)
# mnvonline1 - Multi-node DAQ with hardware.  MINERvA Online Cluster.  (Single & Worker)
# mnvonline2 - Multi-node DAQ with hardware.  MINERvA Online Cluster.  (Backup)
if [ $HOSTNAME == "mnvonline0.fnal.gov" -o $HOSTNAME == "mnvonline1.fnal.gov" -o $HOSTNAME == "mnvonline2.fnal.gov" ]; then
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_multi.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/proc_kill_ALLDAQRC.sh $HOME/kill_all_daqrc.sh
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/acquistionmanager_single.sh $HOME/single_acquistionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
fi

# mnvonlinemaster - Multi-node DAQ with no hardware.  MINERvA Online Cluster.  (Master)
# mnvonlinebck1 - Multi-node DAQ with no hardware.  MINERvA Online Cluster.  (Master Backup)
if [ $HOSTNAME == "mnvonlinemaster.fnal.gov" -o $HOSTNAME == "mnvonlinebck1.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/runcontrol_multi.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_daq_rc_mnvonline.sh $HOME/hard_restart_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_nearline_ssh.sh $HOME/hard_restart_nearline.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_all_mnvonline.sh $HOME/hard_restart_all.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_multi.sh $HOME/hard_restart_dispatchers.sh
fi

# mnvnearline0 - Nearonline (development) machine with no DAQ hardware?
# mnvnearline1 - Nearonline (production) machine with no DAQ hardware.
if [ $HOSTNAME == "mnvnearline1.fnal.gov" ]; then
	echo "Setting up nearline scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/check_nearline_procs.sh $HOME/check_nearline_procs.sh
	ln -sf $HOME/mnvdaqrunscripts/check_om_log.sh $HOME/check_om_log.sh
	ln -sf $HOME/mnvdaqrunscripts/dispatcher_nearline.sh $HOME/dispatcher_nearline.sh
#	ln -sf $HOME/mnvdaqrunscripts/find_om_processes.sh $HOME/find_om_processes.sh # In attic.
	ln -sf $HOME/mnvdaqrunscripts/configure_cvs_env.sh $HOME/configure_cvs_env.sh
	ln -sf $HOME/mnvdaqrunscripts/restart_nearline.sh $HOME/hard_restart.sh
fi

# minerva-rc - Main MINERvA Control Room PC in WH12.
if [ $HOSTNAME == "minerva-rc.fnal.gov" ]; then
	echo "Setting up scripts for primary Run Control on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/whcr_acquistionmanager26.sh $HOME/acquisitionmanager.sh
	ln -sf $HOME/mnvdaqrunscripts/whcr_configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/whcr_dispatcher_mnvonline.sh $HOME/hard_restart_dispatchers.sh
	ln -sf $HOME/mnvdaqrunscripts/whcr_runcontrol26.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $HOME/mnvdaqrunscripts/whcr_restart_all_mnvonline.sh $HOME/hard_restart_all.sh
	ln -sf $HOME/mnvdaqrunscripts/whcr_restart_nearline.sh $HOME/hard_restart_monitoring.sh
fi

