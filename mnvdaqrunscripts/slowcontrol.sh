#!/bin/sh

pushd /work/software/mnvconfigurator/SlowControl >& /dev/null
python SC_MainApp.py &
popd >& /dev/null
