#!/bin/sh

pushd /work/software/mx2daq/mnvconfigurator/v14_SlowControlE2CRC/ >& /dev/null
#pushd /work/software/mnvconfigurator/v14_SlowControlE2CRC/ >& /dev/null
#pushd /work/software/mnvconfigurator/v13_SlowControlE2CRC/ >& /dev/null
#pushd /work/software/mnvconfigurator/SlowControlE2cr2CRC/ >& /dev/null
python SC_MainApp.py &
popd >& /dev/null

