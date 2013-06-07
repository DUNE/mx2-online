# Note, to compile the DAQ, after you pull the package down from CVS, you need to untar the ET code first!
# Set your LOCALE.  One Valid choice right now: "FNAL" for Fermilab.  Currently on the FNAL mnvonline
# machines, the LOCALE is set in the mnvonline user .bash_profile.
if [ "$LOCALE" == "" ]
then
  echo No default LOCALE defined!  Assigning your LOCALE to FNAL...
  export LOCALE=FNAL
fi

echo ---------------------------------------------------------------------------
echo Welcome to the MINERvA DAQ Software Environment.
echo
echo Your LOCALE is $LOCALE
echo ---------------------------------------------------------------------------

if [ $LOCALE == 'FNAL' ]
then
  if [ $# -gt 0 ]; then	 
    export DAQROOT=$1	 
  else	
    export DAQROOT=/work/software/mnvonline/mnvdaq
  fi
  export CAEN_DIR=/work/software/CAENVMElib
  export ET_HOME=$DAQROOT/et_12.0/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
  # Add local SQLite
  export LD_LIBRARY_PATH=$DAQROOT/sqlite/lib:$LD_LIBRARY_PATH
  export PATH=$DAQROOT/sqlite/bin:$PATH
  # Add /usr/local/lib for log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
elif [ $LOCALE == 'NEARLINE' ]
then
  export DAQROOT=/scratch/nearonline/mirror/mnvdaq
  export CAEN_DIR=/scratch/nearonline/mirror/CAENVMElib
  export ET_HOME=$DAQROOT/et_12.0/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
  # Add log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/scratch/nearonline/mirror/log4cpp/lib
elif [ $LOCALE == "NEARLINEDEV" ]
then
  export DAQROOT=/work/mnvdaq
  export CAEN_DIR=/work/CAENVMElib
  export ET_HOME=$DAQROOT/et_12.0/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x64/:$LD_LIBRARY_PATH
  # Add log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/work/log4cpp/lib
elif [ $LOCALE == "D0TESTSTAND" ]
then
  #export DAQROOT=/work/mnvdaq
  setup caenvme
  export CAEN_DIR=$CAENVME_DIR
  export ET_HOME=$DAQROOT/et_12.0/Linux-x86_64-64
  export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
  # Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
  export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
  # Add log4cpp support.
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/work/log4cpp/lib
else
  echo Unsupported LOCALE!
  exit 1
fi

export INSTALL_DIR=$ET_HOME
export ET_USE64BITS=1

echo Your DAQROOT is $DAQROOT
echo Your CAEN_DIR is $CAEN_DIR
echo Your BMS_HOME is $BMS_HOME
echo Your ET INSTALL_DIR is $INSTALL_DIR
echo Your ET_HOME is $ET_HOME
echo Your ET_LIBROOT is $ET_LIBROOT
echo Your ET_USE64BITS is $ET_USE64BITS
echo Your LD_LIBRARY_PATH is $LD_LIBRARY_PATH

echo ---------------------------------------------------------------------------

