#!/bin/sh

pushd /work/software/croce/mnv-configurator/SlowControlE2/ >& /dev/null
python2.6 SC_MainApp.py &
popd >& /dev/null

