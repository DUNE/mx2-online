#!/bin/sh

# mnvtbonline0 - Single node DAQ with hardware.
if [ $HOSTNAME == "mnvtbonline0.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/singleruncontrol.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/singledaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/singledispatcher.sh $HOME/dispatcher.sh
fi

# minervatest01 - Single node DAQ with hardware.
if [ $HOSTNAME == "minervatest01.fnal.gov" ]; then
	echo "Setting up single node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/singleruncontrol.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/singledaqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/singledispatcher.sh $HOME/dispatcher.sh
fi

# minervatest02 - Single & multi-node DAQ with hardware.  
if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then
	echo "Setting up single and multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/singleruncontrol.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/singledispatcher.sh $HOME/single_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/multi_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/multidispatcher.sh $HOME/multi_dispatcher.sh
fi

# minervatest03 - Multi-node DAQ with no hardware.
if [ $HOSTNAME == "minervatest03.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/multiruncontrol.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
fi

# minervatest04 - Single & multi-node DAQ with hardware. 
if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then
	echo "Setting up single and multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/singleruncontrol.sh $HOME/single_runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/multidispatcher.sh $HOME/multi_dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/singledaqenv.sh $HOME/single_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/multi_daqenv.sh
	ln -sf $HOME/mnvdaqrunscripts/singledispatcher.sh $HOME/single_dispatcher.sh
fi

# mnvonline0 - Multi-node DAQ with hardware.  
if [ $HOSTNAME == "mnvonline0.fnal.gov" ]; then
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/multidispatcher.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
fi

# mnvonline1 - Multi-node DAQ with hardware.  
if [ $HOSTNAME == "mnvonline1.fnal.gov" ]; then
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/multidispatcher.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
fi

# mnvonline2 - Multi-node DAQ with hardware.  
if [ $HOSTNAME == "mnvonline2.fnal.gov" ]; then
	echo "Setting up multi-node scripts (with hardware) on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/multidispatcher.sh $HOME/dispatcher.sh
	ln -sf $HOME/mnvdaqrunscripts/slowcontrol.sh $HOME/slowcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
fi

# mnvonlinemaster - Multi-node DAQ with no hardware.
if [ $HOSTNAME == "mnvonlinemaster.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/multiruncontrol.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
fi

# mnvonlinebck1 - Multi-node DAQ with no hardware.
if [ $HOSTNAME == "mnvonlinebck1.fnal.gov" ]; then
	echo "Setting up multi-node scripts on ${HOSTNAME}..."
	ln -sf $HOME/mnvdaqrunscripts/multiruncontrol.sh $HOME/runcontrol.sh
	ln -sf $HOME/mnvdaqrunscripts/setupdaqenv.sh $HOME/setupdaqenv.sh
fi



