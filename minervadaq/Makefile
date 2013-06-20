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
	make -C fermihardware/src

event_structure-lib: FORCE
	make -C event_structure/src

workers-lib: FORCE
	make -C workers/src

event_builder: FORCE
	make -C event_builder/src

main: FORCE
	make -C main

tests: FORCE
	make -C tests

event_builder-clean: FORCE
	make -C event_builder/src clean

main-clean: FORCE
	make -C main clean

hardware-clean: FORCE
	make -C fermihardware/src clean

workers-clean: FORCE
	make -C workers/src clean

event_structure-clean: FORCE
	make -C event_structure/src clean

tests-clean: FORCE
	make -C tests clean

FORCE:
	@if test -d lib; then echo LibOk; else mkdir -p lib; fi
	@if test -d bin; then echo BinOk; else mkdir -p bin; fi
