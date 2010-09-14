# Note, to compile the DAQ, after you pull the package down from CVS, you need to untar the ET code first!
# Set your LOCALE.  Valid choices are "RUT" for the State University of New Jersey and "FNAL" for Fermilab.
# Currently at FNAL, the LOCALE is set by in the minerva .bash_profile.
if [ "$LOCALE" == "" ]
then
  echo No default LOCALE defined!  Assigning your LOCALE to The State University of New Jersey...
  export LOCALE=RUT
fi

echo ---------------------------------------------------------------------------
echo Welcome to the MINERvA DAQ development environment.
echo
echo Your LOCALE is $LOCALE
echo
echo If this is not where you actually are, you need to edit this setup script!
echo ---------------------------------------------------------------------------

if [ $LOCALE == 'RUT' ]
then
	export DAQROOT=/home/minerva/linux_daq/devdaq
        export CAEN_DIR=/home/minerva/compile_here/CAEN_VME_SDK_BRIDGES_3_1/VME_Bridge_Demo_and_Lib/Linux/
	export ET_HOME=$DAQROOT/et_9.0
	export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
	export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib
fi

if [ $LOCALE == 'FNAL' ]
then
	export DAQROOT=/work/software/mnvonline/mnvdaq
        export CAEN_DIR=/work/software/CAENVMElib
	export ET_HOME=$DAQROOT/et_9.0/Linux-x86_64-64
	export ET_LIBROOT=$ET_HOME/Linux-x86_64-64
	export LD_LIBRARY_PATH=$DAQROOT/lib:$ET_LIBROOT/lib:$CAEN_DIR/lib/x86_64/:$LD_LIBRARY_PATH
fi


echo Your DAQROOT is $DAQROOT
echo Your CAEN_DIR is $CAEN_DIR
echo Your ET_HOME is $ET_HOME
echo Your ET_LIBROOT is $ET_LIBROOT
echo Your LD_LIBRARY_PATH is $LD_LIBRARY_PATH
echo ---------------------------------------------------------------------------

