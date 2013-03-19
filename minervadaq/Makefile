# For the build to work, you need to first source the setup_daqbuild.sh script to set your
#       DAQROOT
#       CAEN_DIR
# environment variables.

#include Make.include
SHELL=/bin/bash

all: FORCE
	gmake hardware-lib;
	gmake event_structure-lib;
	gmake workers-lib;
	gmake event_builder;
	gmake main;
	gmake tests;

clean: FORCE
	gmake hardware-clean;
	gmake event_structure-clean;
	gmake workers-clean;
	gmake event_builder-clean;
	gmake main-clean;
	gmake tests-clean;

relink: FORCE
	gmake hardware-clean;
	gmake event_structure-clean;
	gmake workers-clean;
	gmake event_builder-clean;
	gmake main-clean;
	gmake tests-clean;
	gmake hardware-lib;
	gmake event_structure-lib;
	gmake workers-lib;
	gmake event_builder;
	gmake main;
	gmake tests;

hardware-lib: FORCE
	cd fermihardware/src; make;\
	cd ../;

event_structure-lib: FORCE
	cd event_structure/src; make;\
	cd ../;

workers-lib: FORCE
	cd workers/src; make;\
	cd ../;

event_builder: FORCE
	cd event_builder/src; make;\
	cd ../;

main: FORCE
	cd main; make;
	cd ../;

tests: FORCE
	cd tests; make;
	cd ../;

event_builder-clean: FORCE
	cd event_builder/src; gmake clean;
	cd ../;

main-clean: FORCE
	cd main; gmake clean;
	cd ../;

hardware-clean: FORCE
	cd fermihardware/src; gmake clean;

workers-clean: FORCE
	cd workers/src; gmake clean;

event_structure-clean: FORCE
	cd event_structure/src; make clean;

tests-clean: FORCE
	cd tests; gmake clean;
	cd ../;

FORCE:
	if test -d lib; then echo LibOk; else mkdir -p lib; fi
	if test -d bin; then echo BinOk; else mkdir -p bin; fi
