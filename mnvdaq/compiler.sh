#!/bin/sh

# single node build
if [ $DAQROOT == "/work/software/mnvsingle/mnvdaq" ]; then
	if [ $HOSTNAME == "mnvtbonline0.fnal.gov" ]; then 
		cp ${DAQROOT}/options/mnvtbonline0single.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "mnvtbonline1.fnal.gov" ]; then 
		cp ${DAQROOT}/options/mnvtbonline1single.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "minervatest01.fnal.gov" ]; then 
		cp ${DAQROOT}/options/minervatest01single.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then 
		cp ${DAQROOT}/options/minervatest02single.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then 
		cp ${DAQROOT}/options/minervatest04single.opts $DAQROOT/Make.options
	fi
fi

# multi node build
if [ $DAQROOT == "/work/software/mnvonline/mnvdaq" ]; then
	if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then 
		cp ${DAQROOT}/options/minervatest02multi.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "minervatest03.fnal.gov" ]; then 
		cp ${DAQROOT}/options/minervatest03multi.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then 
		cp ${DAQROOT}/options/minervatest04multi.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "mnvonline0.fnal.gov" ]; then 
		cp ${DAQROOT}/options/mnvonline0multi.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "mnvonline1.fnal.gov" ]; then 
		cp ${DAQROOT}/options/mnvonline1multi.opts $DAQROOT/Make.options
	fi
	if [ $HOSTNAME == "mnvonlinemaster.fnal.gov" ]; then 
		cp ${DAQROOT}/options/mnvonlinemastermulti.opts $DAQROOT/Make.options
	fi
fi

# nearline builds (always multi node)
if [ $HOSTNAME == "mnvnearline0.fnal.gov" ]; then 
	cp ${DAQROOT}/options/mnvnearline0.opts $DAQROOT/Make.options
elif [ "$HOSTNAME" == "mnvnearline1.fnal.gov" ]; then
	cp ${DAQROOT}/options/mnvnearline1.opts $DAQROOT/Make.options
fi

if [ $# -gt 0 ]; then
	gmake all
else
	gmake relink
fi