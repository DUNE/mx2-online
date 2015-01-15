#!/bin/sh

pushd /work/software/mnvconfigurator/SlowControlE2cr2CRC/ >& /dev/null
python2.6 SC_MainApp.py &
popd >& /dev/null

