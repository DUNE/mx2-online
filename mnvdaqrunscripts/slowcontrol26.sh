#!/bin/sh

pushd /work/software/mnvconfigurator/SlowControl >& /dev/null
python2.6 SC_MainApp.py &
popd >& /dev/null
