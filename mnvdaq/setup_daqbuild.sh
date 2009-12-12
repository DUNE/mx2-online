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
	export DAQROOT=/work/software/mnvonline/mnvdaq
        export CAEN_DIR=/work/software/CAENVMElib
	export ET_HOME=$DAQROOT/et_9.0/Linux-x86_64-64
	export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
	export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
else
        echo Unsupported LOCALE!
        exit 1
fi

echo Your DAQROOT is $DAQROOT
echo Your CAEN_DIR is $CAEN_DIR
echo Your ET_HOME is $ET_HOME
echo Your ET_LIBROOT is $ET_LIBROOT
echo Your LD_LIBRARY_PATH is $LD_LIBRARY_PATH
echo ---------------------------------------------------------------------------

