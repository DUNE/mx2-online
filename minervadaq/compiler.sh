#!/bin/sh

## single node build
# if [ $DAQROOT == "/work/software/mnvsingle/mnvdaq" ]; then
# 	if [ $HOSTNAME == "mnvtbonline0.fnal.gov" ]; then 
# 		cp ${DAQROOT}/options/mnvtbonline0single.opts $DAQROOT/Make.options
# 	fi
# 	if [ $HOSTNAME == "mnvtbonline1.fnal.gov" ]; then 
# 		cp ${DAQROOT}/options/mnvtbonline1single.opts $DAQROOT/Make.options
# 	fi
# 	if [ $HOSTNAME == "minervatest01.fnal.gov" ]; then 
# 		cp ${DAQROOT}/options/minervatest01single.opts $DAQROOT/Make.options
# 	fi
# 	if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then 
# 		cp ${DAQROOT}/options/minervatest02single.opts $DAQROOT/Make.options
# 	fi
# 	if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then 
# 		cp ${DAQROOT}/options/minervatest04single.opts $DAQROOT/Make.options
# 	fi
# 	if [ $HOSTNAME == "mnvonline0.fnal.gov" ]; then 
# 		cp ${DAQROOT}/options/mnvonline0single.opts $DAQROOT/Make.options
# 	fi
# 	if [ $HOSTNAME == "mnvonline1.fnal.gov" ]; then 
# 		cp ${DAQROOT}/options/mnvonline1single.opts $DAQROOT/Make.options
# 	fi
# fi

## multi node build
# if [ $DAQROOT == "/work/software/mnvonline/mnvdaq" ]; then
#   if [ $HOSTNAME == "minervatest02.fnal.gov" ]; then 
#     cp ${DAQROOT}/options/minervatest02multi.opts $DAQROOT/Make.options
#   fi
#   if [ $HOSTNAME == "minervatest03.fnal.gov" ]; then 
#     cp ${DAQROOT}/options/minervatest03multi.opts $DAQROOT/Make.options
#   fi
#   if [ $HOSTNAME == "minervatest04.fnal.gov" ]; then 
#     cp ${DAQROOT}/options/minervatest04multi.opts $DAQROOT/Make.options
#   fi
#   if [ $HOSTNAME == "mnvonline0.fnal.gov" ]; then 
#     cp ${DAQROOT}/options/mnvonline0multi.opts $DAQROOT/Make.options
#   fi
#   if [ $HOSTNAME == "mnvonline1.fnal.gov" ]; then 
#     cp ${DAQROOT}/options/mnvonline1multi.opts $DAQROOT/Make.options
#   fi
#   if [ $HOSTNAME == "mnvonline2.fnal.gov" ]; then 
#     cp ${DAQROOT}/options/mnvonline2crate0multi.opts $DAQROOT/Make.options   # Replace mnvonline0
#     cp ${DAQROOT}/options/mnvonline2crate1multi.opts $DAQROOT/Make.options   # Replace mnvonline1
#   fi
#   if [ $HOSTNAME == "mnvonlinemaster.fnal.gov" ]; then 
#     cp ${DAQROOT}/options/mnvonlinemastermulti.opts $DAQROOT/Make.options
#   fi
#   if [ $HOSTNAME == "mnvonlinebck1.fnal.gov" ]; then 
#     cp ${DAQROOT}/options/mnvonlinebck1multi.opts $DAQROOT/Make.options
#   fi
# fi

# nearline builds (always multi node)
if [ "$HOSTNAME" == "mnvnearlinelogger.fnal.gov" ]; then
  cp ${DAQROOT}/options/mnvnearlinelogger.opts $DAQROOT/Make.options
fi

 pushd ${DAQROOT}/et_9.0/
 gmake install
 popd

 if [ $# -gt 0 ]; then
   gmake all
 else
   gmake relink
 fi

# if [ $HOSTNAME == "mnvonline2.fnal.gov" ]; then 
#   echo " --- PLEASE NOTE! ---- "
#   echo " You are building a back-up node that can be used for either VME hardware crate! "
#   echo " Please check the compiler script to be sure you are set-up for the right hardware "
#   echo " configuration.  Edit as needed (should be as simple as commenting out a line) and "
#   echo " recompile as needed. "
# fi



