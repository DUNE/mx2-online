#!/bin/sh

EXE=${DAQROOT}/bin/tests
ARGS="-c 2 -h 3 -f 5"
VALLOG="grindtest1.txt"

${EXE} ${ARGS}

# if test -e ${VALLOG}; then
#   rm ${VALLOG}
# fi
# valgrind --num-callers=50 --leak-check=full --verbose --show-reachable=yes --suppressions=${DAQROOT}/tests/suppressions02.supp --log-file-exactly=${VALLOG} ${EXE} ${ARGS}
# # valgrind --num-callers=50 --leak-check=full --verbose --show-reachable=yes --gen-suppressions=all --log-file-exactly=${VALLOG} ${EXE} ${ARGS}

# cp $VALLOG leaksum.txt
# perl -i -e 'while(<>) { chomp; if (/definitely/) { print $_; } }' leaksum.txt
# cat leaksum.txt
# echo 

