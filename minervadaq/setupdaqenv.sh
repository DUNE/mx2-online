#
# Filename: setupminervadaq.sh
#
# Specify the versions of software packages and their locations.
#
# Note, to compile the DAQ, after you pull the package down from CVS, you need to untar the ET code first!
# Set your LOCALE.  One Valid choice right now: "FNAL" for Fermilab.  Currently on the FNAL mnvonline
# machines, the LOCALE is set in the mnvonline user .bash_profile.
#
# Usage: source setupminervadaq.sh (set LOCALE environment variable first)
#
# Recognized LOCALE values:
# 1. FNAL - SLF5 underground DAQ computers, runs daq and event builder
# 2. NEARLINE - SLF5 underground computer that needs to run the event builder
# 3. NEARLINEDEV - SLF5 nearline development computer
# 4. FNAL2 - SLF6 underground and test beam DAQ computers
# 5. D0TESTSTAND - SLF6 DAQ development
# 6. WHTESTSTAND - SLF5 DAQ and electronics development 
# 7. LabF - Lab F Test Stand
# 8. Mx2 - MINERvA for 2x2 development
#

echo ---------------------------------------------------------------------------
echo Welcome to the MINERvA DAQ Software Environment.
echo
echo Your LOCALE is $LOCALE
echo ---------------------------------------------------------------------------

if [ $LOCALE == "FNAL" ]; then
  echo "Setting up FNAL..."
  export DAQROOT=/work/software/croce/minervadaq/minervadaq
  export CODA_VERSION=et_9.0
  export CODA_HOME=${DAQROOT}/${CODA_VERSION}
  export BMS_HOME=${CODA_HOME}/BMS
  export ET_HOME=${CODA_HOME}/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  export INSTALL_DIR=$ET_HOME
  export CAEN_DIR=/work/software/CAENVMElib
  export CAEN_VERSION=CAEN_2_7
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
  # Add local SQLite
  export LD_LIBRARY_PATH=$DAQROOT/sqlite/lib:$LD_LIBRARY_PATH
  export PATH=$DAQROOT/sqlite/bin:$PATH
  # Add /usr/local/lib for log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
elif [ $LOCALE == "NEARLINE" ]; then
  export DAQROOT=/scratch/nearonline/mirror/minervadaq-croce/minervadaq
  export CAEN_DIR=/scratch/nearonline/mirror/CAENVMElib
  export CAEN_VERSION=CAEN_2_7
  export CODA_VERSION=et_9.0
  export CODA_HOME=${DAQROOT}/${CODA_VERSION}
  export BMS_HOME=${CODA_HOME}/BMS
  export ET_HOME=${CODA_HOME}/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  export INSTALL_DIR=$ET_HOME
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
  # Add log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/scratch/nearonline/mirror/log4cpp/lib
elif [ $LOCALE == "NEARLINEDEV" ]; then
  export DAQROOT=/work/mnvdaq
  export CAEN_DIR=/work/CAENVMElib
  export CAEN_VERSION=CAEN_2_7
  export CODA_VERSION=et_9.0
  export CODA_HOME=${DAQROOT}/${CODA_VERSION}
  export BMS_HOME=${CODA_HOME}/BMS
  export ET_HOME=${CODA_HOME}/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  export INSTALL_DIR=$ET_HOME
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x64/:$LD_LIBRARY_PATH
  # Add log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/work/log4cpp/lib
elif [ $LOCALE == "FNAL2" ]; then
  export DAQROOT=/work/software/croce_mtest_labf/minervadaq/minervadaq
  export CAEN_DIR=/work/software/CAENVMElib
  export CAEN_VERSION=CAEN_2_30
  export CODA_VERSION=et_9.0
  export CODA_HOME=${DAQROOT}/${CODA_VERSION}
  export BMS_HOME=${CODA_HOME}/BMS
  export ET_HOME=${CODA_HOME}/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  export INSTALL_DIR=$ET_HOME
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
  # Add log4cpp support.
  #export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/work/log4cpp/lib
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/lib64
elif [ $LOCALE == "D0TESTSTAND" ]; then
  #export DAQROOT=/work/mnvdaq
  setup caenvme
  export CAEN_DIR=$CAENVME_DIR
  export CAEN_VERSION=CAEN_2_30
  export CODA_VERSION=et_9.0
  export CODA_HOME=${DAQROOT}/${CODA_VERSION}
  export BMS_HOME=${CODA_HOME}/BMS
  export ET_HOME=${CODA_HOME}/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  export INSTALL_DIR=$ET_HOME
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
  # Add log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/work/log4cpp/lib
elif [ $LOCALE == "WH14TESTSTAND" ]; then
  SETUP_DIR=`dirname ${BASH_SOURCE[0]}`
  export DAQROOT=`readlink -f ${SETUP_DIR}`
  export CODA_VERSION=et_9.0
  export CODA_HOME=${DAQROOT}/${CODA_VERSION}
  export BMS_HOME=${CODA_HOME}/BMS
  export ET_HOME=${CODA_HOME}/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  export INSTALL_DIR=$ET_HOME
  export CAEN_VERSION=CAEN_2_7
  export CAEN_DIR=/work/software/CAENVMElib
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
  # Add local SQLite
  export LD_LIBRARY_PATH=$DAQROOT/sqlite/lib:$LD_LIBRARY_PATH
  export PATH=$DAQROOT/sqlite/bin:$PATH
  # Add /usr/local/lib for log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
elif [ $LOCALE == "LabF" ]; then
  #Locale for Lab F minerva acd-mnv03 test stand 
  export DAQROOT=/work/software/mx2daq/minervadaq
  export CAEN_DIR=/work/software/CAENVMELib-v4.0.2
  export CAEN_VERSION=CAEN_3_4_4 # Unnecessary
  export CODA_VERSION=et_16.5
  export CODA_HOME=${DAQROOT}/${CODA_VERSION}
  export ET_HOME=${CODA_HOME}/build
  export ET_FILES=$ET_HOME
  export ET_LIBROOT=$ET_HOME
  export INSTALL_DIR=$ET_HOME
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries and log4cpp support
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DAQROOT/lib:$ET_LIBROOT:/usr/local/lib:$ET_LIBROOT/lib
elif [ $LOCALE == "Mx2" ]; then
  #Locale for MINERvA operations for 2x2
  export DAQROOT=/root/minervadaq/minervadaq
  export CAEN_DIR=/work/software/CAENVMElib
  export CAEN_VERSION=CAEN_3_4_4
  export CODA_VERSION=et_16.5
  export CODA_HOME=${DAQROOT}/${CODA_VERSION}
  export ET_HOME=${CODA_HOME}/build
  export ET_LIBROOT=$ET_HOME
  export INSTALL_DIR=$ET_HOME
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries and log4cpp support
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DAQROOT/lib:$ET_LIBROOT:/usr/local/lib:$ET_LIBROOT/lib
else
  echo Unsupported LOCALE!$  LOCALE is not recognized in this script. 
fi

export INSTALL_DIR=$ET_HOME
export ET_USE64BITS=1

echo Your DAQROOT is $DAQROOT
echo Your CAEN_DIR is $CAEN_DIR
if !([ -z "$BMS_HOME" ]); then
  echo Your BMS_HOME is $BMS_HOME
fi #BMS not needed in locales that use later versions of ET
echo Your ET INSTALL_DIR is $INSTALL_DIR
echo Your ET_HOME is $ET_HOME
echo Your ET_LIBROOT is $ET_LIBROOT
echo Your ET_USE64BITS is $ET_USE64BITS
echo Your LD_LIBRARY_PATH is $LD_LIBRARY_PATH

echo ---------------------------------------------------------------------------

