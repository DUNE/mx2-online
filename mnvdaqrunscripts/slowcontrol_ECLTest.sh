#!/bin/sh


pushd /work/software/mnvconfigurator/v14_SlowControlE2CRC/SC_ECL-TestArea/ >& /dev/null

source /work/software/mnvconfigurator/v14_SlowControlE2CRC/SC_ECL-TestArea/ecl_post_7_2c/setup.sh 

python2 SC_MainApp.py &
popd >& /dev/null

