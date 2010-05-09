#!/bin/sh

gmake clean
gmake
rm /work/data/logs/newReadout.txt

if [ $# -gt 0 ]; then
	if [ $1 == "v" ]; then
		rm zvaltest1.txt
		valgrind -v --log-file-exactly=zvaltest1.txt ./newReadout -crim 224 -g
	 fi
else
	./newReadout -crim 224 -g
fi

exit 0
