if [ "$LOCALE" == "" ]
then
  echo No LOCALE defined!  Please source setup_daqbuild.sh!
  return 1
fi

if [ "$ET_HOME" == "" ]
then
  echo No ET_HOME defined!  Please source setup_daqbuild.sh!
  return 1
fi

export BMS_HOME=${DAQROOT}/et_9.0/BMS
export INSTALL_DIR=$ET_HOME
export ET_USE64BITS=1

echo ---------------------------------------------------------------------------
echo Your BMS_HOME is $BMS_HOME
echo Your INSTALL_DIR is $INSTALL_DIR
echo Your ET_USE64BITS is $ET_USE64BITS
echo Your LD_LIBRARY_PATH is $LD_LIBRARY_PATH
echo ---------------------------------------------------------------------------

