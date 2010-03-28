# Set your LOCALE.  Currently on the FNAL mnvonline and minervatest
# machines, the LOCALE is set in the mnvonline user .bash_profile.
if [ "$LOCALE" == "" ]
then
  echo No default LOCALE defined!  Assigning your LOCALE to FNAL...
  export LOCALE=FNAL
fi

echo ---------------------------------------------------------------------------
echo Welcome to the MINERvA DAQ Software Environment.
echo
echo Your LOCALE is $LOCALE.
echo Note, when you run this script you may supply the DAQROOT as an argument.
echo ---------------------------------------------------------------------------

if [ $LOCALE == 'FNAL' ]
then
	export DAQROOT=/work/software/mnvonline/mnvdaq
	if [ $# -gt 0 ]; then
		export DAQROOT=$1
	fi
        export CAEN_DIR=/work/software/CAENVMElib
	export ET_HOME=$DAQROOT/et_9.0/Linux-x86_64-64
	export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
	# Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
	export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
	# Add /usr/local/lib for log4cpp support.
	export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/lib
elif [ $LOCALE == 'NEARLINE' ]
then
	export DAQROOT=/scratch/nearonline/mnvdaq
	if [ $# -gt 0 ]; then
		export DAQROOT=$1
	fi
	export CAEN_DIR=/scratch/nearonline/CAENVMElib
	export ET_HOME=$DAQROOT/et_9.0/Linux-x86_64-64
	export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
	# Add $ET_LIBROOT/lib & $CAEN_DIR/lib for ET & CAEN libraries.
	export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
	# Add log4cpp support.
	export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/scratch/nearonline/log4cpp/lib
else
	echo Unsupported LOCALE!
	exit 1
fi

export BMS_HOME=${DAQROOT}/et_9.0/BMS
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

