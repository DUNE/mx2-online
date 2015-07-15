#!/bin/sh

. $HOME/mnvdaqrunscripts/defs_standardpaths

# Get Python version.
which python2.6 >& /tmp/pytest.txt
PYV=`perl -ne 'if (/no/) { print "python"; } else { print "python2.6"; }' /tmp/pytest.txt`

pushd ${RCROOT}/backend >& /dev/null
$PYV DataAcquisitionManager.py start 
popd >& /dev/null

