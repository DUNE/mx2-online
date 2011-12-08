#!/bin/sh

which python2.6 >& /tmp/pytest.txt
PYV=`perl -ne 'if (/no/) { print "python"; } else { print "python2.6"; }' /tmp/pytest.txt`

pushd /work/software/mnvconfigurator/SlowControl >& /dev/null
$PYV SC_MainApp.py &
popd >& /dev/null
