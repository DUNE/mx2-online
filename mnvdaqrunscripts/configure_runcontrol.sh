#!/bin/sh

. $HOME/mnvdaqrunscripts/defs_standardpaths

which python2.6 >& /tmp/pytest.txt
PYV=`perl -ne 'if (/no/) { print "python"; } else { print "python2.6"; }' /tmp/pytest.txt`

$PYV  ${RCROOT}/frontend/RunControlConfiguration.py &

