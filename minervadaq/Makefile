# For the build to work, you need to first source the setup_daqbuild.sh script to set your
#       DAQROOT
#       CAEN_DIR
# environment variables.

#include Make.include
SHELL=/bin/bash

all: FORCE
	gmake hardware-lib;
	gmake event_structure-lib;
	gmake acquire_data-lib;
	gmake event_builder;
	gmake main;
	gmake tests;

clean: FORCE
	gmake hardware-clean;
	gmake event_structure-clean;
	gmake acquire_data-clean;
	gmake event_builder-clean;
	gmake main-clean;
	gmake tests-clean;

relink: FORCE
	gmake hardware-clean;
	gmake event_structure-clean;
	gmake acquire_data-clean;
	gmake event_builder-clean;
	gmake main-clean;
	gmake tests-clean;
	gmake hardware-lib;
	gmake event_structure-lib;
	gmake acquire_data-lib;
	gmake event_builder;
	gmake main;
	gmake tests;

hardware-lib: FORCE
	cd fermihardware/src; make;\
	cd ../;

event_structure-lib: FORCE
	cd event_structure/src; make;\
	cd ../;

acquire_data-lib: FORCE
	cd acquire_data/src; make;\
	cd ../;

event_builder: FORCE
	cd event_builder/src; make;\
	cd ../;

main: FORCE
	cd main; make;
	cd ../;
	cd daq_master; gmake
	cd ../;
	cd daq_server; gmake
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
	cd daq_master; gmake clean;
	cd ../;
	cd daq_server; gmake clean;
	cd ../;
	cd bin; rm minervadaq; rm daq_master; rm daq_slave_service; rm event_builder;
	cd ../;

hardware-clean: FORCE
	cd fermihardware/src; make clean;

acquire_data-clean: FORCE
	cd acquire_data/src; make clean;

event_structure-clean: FORCE
	cd event_structure/src; make clean;

tests-clean: FORCE
	cd tests; gmake clean;
	cd ../;

FORCE:
	if test -d lib; then echo LibOk; else mkdir -p lib; fi
