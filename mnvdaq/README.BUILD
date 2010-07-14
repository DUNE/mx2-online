This file is current as of 2010.July.14 - GNP

How to Build the MINERvA DAQ.
-----------------------------

Quick Directions (software already installed):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1) Log on to the DAQ machine you want to update as the "mnvonline" user.  On T977 machines, use the "tbonline" 
account instead.  In the $HOME are there will be a set of scripts for launching the Run and Slow Controls, 
configuring the environment, etc.  These scripts will vary from machine to machine, but they are hopefully 
titled in a useful way.  The primary distinction to be aware of is between single and mulit-machine DAQ builds.  
For most production machines, that choice is hidden, but the user should pay attention to the setup scripts just 
in case.

2) Source the setup script to set the DAQ environment variables.  On E938 machines, the script is likely named 
"setupdaqenv.sh."  On T977 machines, it will likely be named "singledaqenv.sh."

3) Change directories to the $DAQROOT.

4) Run the compiler script.

Example:
mnvtbonline0.fnal.gov> cd $DAQROOT
mnvtbonline0.fnal.gov> ./compiler.sh

5) If the build succeeded, you should see the following in the $DAQROOT/lib and $DAQROOT/bin directories:
        
mnvtbonline0.fnal.gov> llt lib/ bin/
lib/:   
total 1.2M
drwxr-xr-x 2 tbonline e938 4.0K Apr 23 16:52 CVS/
-rwxr-xr-x 1 tbonline e938 715K Jun  1 18:13 libhardware.so*
-rwxr-xr-x 1 tbonline e938  52K Jun  1 18:13 libcaeninterface.so*
-rwxr-xr-x 1 tbonline e938 326K Jun  1 18:13 libminerva_acquire.so*
-rwxr-xr-x 1 tbonline e938  48K Jun  1 18:13 libevent_structure.so*bin/:
total 532K
-rwxr-xr-x 1 tbonline e938   97 Nov 29  2009 cleaner.sh*
drwxr-xr-x 2 tbonline e938 4.0K Apr 29 09:59 CVS/
-rwxr-xr-x 1 tbonline e938  84K Jun  1 18:13 event_builder*
-rwxr-xr-x 1 tbonline e938 243K Jun  1 18:13 minervadaq*
-rwxr-xr-x 1 tbonline e938  77K Jun  1 18:13 daq_master*
-rwxr-xr-x 1 tbonline e938  98K Jun  1 18:13 daq_slave_service*


Complete Directions (no software installed):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To build the MINERvA Production DAQ (mnvdaq) you need to first install and build CAEN driver libraries 
to interface with the CAEN v2718 VME Controller and a2818 PCI Interface Card.  These drivers are available
on the CAEN website (http://www.caen.it/nuclear/index.php) and specific drivers for SLF4.6 and SLF5.3 have 
been stored on the MINERvA Plone (https://plone3.fnal.gov/P0/Minerva).  Note that the drivers for SLF4.6 
must be patched (the patch is stored on the MINERvA Plone).  

The most recent CAENlib version as of 2009.December.30 is 2.11, but we currently choose to use 2.7 due to 
some slightly funny bugs with 2.11.  Migration to 2.11 or 2.12 when it becomes available should be 
investigated.  The 2.7 version of the drivers is available with the DAQ in the misc/support directory.

Store the CAEN libraries in a directory named ${WORKROOT}/CAENVMElib/lib, where $WORKROOT is a directory 
of your choosing.  If you attempt to install the CAEN drivers by untarring the packages and following the 
contained instructions in $WORKROOT you will end up with the correct structure for the 2.11 version of the
libraries.  v2.7 requires some fiddling to get things clean afterwards because the packages also contains 
the libraries for Windows.  Note that even if you do not intend to run the DAQ for acquisition, you still 
need the CAEN libraries to build the code.

Note: It is worth mentioning that the drivers are set up a bit funny on the default DAQ machines.  We used 
the x86_64 version of the library, but ran the regular install script (which put the libraries in /usr/lib 
instead of /usr/lib64 as is technically proper).  The Makefiles for the DAQ reflect this, so if you put 
the CAEN libraries in the "correct" directory (/usr/lib64), you will need to also modify the default 
Makefiles in order to get the DAQ to build.

Once the CAEN libraries are installed, go to $WORKROOT and create a mnvonline/ directory to hold the DAQ 
and (eventually) SlowControl code.  Within mnvonline/ run a CVS checkout on the package mnvdaq.  Make sure 
you have the following environment variables set and a valid kerberos ticket to access the MINERvA CVS 
repository:
	CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/minervasw
	CVS_RSH=ssh

Inside the mnvdaq/ directory you will find a setup script.  It is a good idea to read this script 
carefully before proceeding.  The "location" is set by a $LOCALE environment variable.  Set your own $LOCALE 
variable or mimic the directory structure of another $LOCALE and use that value for your own $LOCALE.  

As of 2010.July14, the set-up scripts and run scripts are tuned in a fairly inflexible way for 
operation on Fermilab machines, set by hostnames in the options/ directory set of Make.options files.  
For set-up in a different environment, the default scripts will need to be edited carefully.

Before you build the DAQ, it is important to understand the possible architectures.  The DAQ can be run 
either on a single PC or on a network of PC's.  Currently, we support the following options:
1) Single PC
2) Multi-PC with one Head Node, one Soldier (Chief) Readout Client, and one Worker Readout Client.
The distinguishing feature between the Readout Clients is that one and only one is responsible for attaching 
the end-of-event DAQ Header bank (the Soldier).

In principle, the DAQ can be extended to support an arbitrary number of Worker Clients, but this feature is 
not currently supported (and would require some significant re-engineering of the networking).  Having three
"tiers" of machines can make the jargon confusing, so partly for fun, we will use the following short-hand:
- Queen : Server node (also the Single PC mode).
- Soldier : Chief Readout Client (attaches the DAQ Header bank at the end of the gate).
- Worker : Worker Readout Client.

By default the DAQ will build in Single PC mode.  If you want to build in multi-PC mode, configure the 
options in the Make.options as follows:
	Queen  : COMPILE_OPTIONS += -DMULTIPC -DMASTER 
	Soldier: COMPILE_OPTIONS += -DMULTIPC -DMASTER 
	Worker : COMPILE_OPTIONS += -DMULTIPC  
The Queen actually is ambivalent about the MASTER flag - we only run the event_builder task on the Queen, not 
any of the acquisition tasks.

Once you have configured your setup scripts, build the DAQ with the following steps:

1) Go to $DAQROOT/

2) source setupdaqenv.sh

3) Now build ET.  Go to the et_9.0 directory and type "gmake install".

4) MINERvA DAQ uses the following set of ports:
	1090 : Queen-Soldier port (on Soldier)
	1091-1096 : et port (on Queen)
	1098 : Run Control
	1110-1113, 1120-1123: Worker-Solider synchronization ports.
It is a good idea to configure your firewall such that these ports are kept open. 

5) Check ${ET_LIBROOT}/lib and make sure you have libet.a, libet_remote.so, and libet.so.

6) Return to $DAQROOT and type "gmake all"

7) Check ${DAQROOT}/bin/ for 
	daq_master
	daq_slave_service
	event_builder
	minervadaq
And check ${DAQROOT}/lib/ for 
	libcaeninterface.so
	libevent_structure.so
	libhardware.so
	libminerva_acquire.so

8) If you are missing any of these, read the Makefile and try building each package one at a time and check 
for errors.  Most likely, an environment variable has been incorrectly set.

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Note about data sizes!  If you run the DAQ on an OS besides 64-bit SLF5.3, be sure to check the data sizes 
your compiler uses for variables.  The code currently assumes the following (check with sizeOfTest in the 
misc/ folder):

size of unsigned char      = 1
size of unsigned short int = 2
size of unsigned int       = 4
size of unsigned long      = 8
size of unsigned long long = 8

(Size is shown in bytes.)

