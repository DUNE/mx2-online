# For the build to work, you need to first source the setup_daqbuild.sh script to set your
#       DAQROOT
#       CAEN_DIR
# environment variables.

#include Make.include
SHELL=/bin/bash

hardware-lib: FORCE
	cd fermihardware/src; make;\
	cd ../;

caenint-lib: FORCE
	cd caeninterface/src; make;\
	cd ../;

acquire_data-lib: FORCE
	cd acquire_data/src; make;\
	cd ../;

event_structure-lib: FORCE
	cd event_structure/src; make;\
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

hardware-clean: FORCE
	cd fermihardware/src; make clean;

caenint-clean: FORCE
	cd caeninterface/src; make clean;

acquire_data-clean: FORCE
	cd acquire_data/src; make clean;

event_structure-clean: FORCE
	cd event_structure/src; make clean;

all: FORCE
	gmake hardware-lib;
	gmake caenint-lib;
	gmake acquire_data-lib;
	gmake event_structure-lib;
	gmake event_builder;
	gmake main;

clean: FORCE
	gmake hardware-clean;
	gmake caenint-clean;
	gmake acquire_data-clean;
	gmake event_structure-clean;
	gmake event_builder-clean;
	gmake main-clean;



FORCE:

