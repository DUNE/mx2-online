#!/bin/sh

if [[ "$BASH_SOURCE" != "$0" ]]; then
        echo "Don't SOURCE this script; EXECUTE it instead."
        return
fi

script_dir="$( cd "$( dirname "$0" )" && pwd )"

# mnvtbonline0 - Single node DAQ with hardware.  MTest DAQ.
#  (We still need some scripting for the test beam DAQ PC.)
# mnvtbonline1 - Single node DAQ with hardware.  Lab F PMT X-Talk DAQ; MTest Backup DAQ.
if [ $HOSTNAME == "mnvtbonline0.fnal.gov" -o $HOSTNAME == "mnvtbonline1.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $script_dir/runcontrol_single.sh $HOME/runcontrol.sh
	ln -sf $script_dir/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $script_dir/singledaqenv.sh $HOME/singledaqenv.sh
	ln -sf $script_dir/dispatcher_single.sh $HOME/dispatcher.sh
	ln -sf $script_dir/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $script_dir/proc_kill_ALLDAQRC.sh $HOME/kill_all_daqrc.sh
fi

# mnvtbonline2 - Testbeam DAQ with hardware / Testbeam Control room machine / H. Budd's desktop.
# 	Uses "new" wxPython install method - have to use python2.6
if [ $HOSTNAME == "mnvtbonline2.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $script_dir/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $script_dir/runcontrol_multi26.sh $HOME/runcontrol.sh
	ln -sf $script_dir/setupdaqenv.sh $HOME/setupdaqenv.sh
	ln -sf $script_dir/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $script_dir/restart_all_minervatest26.sh $HOME/hard_restart_all.sh
	ln -sf $script_dir/restart_daq_rc_minervatest26.sh $HOME/hard_restart_daq_rc.sh
	ln -sf $script_dir/dispatcher_minervatest_ssh.sh $HOME/hard_restart_dispatchers.sh
fi

# minervatest01 - Single node DAQ with hardware.
#  Not supporting minervatest01 as a MINERvA DAQ PC right now...
if [ $HOSTNAME == "minervatest01.fnal.gov" ]; then
	echo "Not supporting ${HOSTNAME} as a MINERvA DAQ PC right now..."
fi

# minervatest02 - Single & multi-node DAQ with hardware.  WH14 Test Stand DAQ.  (Single & Soldier)
# minervatest04 - Single & multi-node DAQ with hardware.  WH14 Test Stand DAQ.  (Single & Worker)
if [ $HOSTNAME == "minervatest02.fnal.gov" -o $HOSTNAME == "minervatest04.fnal.gov" ]; then
	echo "Setting up generic scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $script_dir/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $script_dir/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $script_dir/proc_kill_ALLDAQRC.sh $HOME/kill_all_daqrc.sh
	ln -sf $script_dir/slowcontrol.sh $HOME/slowcontrol.sh
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $script_dir/dispatcher_multi.sh $HOME/multi_dispatcher.sh
	ln -sf $script_dir/setupdaqenv.sh $HOME/multi_daqenv.sh
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $script_dir/acquisitionmanager_single.sh $HOME/acquisitionmanager.sh
	ln -sf $script_dir/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $script_dir/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $script_dir/singledaqenv.sh $HOME/single_daqenv.sh
fi

# minervatest03 - Multi-node DAQ with no hardware.  WH14 Test Stand DAQ.  (Master)
if [ $HOSTNAME == "minervatest03.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $script_dir/acquisitionmanager_multi.sh $HOME/acquisitionmanager.sh
	ln -sf $script_dir/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $script_dir/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $script_dir/dispatcher_minervatest_ssh.sh $HOME/dispatchers.sh
	ln -sf $script_dir/restart_all_minervatest.sh $HOME/hard_restart_all.sh
	ln -sf $script_dir/restart_daq_rc_minervatest.sh $HOME/hard_restart_daq_rc.sh
	ln -sf $script_dir/runcontrol_multi.sh $HOME/runcontrol.sh
	ln -sf $script_dir/setupdaqenv.sh $HOME/setupdaqenv.sh
fi

# mnvonline0 - Multi-node DAQ with hardware.  MINERvA Online Cluster.  (Single & Soldier)
# mnvonline1 - Multi-node DAQ with hardware.  MINERvA Online Cluster.  (Single & Worker)
# mnvonline2 - Multi-node DAQ with hardware.  MINERvA Online Cluster.  (Backup)
if [ $HOSTNAME == "mnvonline0.fnal.gov" -o $HOSTNAME == "mnvonline1.fnal.gov" -o $HOSTNAME == "mnvonline2.fnal.gov" ]; then
	echo "Setting up generic scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $script_dir/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $script_dir/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $script_dir/proc_kill_ALLDAQRC.sh $HOME/kill_all_daqrc.sh
	ln -sf $script_dir/slowcontrol.sh $HOME/slowcontrol.sh
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $script_dir/dispatcher_multi.sh $HOME/dispatcher.sh
	ln -sf $script_dir/setupdaqenv.sh $HOME/setupdaqenv.sh
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $script_dir/acquisitionmanager_single.sh $HOME/single_acquisitionmanager.sh
	ln -sf $script_dir/dispatcher_single.sh $HOME/single_dispatcher.sh
	ln -sf $script_dir/runcontrol_single.sh $HOME/single_runcontrol.sh
	ln -sf $script_dir/singledaqenv.sh $HOME/single_daqenv.sh
fi

# mnvonlinemaster - Multi-node DAQ with no hardware.  MINERvA Online Cluster.  (Master)
# mnvonlinebck1 - Multi-node DAQ with no hardware.  MINERvA Online Cluster.  (Master Backup)
if [ $HOSTNAME == "mnvonlinemaster.fnal.gov" -o $HOSTNAME == "mnvonlinebck1.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $script_dir/acquisitionmanager_multi.sh $HOME/acquisitionmanager.sh
	ln -sf $script_dir/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $script_dir/configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $script_dir/dispatcher_mnvonline_ssh_local.sh $HOME/dispatchers.sh
	ln -sf $script_dir/restart_all_mnvonline_local.sh $HOME/hard_restart_all.sh
	ln -sf $script_dir/restart_daq_rc_mnvonline_local.sh $HOME/hard_restart_daq_rc.sh
	ln -sf $script_dir/restart_nearline_ssh.sh $HOME/hard_restart_nearline.sh
	ln -sf $script_dir/runcontrol_multi.sh $HOME/runcontrol.sh
	ln -sf $script_dir/runcontrol_multi_soft.sh $HOME/soft_runcontrol.sh
	ln -sf $script_dir/setupdaqenv.sh $HOME/setupdaqenv.sh
fi

# mnvnearline0 - Nearonline (development) machine with no DAQ hardware?
# mnvnearline1 - Nearonline (production) machine with no DAQ hardware.
# mnvonlinebck2 - Nearonline (emergency underground backup) machine with no DAQ hardware.
if [ $HOSTNAME == "mnvnearline1.fnal.gov" -o "$HOSTNAME" == "mnvonlinebck2.fnal.gov" ]; then
	echo "Setting up nearline scripts on ${HOSTNAME}..."
	ln -sf $script_dir/check_nearline_procs.sh $HOME/check_nearline_procs.sh
	ln -sf $script_dir/check_om_log.sh $HOME/check_om_log.sh
	ln -sf $script_dir/dispatcher_nearline.sh $HOME/dispatcher_nearline.sh
	ln -sf $script_dir/configure_cvs_env.sh $HOME/configure_cvs_env.sh
	ln -sf $script_dir/restart_nearline.sh $HOME/hard_restart.sh
fi

# minerva-rc - Main MINERvA Control Room PC in WH12.
# ksmcf-cart.pas.rochester.edu - UROC at Rochester
# uroc.phy.tufts.edu - UROC at Tufts
# uroc.hep.utexas.edu - UROC at Austin
# uroc.fis.utfsm.cl - UROC at USM (Chile)
# uroc.wm.edu - UROC at William & Mary
# uroc.d.umn.edu - UROC at Minnesota

if [ "$HOSTNAME" == "minerva-rc.fnal.gov" -o "$HOSTNAME" == "ksmcf-cart.pas.rochester.edu" -o "$HOSTNAME" == "uroc.phy.tufts.edu" -o "$HOSTNAME" == "uroc.hep.utexas.edu" -o "$HOSTNAME" == "uroc.fis.utfsm.cl" -o "$HOSTNAME" == "uroc.wm.edu" -o "$HOSTNAME" == "uroc.d.umn.edu" ]; then
	echo "Setting up scripts for primary Run Control on ${HOSTNAME}..."
	ln -sf $script_dir/check_daq_rc.sh $HOME/check_daq_rc.sh
	ln -sf $script_dir/whcr_configure_runcontrol.sh $HOME/configure_runcontrol.sh
	ln -sf $script_dir/whcr_restart_all_mnvonline.sh $HOME/hard_restart_all.sh
	ln -sf $script_dir/whcr_restart_daq_rc_mnvonline.sh $HOME/hard_restart_daq_rc.sh
	ln -sf $script_dir/whcr_dispatcher_mnvonline.sh $HOME/hard_restart_dispatchers.sh
	ln -sf $script_dir/whcr_restart_nearline.sh $HOME/hard_restart_monitoring.sh
	ln -sf $script_dir/whcr_runcontrol26.sh $HOME/runcontrol.sh
fi

