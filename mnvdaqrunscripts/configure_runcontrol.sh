#!/bin/sh

. $HOME/mnvdaqrunscripts/defs_mx2paths

#which python2.6 >& /tmp/pytest.txt
#PYV=`perl -ne 'if (/no/) { print "python"; } else { print "python2.6"; }' /tmp/pytest.txt`

python  ${RCROOT}/frontend/RunControlConfiguration.py &

