/*! \file minervadaq.cpp
 * \brief  Main routine: minervadaq for acquiring data from the MINERvA detector. 
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 */

#include "acquire_data.h"
#include "eb_service.h"
#include "MinervaEvent.h"
#include <fstream>
#include <iostream>
#include <sstream>

#include <boost/ref.hpp>
#include <boost/thread/mutex.hpp>
#include <ctime>
#include <sys/time.h>
#include <sys/stat.h> // for file sizes, not actually used... (can't trust answers)
#include <stdlib.h>   // for file sizes, not actually used...
#include <signal.h>

#define THREAD_COUNT 4  /*!< a thread count var if we aren't finding the # of threads needed */
#if MASTER||SINGLEPC // Soldier Node
#define CONTROLLER_ID 0
#elif (!MASTER)&&(!SINGLEPC) // Worker Node
#define CONTROLLER_ID 1
#endif

#include "minervadaq.h"

// log4cpp Variables - Needed throughout the minervadaq functions.
log4cpp::Appender* daqAppender;
log4cpp::Category& root   = log4cpp::Category::getRoot();
log4cpp::Category& mnvdaq = log4cpp::Category::getInstance(std::string("mnvdaq"));

/*! The main routine which executes the data acquisition sequences for minervadaq. */

using namespace std;

int main(int argc, char *argv[]) 
{
	/*********************************************************************************/
	/*      Initialize some execution status variables                               */
	/*********************************************************************************/
	bool sentSentinel        = false;     // Whether the sentinel (end-of-data signal) gate was sent to the master by this process
	int record_gates         = -1;        // Run length in GATES.
	RunningModes runningMode = OneShot;
	int runMode              = 0;         // Same as OneShot...
	int runNumber            = 938;       // MINERvA!
	int subRunNumber         = 11;        // It goes to 11...
	int record_seconds       = -1;	      // Run length in SECONDS (Not Supported...)
	int detector             = 0;         // Default to UnknownDetector.
	int detectorConfig       = 0;         // Number of FEB's.
	int LEDLevel             = 0;
	int LEDGroup             = 0;
	int hardwareInit         = 1;         // Default to "init." (This will set VME card timing modes, etc., but not touch FEB's).
	string fileroot          = "testme";  // For logs, etc.  
	string strtemp           = "unknown"; // For SAM, temp.
	char config_filename[100]; sprintf(config_filename,"unknown"); // For SAM.
	string et_filename       = "/work/data/etsys/testme_RawData";  
	string log_filename      = "/work/data/logs/testme_Log.txt"; 
	char sam_filename[100]; sprintf(sam_filename,"/work/data/sam/testme_SAM.py");
	char lasttrigger_filename[100]; sprintf(lasttrigger_filename,"/work/conditions/last_trigger.dat"); 
	char data_filename[100]; sprintf(data_filename,"/work/data/sam/testme_RawData.dat");
	unsigned long long firstEvent, lastEvent;  //unused in main...
	int networkPort          = 1201; // 1201-1250 (inclusive) currently open.
	int controllerErrCode;
	string str_controllerID  = "0";
#if MASTER||SINGLEPC // Soldier Node
	str_controllerID  = "0";
	controllerErrCode = 2;
#elif (!MASTER)&&(!SINGLEPC) // Worker Node
	str_controllerID  = "1";
	controllerErrCode = 4;
#endif
	unsigned long long startTime, stopTime;          // For SAM.  Done at second & microsecond precision.
	unsigned long long startReadout, stopReadout;    // For gate monitoring.  Done at microsecond precision.
	unsigned long long debugTimeStart, debugTimeEnd; // Misc. debug vars.

	/*********************************************************************************/
	/* Process the command line argument set.                                        */
	/*********************************************************************************/
	int optind = 1;
	// Decode Arguments
	std::cout << "\nArguments to MINERvA DAQ: \n";
	while ((optind < argc) && (argv[optind][0]=='-')) {
		string sw = argv[optind];
		if (sw=="-r") {
			optind++;
			runNumber = atoi(argv[optind]);
			std::cout << "\tRun Number             = " << runNumber << std::endl;
        	}
		else if (sw=="-s") {
			optind++;
			subRunNumber = atoi(argv[optind]);
			std::cout << "\tSubrun Number          = " << subRunNumber << std::endl;
        	}
		else if (sw=="-g") {
			optind++;
			record_gates = atoi(argv[optind]);
			std::cout << "\tTotal Gates            = " << record_gates << std::endl;
        	}
		else if (sw=="-t") {
			optind++;
			record_seconds = atoi(argv[optind]);
			std::cout << "\tTotal Seconds (not supported) = " << record_seconds << std::endl;
        	}
		else if (sw=="-m") {
			optind++;
			runMode = atoi(argv[optind]);
			runningMode = (RunningModes)runMode;
			std::cout << "\tRunning Mode (encoded) = " << runningMode << std::endl;
        	}
		else if (sw=="-d") {
			optind++;
			detector = atoi(argv[optind]);
			std::cout << "\tDetector (encoded)     = " << detector << std::endl;
        	}
		else if (sw=="-et") {
			optind++;
			fileroot     = argv[optind];
			et_filename  = "/work/data/etsys/" + fileroot + "_RawData";
			log_filename = "/work/data/logs/" + fileroot + "_Controller" + 
				str_controllerID + "Log.txt";
			sprintf(sam_filename,"/work/data/sam/%s_SAM.py",fileroot.c_str());
			sprintf(data_filename,"/work/data/rawdata/%s_RawData.dat",fileroot.c_str());
			std::cout << "\tET Filename            = " << et_filename << std::endl;
			std::cout << "\tSAM Filename           = " << sam_filename << std::endl;
			std::cout << "\tLOG Filename           = " << log_filename << std::endl;
		}
		else if (sw=="-cf") {
			optind++;
			strtemp = argv[optind]; 
			sprintf(config_filename,"%s",strtemp.c_str());
			std::cout << "\tHardware Config. File  = " << config_filename << std::endl;
		}
		else if (sw=="-dc") {
			optind++;
			detectorConfig = atoi(argv[optind]);
			std::cout << "\tDetector Config. Code  = " << detectorConfig << std::endl;	
		}
		else if (sw=="-ll") {
			optind++;
			LEDLevel = atoi(argv[optind]);
			std::cout << "\tLED Level              = " << LEDLevel << std::endl;	
		}
		else if (sw=="-lg") {
			optind++;
			LEDGroup = atoi(argv[optind]);
			std::cout << "\tLED Group              = " << LEDGroup << std::endl;	
		}
		else if (sw=="-hw") {
			optind++;
			hardwareInit = atoi(argv[optind]);
			std::cout << "\tVME Card Init. Level   = " << hardwareInit << std::endl;	
		}
		else if (sw=="-p") {
			optind++;
			networkPort = atoi(argv[optind]);
			std::cout << "\tET System Port         = " << networkPort << std::endl;	
		}
		else
			std::cout << "Unknown switch: " << argv[optind] << std::endl;
		optind++;
	}
	std::cout << std::endl;

	// Report the rest of the command line...
	if (optind < argc) {
		std::cout << "There were remaining arguments!  Are you SURE you set the run up correctly?" << std::endl;
		std::cout << "  Remaining arguments = ";
		for (;optind<argc;optind++) std::cout << argv[optind];
		std::cout << std::endl;
	}

	// Set up general logging utilities.
	daqAppender = new log4cpp::FileAppender("default", log_filename);
	daqAppender->setLayout(new log4cpp::BasicLayout());
	root.addAppender(daqAppender);
	root.setPriority(log4cpp::Priority::DEBUG);
        mnvdaq.setPriority(log4cpp::Priority::DEBUG);
	root.infoStream()   << "Starting MINERvA DAQ. ";
	mnvdaq.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
	mnvdaq.infoStream() << "Arguments to MINERvA DAQ: ";
	mnvdaq.infoStream() << "  Run Number             = " << runNumber;
	mnvdaq.infoStream() << "  Subrun Number          = " << subRunNumber;
	mnvdaq.infoStream() << "  Total Gates            = " << record_gates;
	mnvdaq.infoStream() << "  Running Mode (encoded) = " << runningMode;
	mnvdaq.infoStream() << "  Detector (encoded)     = " << detector;
	mnvdaq.infoStream() << "  DetectorConfiguration  = " << detectorConfig;
	mnvdaq.infoStream() << "  LED Level (encoded)    = " << LEDLevel;
	mnvdaq.infoStream() << "  LED Group (encoded)    = " << LEDGroup;
	mnvdaq.infoStream() << "  ET Filename            = " << et_filename;
	mnvdaq.infoStream() << "  SAM Filename           = " << sam_filename;
	mnvdaq.infoStream() << "  LOG Filename           = " << log_filename;
	mnvdaq.infoStream() << "  Configuration File     = " << config_filename;
	mnvdaq.infoStream() << "  VME Card Init. Level   = " << hardwareInit;	
	mnvdaq.infoStream() << "  ET System Port         = " << networkPort;	
	mnvdaq.infoStream() << "See Event/MinervaEvent/xml/DAQHeader.xml for codes.";
	mnvdaq.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
	mnvdaq.infoStream() << "Additional Parameters: ";
	mnvdaq.infoStream() << "  Mixed Mode Physics Gate Cutoff Time  = " << physReadoutMicrosec;	
#if MULTIPC
	mnvdaq.infoStream() << "  Configured for a Multi-PC Build...";	
#if MASTER
	mnvdaq.infoStream() << "  ->Configured as a Soldier Node...";	
#else
	mnvdaq.infoStream() << "  ->Configured as a Worker Node...";	
#endif
#endif
#if SINGLEPC
	mnvdaq.infoStream() << "  Configured for a Single-PC Build...";	
#endif
	mnvdaq.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";

	// Log files for threading in the main routine. 
#if (THREAD_ME)&&(TIME_ME)
	ofstream thread_launch_log;
	ofstream thread_return_log;
	thread_launch_log.open("thread_launch_log.csv");
	thread_return_log.open("thread_return_log.csv");
#endif

#if TIME_ME
	// For Benchmark Execution Timing.                                             
	struct timeval start_time, stop_time;
	gettimeofday(&start_time, NULL);
	take_data_extime_log.open("take_data_extime_log.csv");
#endif

	/*********************************************************************************/
	/*   An event_handler structure object for building event data blocks.           */
	/*********************************************************************************/
	event_handler event_data;
	evt_record_available = true;
	// Add some data for the header to the event_handler...
	event_data.runNumber      = runNumber;
	event_data.subRunNumber   = subRunNumber;
	event_data.detectorType   = (unsigned char)detector;
	event_data.detectorConfig = (unsigned short)detectorConfig;
	event_data.triggerType    = (unsigned short)0;
	event_data.minosSGATE     = (unsigned int)0;
	event_data.readoutTime    = (unsigned int)0;


	/*********************************************************************************/
	/* Now set up ET for use in writing the first-pass memory mapped data file.      */
	/*********************************************************************************/
	et_att_id      attach;
	et_sys_id      sys_id;
	//et_id          *id;  // Unused in main?
	et_openconfig  openconfig;

	// Configuring the ET system is the first thing we must do.
	et_open_config_init(&openconfig);

	// Set the remote host.
	// We operate the DAQ exclusively in "remote" mode even when running on only one PC.
	et_open_config_setmode(openconfig, ET_HOST_AS_REMOTE); 

	// Set to the current host machine name. 
	char hostName[100];
#if SINGLEPC
	sprintf(hostName, "localhost");
#endif
#if MULTIPC
	char soldierName[100];
	char workerName[100];
#if WH14T||WH14B
	sprintf(hostName,    "minervatest03.fnal.gov");
	sprintf(soldierName, "minervatest02.fnal.gov");
	sprintf(workerName,  "minervatest04.fnal.gov");
#endif
#if CRATE0||CRATE1
#if BACKUPNODE
	sprintf(hostName,    "mnvonlinebck1.fnal.gov");
#else
	sprintf(hostName,    "mnvonlinemaster.fnal.gov");
#endif
	sprintf(soldierName, "mnvonline0.fnal.gov");
	sprintf(workerName,  "mnvonline1.fnal.gov");
#endif
#endif
	et_open_config_sethost(openconfig, hostName);  
	mnvdaq.infoStream() << "Setting ET host to " << hostName;	

	// Set direct connection.
	et_open_config_setcast(openconfig, ET_DIRECT);  // Remote mode only.

	// Set the server port.
	et_open_config_setserverport(openconfig, networkPort); // Remote mode only.
	mnvdaq.infoStream() << "Set ET server port to " << networkPort;	

	// Open it.
	mnvdaq.infoStream() << "Trying to open ET system...";	
	if (et_open(&sys_id, et_filename.c_str(), openconfig) != ET_OK) {
		printf("et_producer: et_open problems\n");
		mnvdaq.fatalStream() << "et_producer: et_open problems!";
		exit(EXIT_UNSPECIFIED_ERROR);
	}
	mnvdaq.infoStream() << "...Opened ET system!";	

	// Clean up.
	et_open_config_destroy(openconfig);

	// Set the debug level for output (everything).
	et_system_setdebug(sys_id, ET_DEBUG_INFO);

	// Attach to GRANDCENTRAL station since we are producing events.
	if (et_station_attach(sys_id, ET_GRANDCENTRAL, &attach) < 0) {
		printf("et_producer: error in station attach\n");
		mnvdaq.fatalStream() << "et_producer: error in station attach!";
		system("sleep 10s");
		exit(EXIT_UNSPECIFIED_ERROR);
	} 
	mnvdaq.infoStream() << "Successfully attached to GRANDCENTRAL Station.";	


	/*********************************************************************************/
	/*  Basic Socket Configuration for Worker && Soldier Nodes.                      */
	/*********************************************************************************/
#if MULTIPC
	workerToSoldier_port += (unsigned short)(subRunNumber % 4); 
	soldierToWorker_port += (unsigned short)(subRunNumber % 4);
	mnvdaq.infoStream() << "Worker to Solider Network Port = " << workerToSoldier_port;
	mnvdaq.infoStream() << "Soldier to Worker Network Port = " << soldierToWorker_port;
#endif
#if MASTER&&(!SINGLEPC) // Soldier Node
	// Create a TCP socket pair.
	mnvdaq.infoStream() << "~~~~~~~ Socket Setup";
	try {
		int error = CreateSocketPair(workerToSoldier_socket_handle, soldierToWorker_socket_handle);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Could not create socket pair!  Exiting!" << std::endl;
		mnvdaq.fatalStream() << "Could not create socket pair!  Exiting!";
		exit(EXIT_UNSPECIFIED_ERROR);
	}
	// Set up the soldierToWorker service.
	try {
		int error = SetupSocketService(soldierToWorker_service, worker_node_info, workerName, soldierToWorker_port ); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Could not setup socket service!  Exiting!" << std::endl;
		mnvdaq.fatalStream() << "Could not setup socket service!  Exiting!";
		exit(EXIT_UNSPECIFIED_ERROR);		
	}
	// Create an address for the workerToSoldier listener.  The soldier listens for data.
	workerToSoldier_socket_address.s_addr = htonl(INADDR_ANY); 
	memset (&workerToSoldier_service, 0, sizeof (workerToSoldier_service));
	workerToSoldier_service.sin_family = AF_INET;
	workerToSoldier_service.sin_port = htons(workerToSoldier_port); 
	workerToSoldier_service.sin_addr = workerToSoldier_socket_address;
	
	// Need to allow the socket to be reused.  This prevents "address already in use" 
	// errors when starting the DAQ again too quickly after the last time it shut down.
	int optval = 1;
	setsockopt(workerToSoldier_socket_handle, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof optval);
	
	// Bind the workerToSoldier socket to that address for the listener.
	if ((bind (workerToSoldier_socket_handle, (const sockaddr*)&workerToSoldier_service, 
			sizeof (workerToSoldier_service)))) {
		mnvdaq.fatalStream() << "Error binding the workerToSoldier socket!"; 
		perror ("bind"); exit(EXIT_UNSPECIFIED_ERROR); 
	} else {
		mnvdaq.infoStream() << "Finished binding the workerToSoldier socket.";
	}
	// Enable connection requests on the workerToSoldier socket for the listener.
	if (listen (workerToSoldier_socket_handle, 10)) { 
		mnvdaq.fatalStream() << "Error listening on the workerToSoldier socket!"; 
		perror("listen"); exit(EXIT_UNSPECIFIED_ERROR); 
	} else {
		mnvdaq.infoStream() << "Enabled listening on the workerToSoldier socket.";
	}
#endif // end if MASTER&&(!SINGLEPC)

#if (!MASTER)&&(!SINGLEPC) // Worker Node
	// Create a TCP socket pair.
	mnvdaq.infoStream() << "~~~~~~~ Socket Setup";
	try {
		int error = CreateSocketPair(workerToSoldier_socket_handle, soldierToWorker_socket_handle);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Could not create socket pair!  Exiting!" << std::endl;
		mnvdaq.fatalStream() << "Could not create socket pair!  Exiting!";
		exit(EXIT_UNSPECIFIED_ERROR);
	}
	// Set up the workerToSoldier service. 
	try {
		int error = SetupSocketService(workerToSoldier_service, soldier_node_info, soldierName, workerToSoldier_port ); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Could not setup socket service!  Exiting!" << std::endl;
		mnvdaq.fatalStream() << "Could not setup socket service!  Exiting!";
		exit(EXIT_UNSPECIFIED_ERROR);                		
	}
	// Create an address for the soldierToWorker listener.  The worker listens for data.
	soldierToWorker_socket_address.s_addr = htonl(INADDR_ANY); 
	memset (&soldierToWorker_service, 0, sizeof (soldierToWorker_service));
	soldierToWorker_service.sin_family = AF_INET;
	soldierToWorker_service.sin_port = htons(soldierToWorker_port); 
	soldierToWorker_service.sin_addr = soldierToWorker_socket_address;

	// Need to allow the socket to be reused.  This prevents "address already in use" 
	// errors when starting the DAQ again too quickly after the last time it shut down.
	int optval = 1;
	setsockopt(soldierToWorker_socket_handle, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof optval);

	// Bind the soldierToWorker socket to that address for the listener.
	if ((bind (soldierToWorker_socket_handle, (const sockaddr*)&soldierToWorker_service, 
			sizeof (soldierToWorker_service)))) { 
		mnvdaq.fatalStream() << "Error binding the soldierToWorker socket!"; 
		perror ("bind"); exit(EXIT_UNSPECIFIED_ERROR); 
	} else {
		mnvdaq.infoStream() << "Finished binding the soldierToWorker socket.";
	}
	// Enable connection requests on the global socket for the listener.
	if (listen (soldierToWorker_socket_handle, 10)) { 
		mnvdaq.fatalStream() << "Error listening on the soldierToWorker socket!"; 
		perror("listen"); exit(EXIT_UNSPECIFIED_ERROR); 
	} else {
		mnvdaq.infoStream() << "Enabled listening on the soldierToWorker socket.";
	}
#endif // end if (!MASTER)&&(!SINGLEPC)


	// Client-server connect - workerToSoldier. 
	workerToSoldier_socket_is_live = false;
#if MASTER&&(!SINGLEPC) // Soldier Node
	std::cout << "\nPreparing make new server connection for workerToSoldier synchronization...\n";
	mnvdaq.infoStream() << "~~~~~~~ Socket Connections";
	mnvdaq.infoStream() << "Preparing make new server connection for workerToSoldier synchronization...";
	mnvdaq.infoStream() << " workerToSoldier_socket_is_live = " << workerToSoldier_socket_is_live; 
	// Accept connection from worker node to supply end of event signalling.
	while (!workerToSoldier_socket_is_live) {
		std::cout << " Waiting for worker node...\n";
		std::cout << " Ready to connect to workerToSoldier_socket_handle: " << 
			workerToSoldier_socket_handle << std::endl;
		mnvdaq.infoStream() << " Waiting for worker node...";
		mnvdaq.infoStream() << " Ready to connect to workerToSoldier_socket_handle: " << 
			workerToSoldier_socket_handle;
		struct sockaddr_in remote_address;
		socklen_t address_length;
		address_length = sizeof (remote_address);
		// Accept will wait for a connection...
		workerToSoldier_socket_connection = 
			accept(workerToSoldier_socket_handle, (sockaddr*)&remote_address, &address_length);
		mnvdaq.infoStream() << " workerToSoldier_socket_connection return value = " << workerToSoldier_socket_connection;
		if (workerToSoldier_socket_connection == -1) {
			// The call to accept failed. 
			if (errno == EINTR) {
				// The call was interrupted by a signal. Try again.
				continue;
			} else {
				// Something else went wrong.
				mnvdaq.fatalStream() << "Error in socket accept!"; 
				perror("accept");
				exit(EXIT_UNSPECIFIED_ERROR);
			}
		}
		workerToSoldier_socket_is_live = true;
	} // end while !workerToSoldier_socket_is_live
	std::cout << " ->Connection complete at " << workerToSoldier_socket_connection << 
		" with live status = " << workerToSoldier_socket_is_live << "\n";
	mnvdaq.infoStream() << " ->Connection complete at " << workerToSoldier_socket_connection << 
		" with live status = " << workerToSoldier_socket_is_live;
	minervasleep(100);
#endif // end if MASTER&&(!SINGLEPC)
#if (!MASTER)&&(!SINGLEPC) // Worker Node
	// Initiate connection with "server" (soldier node).  Connect waits for a server response.
	mnvdaq.infoStream() << "Initiate connection with server (soldier node).";
	int conCounter=0;
	int conVal = connect(workerToSoldier_socket_handle, (struct sockaddr*) &workerToSoldier_service, 
		sizeof (struct sockaddr_in));
	mnvdaq.infoStream() << "   conCounter = " << conCounter << " ; conVal = " << conVal;
	while ( (conVal==-1) && conCounter<50) {
		conVal = connect(workerToSoldier_socket_handle, (struct sockaddr*) &workerToSoldier_service, 
			sizeof (struct sockaddr_in));
		conCounter++;
		mnvdaq.infoStream() << "   conCounter = " << conCounter << " ; conVal = " << conVal;
	}
	if (conVal == -1) {
		mnvdaq.fatalStream() << "Error in workerToSoldier connect!";
		perror ("connect"); exit(EXIT_UNSPECIFIED_ERROR);
	} else {
		mnvdaq.infoStream() << "Completed workerToSoldier connect!";
	}
	std::cout << " ->Returned from connect to workerToSoldier!\n";
	mnvdaq.infoStream() << " ->Returned from connect to workerToSoldier!";
	minervasleep(100);
#endif // end if (!MASTER)&&(!SINGLEPC)

	
	// Client-server connect - soldierToWorker. 
	soldierToWorker_socket_is_live = false;
#if (!MASTER)&&(!SINGLEPC) // Worker Node
	std::cout << "\nPreparing make new server connection for soldierToWorker synchronization...\n";
	mnvdaq.infoStream() << "~~~~~~~ Socket Connections";
	mnvdaq.infoStream() << "Preparing make new server connection for soldierToWorker synchronization...";
	mnvdaq.infoStream() << " soldierToWorker_socket_is_live = " << soldierToWorker_socket_is_live; 
	// Accept connection from worker node to supply global gate signalling.
	while (!soldierToWorker_socket_is_live) {
		std::cout << " Waiting for soldier node...\n";
		std::cout << " Ready to connect to soldierToWorker_socket_handle: " << 
			soldierToWorker_socket_handle << std::endl;
		mnvdaq.infoStream() << " Waiting for soldier node...";
		mnvdaq.infoStream() << " Ready to connect to soldierToWorker_socket_handle: " << 
			soldierToWorker_socket_handle;
		struct sockaddr_in remote_address;
		socklen_t address_length;
		address_length = sizeof (remote_address);
		// Accept will wait for a connection...
		soldierToWorker_socket_connection = 
			accept(soldierToWorker_socket_handle, (sockaddr*)&remote_address, &address_length);
		mnvdaq.infoStream() << " soldierToWorker_socket_connection return value = " << soldierToWorker_socket_connection;
		if (soldierToWorker_socket_connection == -1) {
			// The call to accept failed. 
			if (errno == EINTR) {
				// The call was interrupted by a signal. Try again.
				continue;
			} else {
				// Something else went wrong. 
				mnvdaq.fatalStream() << "Error in socket accept!"; 
				perror("accept");
				exit(EXIT_UNSPECIFIED_ERROR);
			}
		}
		soldierToWorker_socket_is_live = true;
	} // end while !soldierToWorker_socket_is_live
	std::cout << " ->Connection complete at " << soldierToWorker_socket_connection << 
		" with live status = " << soldierToWorker_socket_is_live << "\n\n";
	mnvdaq.infoStream() << " ->Connection complete at " << soldierToWorker_socket_connection << 
		" with live status = " << soldierToWorker_socket_is_live;
	minervasleep(100);
#endif // end if (!MASTER)&&(!SINGLEPC)
#if MASTER&&(!SINGLEPC) // Soldier Node
	// Initiate connection with "server" (worker node).  Connect waits for a server response.
	mnvdaq.infoStream() << "Initiate connection with server (worker node).";
	int conCounter=0;
	int conVal = connect(soldierToWorker_socket_handle, (struct sockaddr*) &soldierToWorker_service, 
		sizeof (struct sockaddr_in));
	mnvdaq.infoStream() << "   conCounter = " << conCounter << " ; conVal = " << conVal;
	while ( (conVal==-1) && conCounter<50) {
		conVal = connect(soldierToWorker_socket_handle, (struct sockaddr*) &soldierToWorker_service, 
			sizeof (struct sockaddr_in));
		conCounter++;
		mnvdaq.infoStream() << "   conCounter = " << conCounter << " ; conVal = " << conVal;
	}
	if (conVal == -1) {
		mnvdaq.fatalStream() << "Error in soldierToWorker connect!";
		perror ("connect"); exit(EXIT_UNSPECIFIED_ERROR);
	} else {
		mnvdaq.infoStream() << "Completed soldierToWorker connect!";
	}
	std::cout << " ->Returned from connect to soldierToWorker!\n\n";
	mnvdaq.infoStream() << " ->Returned from connect to soldierToWorker!";
	minervasleep(100);
#endif // end if MASTER&&(!SINGLEPC)


	// Make an acquire data object containing functions for performing initialization and acquisition.
	mnvdaq.infoStream() << "~~~~~~~ Begin Hardware Setup";
	acquire_data *daq = new acquire_data(et_filename, daqAppender, log4cpp::Priority::DEBUG, hardwareInit); 
	mnvdaq.infoStream() << "Got the acquire_data functions.";

	/*********************************************************************************/
	/*      Now initialize the DAQ electronics                                       */
	/*********************************************************************************/
	std::list<readoutObject*> readoutObjects;
#if NEWREADOUT
	daq->InitializeDaq(CONTROLLER_ID, runningMode, &readoutObjects);
	daq->DisplayReadoutObjects(&readoutObjects);
#else
	daq->InitializeDaq(CONTROLLER_ID, runningMode);
#endif
	// Get the controller object created during InitializeDaq.
	controller *currentController = daq->GetController(); 
	// Vector of the CROC's we initialized - we will loop over these when we record data.
	vector<croc*> *croc_vector = currentController->GetCrocVector();
	vector<croc*>::iterator croc_iter = croc_vector->begin();
	// Vector of the CRIM's we initialized - we use these for interrupt & cosmic configuration.
	vector<crim*> *crim_vector = currentController->GetCrimVector();
	vector<crim*>::iterator crim_iter   = crim_vector->begin();
	vector<crim*>::iterator crim_master = crim_vector->begin(); // Use two in case we increment...
	mnvdaq.infoStream() << "Returned from electronics initialization.";

	// Start to setup vars for SAM metadata.
	struct timeval runstart, readend, readstart, debugstart;
	gettimeofday(&runstart, NULL);
	startTime = (unsigned long long)(runstart.tv_sec);
	// Set initial start & stop readout times.
	startReadout = stopReadout  = (unsigned long long)(runstart.tv_sec*1000000) 
		+ (unsigned long long)(runstart.tv_usec);
#if SINGLEPC||MASTER // Single PC or Soldier Node
	firstEvent = GetGlobalGate();
	std::cout << "Opened Event Log, First Event = " << firstEvent << std::endl;
	mnvdaq.infoStream() << "Opened Event Log, First Event = " << firstEvent;
#endif

	/*********************************************************************************/
	/*  At this point we are now set up and are ready to start event acquistion.     */
	/*********************************************************************************/
	// Make the data-taking threads if in multi-threaded operation.
#if THREAD_ME
	boost::thread *data_threads[thread_count];
#endif
#if TAKE_DATA
	std::cout << "Getting ready to start taking data!" << std::endl;
	std::cout << " Attempting to record " << record_gates << " gates.\n" << std::endl;
	mnvdaq.infoStream() << "Getting ready to start taking data!";
	mnvdaq.infoStream() << " Attempting to record " << record_gates << " gates.";

	/*********************************************************************************/
	/* Set up the signal handler so we can always exit cleanly                       */
	/*********************************************************************************/
	struct sigaction quit_action;
	quit_action.sa_handler = quitsignal_handler;
	sigemptyset (&quit_action.sa_mask);
	quit_action.sa_flags = SA_RESTART;		// restart interrupted system calls instead of failing with EINTR
	
	sigaction(SIGINT,  &quit_action, NULL);
	sigaction(SIGTERM, &quit_action, NULL);

	/*********************************************************************************/
	/*      The top of the Event Loop.  Events here are referred to as GATES.        */
	/*      Be mindful of this jargon - in ET, "events" are actually FRAMES.         */
	/*********************************************************************************/
	int  gate            = 0; // Increments only for successful readout. 
	int  triggerCounter  = 0; // Increments on every attempt...
	bool readFPGA        = true; 
	bool zeroSuppress    = false; 
	int  nReadoutADC     = 8;
	continueRunning = true;		// declared in header.
	mnvdaq.infoStream() << "~~~~~~~ Begin Acquisition";
	while ( (gate<record_gates) && continueRunning ) {
		triggerCounter++; // Not a gate counter - this updates trigger type in mixed mode.
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "\t\t\t\tNew Gate";
		mnvdaq.debugStream() << "triggerCounter = " << triggerCounter;
#endif
#if TIME_ME
		struct timeval gate_start_time, gate_stop_time;
		gettimeofday(&gate_start_time, NULL);
#endif
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "->Top of the Readout Loop, starting Gate: " << gate+1;
#endif
		if (!((gate+1)%100)) { std::cout << "   Acquiring Gate: " << gate+1 << std::endl; }
		if (!((gate+1)%10)) { mnvdaq.infoStream() << "   Acquiring Gate: " << gate+1; }
		/**********************************************************************************/
		/*  Initialize the following data members of the event_handler structure.         */
		/*  event_data:                                                                   */
		/*   event_data.feb_info[0-9] 0: link_no, 1: crate_no, 2: croc_no,                */
		/*    3: chan_no, 4: bank 5: buffer length, 6: feb number, 7: firmware, 8: hits   */
		/**********************************************************************************/
		event_data.gate        = 0;  // Set only after successful readout. 
		event_data.triggerTime = 0;  // Set after returning from the Trigger function.
		event_data.readoutInfo = 0;  // Error bits.
		event_data.minosSGATE  = 0;  // MINOS Start GATE in their time coordinates.
		event_data.ledLevel    = (unsigned char)LEDLevel; 
		event_data.ledGroup    = (unsigned char)LEDGroup; 
		for (int i=0;i<9;i++) {
			event_data.feb_info[i] = 0; // Initialize the FEB information block. 
		}
#if SINGLEPC||MASTER // Single PC or Soldier Node
		event_data.globalGate = GetGlobalGate();
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "    Global Gate: " << event_data.globalGate;
#endif
#endif // end if SINGLEPC||MASTER
#if (!MASTER)&&(!SINGLEPC) // Worker Node
		event_data.globalGate = 0; // Don't care, don't use this...
#endif
		// Set the data_ready flag to false, we have not yet taken any data.
		// Don't really use this...
		data_ready = false; 

		// Reset the thread count if in threaded operation.
#if THREAD_ME
		thread_count = 0;
#endif

		/**********************************************************************************/
		/* Trigger the DAQ, threaded or unthreaded.                                       */
		/**********************************************************************************/
		unsigned short int triggerType;
		readFPGA     = true;    // default to reading the FPGA programming registers
		nReadoutADC  = 8;       // default to maximum possible
		zeroSuppress = false;   // default to no suppression.
#if ZEROSUPPRESSION
		zeroSuppress = true;
#endif
		allowedReadoutTime = 0; // default to "infinity"
		// Convert to int should be okay - we only care about the least few significant bits.
		int readoutTimeDiff = (int)stopReadout - (int)startReadout; // stop updated at end of LAST gate.
#if DEBUG_MIXEDMODE
		mnvdaq.debugStream() << "stopReadout  time = " << stopReadout;
		mnvdaq.debugStream() << "startReadout time = " << startReadout;
		mnvdaq.debugStream() << "        time diff = " << readoutTimeDiff;
#endif
#if DEBUG_TIMING&&(!MTEST)
		mnvdaq.debugStream() << "\tReadout Time (previous gate = " << gate << ") = " << readoutTimeDiff;
#endif
#if MTEST
		// We need to reset the external trigger latch for v85 (cosmic) FEB firmware.
		// Precompiler flag here should really be for FEB firmware (i.e., anywhere there 
		// is an "85" equivalent).
		for (croc_iter = croc_vector->begin(); croc_iter != croc_vector->end(); croc_iter++) {
			int crocID = (*croc_iter)->GetCrocID();
			try {
				unsigned char command[] = {0x85};
				int error = daq->WriteCROCFastCommand(crocID, command);
				if (error) throw error;
			} catch (int e) {
				mnvdaq.fatalStream() << "Error for CROC " <<
					((*croc_iter)->GetCrocAddress()>>16) << " for Gate " << gate;
				mnvdaq.fatalStream() << "Cannot write to FastCommand register!";
				std::cout << "Error in minervadaq::main() for CROC " <<
					((*croc_iter)->GetCrocAddress()>>16) << " for Gate " << gate 
					<< std::endl;
				std::cout << "Cannot write to FastCommand register!" << std::endl;
				continueRunning = false;
				break;
			}
		}
#endif

		// don't want to keep going through and possibly spitting out garbage!
		if (!continueRunning)
			break; // exit the gate while loop
			
		switch (runningMode) { 
			case OneShot:
				zeroSuppress = false;   // Never zero suppress pure pedestals.
				triggerType = Pedestal;
				allowedReadoutTime = allowedPedestal;
				break;
			case NuMIBeam:
				triggerType = NuMI;
				allowedReadoutTime = allowedNuMI;
				break;
			case Cosmics:
				// We need to reset the sequencer latch on the CRIM in Cosmic mode...
				// MAKE SURE CRIM FIRMWARE IS COMPATIBLE!
				try {
					int crimID = (*crim_master)->GetCrimID(); // Only the master!
					int error = daq->ResetCRIMSequencerLatch(crimID);
					if (error) throw error;
				} catch (int e) {
					mnvdaq.fatalStream() << "Error for CRIM " << 
						((*crim_master)->GetCrimAddress()>>16) << " for Gate " << gate;
					mnvdaq.fatalStream() << "Cannot reset sequencer latch in Cosmic mode!";
					std::cout << "Error for CRIM " << 
						((*crim_master)->GetCrimAddress()>>16) << " for Gate " << gate
						<< std::endl;
					std::cout << "Cannot reset sequencer latch in Cosmic mode!" << std::endl;
					continueRunning = false;
				}
				triggerType = Cosmic;
				allowedReadoutTime = allowedCosmic;
				break;
			case MTBFBeamMuon:
				// We need to reset the sequencer latch on the CRIM in Cosmic mode...
				// MAKE SURE CRIM FIRMWARE IS COMPATIBLE!
				try {
					int crimID = (*crim_master)->GetCrimID(); // Only the master!
					int error = daq->ResetCRIMSequencerLatch(crimID);
					if (error) throw error;
				} catch (int e) {
					mnvdaq.fatalStream() << "Error for CRIM " << 
						((*crim_master)->GetCrimAddress()>>16) << " for Gate " << gate;
					mnvdaq.fatalStream() << "Cannot reset sequencer latch in Cosmic mode!";
					std::cout << "Error for CRIM " << 
						((*crim_master)->GetCrimAddress()>>16) << " for Gate " << gate
						<< std::endl;
					std::cout << "Cannot reset sequencer latch in Cosmic mode!" << std::endl;
					continueRunning = false;
				}
				triggerType = MTBFMuon;
				allowedReadoutTime = allowedCosmic;
				break;
			case MTBFBeamOnly:
				// We need to reset the sequencer latch on the CRIM in Cosmic mode...
				// MAKE SURE CRIM FIRMWARE IS COMPATIBLE!
				try {
					int crimID = (*crim_master)->GetCrimID(); // Only the master!
					int error = daq->ResetCRIMSequencerLatch(crimID);
					if (error) throw error;
				} catch (int e) {
					mnvdaq.fatalStream() << "Error for CRIM " << 
						((*crim_master)->GetCrimAddress()>>16) << " for Gate " << gate;
					mnvdaq.fatalStream() << "Cannot reset sequencer latch in Cosmic mode!";
					std::cout << "Error for CRIM " << 
						((*crim_master)->GetCrimAddress()>>16) << " for Gate " << gate
						<< std::endl;
					std::cout << "Cannot reset sequencer latch in Cosmic mode!" << std::endl;
					continueRunning = false;
				}
				triggerType = MTBFBeam;
				allowedReadoutTime = allowedCosmic;
				break;
			case PureLightInjection:
				triggerType = LightInjection;
				allowedReadoutTime = allowedLightInjection;
				zeroSuppress = false; // Should always read all boards for LI & Discr. may be off.
				nReadoutADC = 1;      // Deepest only.
				break;
			case MixedBeamPedestal:
				if (triggerCounter%2) { // ALWAYS start with NuMI!
					triggerType = NuMI;
					allowedReadoutTime = allowedNuMI;
				} else {
					if ( readoutTimeDiff < physReadoutMicrosec ) { 
						triggerType = Pedestal;
						allowedReadoutTime = allowedPedestal;
						zeroSuppress = false; // Should always read all boards for peds.
						readFPGA    = false;
					} else {
						triggerType = NuMI; 
						allowedReadoutTime = allowedNuMI;
#if DEBUG_MIXEDMODE
						mnvdaq.debugStream() << "Aborting calib trigger!";
#endif
					}
				}
				break;
			case MixedBeamLightInjection:
				if (triggerCounter%2) { // ALWAYS start with NuMI!
					triggerType = NuMI;
					allowedReadoutTime = allowedNuMI;
				} else {
					if ( readoutTimeDiff < physReadoutMicrosec ) { 
						triggerType = LightInjection;
						allowedReadoutTime = allowedLightInjection;
						zeroSuppress = false; // Should always read all boards for LI.
						nReadoutADC = 1;      // Deepest only.
					} else {
						triggerType = NuMI; 
						allowedReadoutTime = allowedNuMI;
#if DEBUG_MIXEDMODE
						mnvdaq.debugStream() << "Aborting calib trigger!";
#endif
					}
				}
				break; 
			default:
				std::cout << "minervadaq::main(): ERROR! Improper Running Mode = " << runningMode << std::endl;
				mnvdaq.fatalStream() << "Improper Running Mode = " << runningMode;
				continueRunning = false;
		}

		// don't want to keep going through and possibly spitting out garbage!
		if (!continueRunning)
			break; // exit the gate while loop.

		event_data.triggerType  = triggerType;
		soldierToWorker_trig[0] = (unsigned short int)0;
		workerToSoldier_trig[0] = (unsigned short int)0;
#if DEBUG_TIMING&&(!MTEST)
		mnvdaq.debugStream() << "\tTrigger Type = " << triggerType << " for gate " << gate+1;
#endif
		// Synchronize trigger types. TODO - test synch write & listen functions w/ return values...
		//SynchWrite(soldierToWorker_socket_handle, soldierToWorker_trig);  
		//SynchListen(soldierToWorker_socket_connection, soldierToWorker_trig);
#if MASTER&&(!SINGLEPC) // Soldier Node
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeStart = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Starting trigger synch.";
#endif
		// Write trigger type to the worker node	 
		soldierToWorker_trig[0] = triggerType;
		if (write(soldierToWorker_socket_handle,soldierToWorker_trig,sizeof(soldierToWorker_trig)) == -1) {	 
			mnvdaq.fatalStream() << "socket write error: soldierToWorker_trig!";	 
			perror("write error: soldierToWorker_trig");	 
			break;	// break out of main acquisition loop to prevent garbage data taking
		}
		// Read trigger type from the worker node	 
		while (!workerToSoldier_trig[0]) {	 
			int read_val = read(workerToSoldier_socket_connection,workerToSoldier_trig,sizeof(workerToSoldier_trig));	 
			if ( read_val != sizeof(workerToSoldier_trig) ) {	 
				mnvdaq.fatalStream() << "server read error: cannot get workerToSoldier_trig!";
				mnvdaq.fatalStream() << "  socket readback data size = " << read_val;	 
				perror("server read error: workerToSoldier_trig");	 
				continueRunning = false;
				break;
			}
		}
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeEnd = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Finished triggtrigger synch.";
		mnvdaq.debugStream() << "->Required time = " << (debugTimeEnd - debugTimeStart);
#endif
		if (!continueRunning)
			break;

#if DEBUG_SOCKETS
		mnvdaq.debugStream() << "Got the trigger type from the Worker = " << workerToSoldier_trig[0];
#endif 
		if (event_data.triggerType != workerToSoldier_trig[0]) {
			mnvdaq.warnStream() << "Trigger type disagreement between nodes!  Aborting trigger for gate " << (gate+1);
			stopReadout = startReadout; // no readout, so reset counter
			continue;  // Go to beginning of gate loop.
		} 
#endif
#if (!MASTER)&&(!SINGLEPC) // Worker Node
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeStart = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Starting trigger synch.";
#endif
		// Write trigger type to the soldier node	 
		workerToSoldier_trig[0] = triggerType;
		if (write(workerToSoldier_socket_handle,workerToSoldier_trig,sizeof(workerToSoldier_trig)) == -1) {	 
			mnvdaq.fatalStream() << "socket write error: workerToSoldier_trig!";	 
			perror("write error: workerToSoldier_trig");	 
			break;	// break out of main acquisition loop to prevent garbage data taking
		}
		// Read trigger type from the soldier node	 
		while (!soldierToWorker_trig[0]) {	 
			int read_val = read(soldierToWorker_socket_connection,soldierToWorker_trig,sizeof(soldierToWorker_trig));	 
			if ( read_val != sizeof(soldierToWorker_trig) ) {	 
				mnvdaq.fatalStream() << "server read error: cannot get soldierToWorker_trig!";
				mnvdaq.fatalStream() << "  socket readback data size = " << read_val;	 
				perror("server read error: soldierToWorker_trig");	 
				continueRunning = false;
				break;
			}
		}
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeEnd = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Finished trigger synch.";
		mnvdaq.debugStream() << "->Required time = " << (debugTimeEnd - debugTimeStart);
#endif
		if (!continueRunning)
			break;

#if DEBUG_SOCKETS
		mnvdaq.debugStream() << "Got the trigger type from the Soldier = " << soldierToWorker_trig[0];
#endif 
		if (event_data.triggerType != soldierToWorker_trig[0]) {
			mnvdaq.warnStream() << "Trigger type disagreement between nodes!  Aborting trigger for gate " << (gate+1);
			stopReadout = startReadout; // no readout, so reset counter
			continue;  // Go to beginning of gate loop.
		} 
#endif
		// Trigger the DAQ (active communication with the electronics in internal timing modes only).
		// TODO - Have the DAQ handle "timeouts" differently from real VME errors!
		try {
			int error = TriggerDAQ(daq, triggerType, runningMode, currentController);
			if (error) throw error;
		} catch (int e) {
			std::cout << "Warning in minervadaq::main()!  Cannot trigger the DAQ for Gate = " << gate << 
				" and Trigger Type = " << triggerType << std::endl;
			std::cout << "  Error Code = " << e << ".  Skipping this attempt and trying again..." << std::endl;
			mnvdaq.warnStream() << "Warning in minervadaq::main()!  Cannot trigger the DAQ for Gate = " << gate << 
				" and Trigger Type = " << triggerType;
			mnvdaq.warnStream() << "  Error Code = " << e << ".  Skipping this attempt and trying again...";
			// This is subtle... need to be careful with this approach. 
			mnvdaq.fatalStream() << "Not sure how to handle timeouts yet!  Bailing!";
			break;	// break out of main acquisition loop to prevent garbage data taking
		}

#if DEBUG_GENERAL
		mnvdaq.debugStream() << "Returned from TriggerDAQ.";
#endif

		// Make the event_handler pointer.
		event_handler *evt = &event_data;

		// Now update startReadout for the next gate...
		gettimeofday(&readstart, NULL);
		startReadout = (unsigned long long)(readstart.tv_sec*1000000) + 
			(unsigned long long)(readstart.tv_usec);
		event_data.readoutInfo = (unsigned short)0; // No Error

#if NEWREADOUT
		/**********************************************************************************/
		/*                      Execute the "new" readout model.                          */        
		/**********************************************************************************/
		try {
			int error = TakeData(daq, evt, attach, sys_id, &readoutObjects, allowedReadoutTime, 
				readFPGA, nReadoutADC, zeroSuppress);
			if (error) { throw error; }
		} catch (int e) {
			event_data.readoutInfo += (unsigned short)controllerErrCode;
			std::cout << "Error Code " << e << " in minervadaq::main()!  ";
			std::cout << "Cannot TakeData for Gate: " << gate << std::endl;
			mnvdaq.critStream() << "Error Code " << e << " in minervadaq::main()!  ";
			mnvdaq.critStream() << "Cannot TakeData for Gate: " << gate;
			continueRunning = false;  // "Stop" gate loop. (There is no chain loop.)
		}
		gettimeofday(&readend, NULL);
		stopReadout = (unsigned long long)(readend.tv_sec*1000000) + 
			(unsigned long long)(readend.tv_usec);
		readoutTimeDiff = (int)stopReadout - (int)startReadout; 
#if DEBUG_TIMING
		mnvdaq.debugStream() << "Total readout time at end of electronics readout = " << readoutTimeDiff;
#endif
		if (readoutTimeDiff > allowedReadoutTime) {
			event_data.readoutInfo += (unsigned short)1; // "Timeout Error"
			mnvdaq.critStream() << "Readout is taking longer than allowed! -> " 
				<< readoutTimeDiff;
			// No other loop to exit in this model.
		}

#else // NEWREADOUT CHECK
		int croc_id;
		int no_crocs = currentController->GetCrocVectorLength(); 
		/**********************************************************************************/
		/*                      Execute the "old" readout model.                          */        
		/* This model will not receive further *structural* fixes (use the new readout    */
		/* model instead).  GNP 20100518.                                                 */
		/*                                                                                */ 
		/* Loop over crocs and then channels in the system.  Execute TakeData on each     */
		/* Croc/Channel combination of FEB's.  Here we assume that the CROCs are indexed  */
		/* from 1->N.  The routine will fail if this is false!                            */
		/**********************************************************************************/
		// It would be better to iterate over the CROC vector here rather loop over ID's.
		if (continueRunning) {
			for (int i=0; i<no_crocs; i++) {
				croc_id = i+1;
				croc *tmpCroc = currentController->GetCroc(croc_id);
				for (int j=0; j<4 ;j++) { // Loop over FE Chains.
					if ((tmpCroc->GetChannelAvailable(j))&&(tmpCroc->GetChannel(j)->GetHasFebs())) {
						//
						// Threaded Option
						//
#if THREAD_ME
#if TIME_ME
						struct timeval dummy;
						gettimeofday(&dummy,NULL);
						thread_launch_log<<thread_count<<"\t"<<gate<<"\t"
							<<(dummy.tv_sec*1000000+dummy.tv_usec)<<"\t"
							<<(gate_start_time.tv_sec*1000000+gate_start_time.tv_usec)<<endl;
#endif
						data_threads[thread_count] = 
							new boost::thread((boost::bind(&TakeData,boost::ref(daq),boost::ref(evt),croc_id,j,
							thread_count, attach, sys_id)));
#if TIME_ME
						gettimeofday(&dummy,NULL);
						thread_return_log<<thread_count<<"\t"<<gate<<"\t"
							<<(dummy.tv_sec*1000000+dummy.tv_usec)<<"\t"
							<<(gate_start_time.tv_sec*1000000+gate_start_time.tv_usec)<<endl;
#endif
						thread_count++;

						//
						//  Unthreaded option
						//
#elif NO_THREAD
#if DEBUG_GENERAL
						mnvdaq.debugStream() << " Reading CROC Addr: " << (tmpCroc->GetCrocAddress()>>16) << 
							" Index: " << croc_id << " Chain: " << j;
#endif
						try {
							int error = TakeData(daq,evt,croc_id,j,0,attach,sys_id,readFPGA,nReadoutADC);
							if (error) { throw error; }
						} catch (int e) {
							event_data.readoutInfo += (unsigned short)controllerErrCode; 
							std::cout << "Error Code " << e << " in minervadaq::main()!  ";
							std::cout << "Cannot TakeData for Gate: " << gate << std::endl;
							std::cout << "Failed to execute on CROC Addr: " << 
								(tmpCroc->GetCrocAddress()>>16) << " Chain: " << j << std::endl;
							mnvdaq.critStream() << "Error Code " << e << " in minervadaq::main()!  ";
							mnvdaq.critStream() << "Cannot TakeData for Gate: " << gate;
							mnvdaq.critStream() << "Failed to execute on CROC Addr: " << 
								(tmpCroc->GetCrocAddress()>>16) << " Chain: " << j;
							continueRunning = false;  // "Stop" gate loop.
							break;                    // Exit chain loop.
						}
#endif
					} //channel has febs check
				} //channel loop
				if (allowedReadoutTime && (i<(no_crocs-1)) ) { // t==0 -> infinity
					gettimeofday(&readend, NULL);
					stopReadout = (unsigned long long)(readend.tv_sec*1000000) + 
						(unsigned long long)(readend.tv_usec);
					readoutTimeDiff = (int)stopReadout - (int)startReadout; 
#if DEBUG_TIMING
					mnvdaq.debugStream() << "Radout time at end of CROC " << (tmpCroc->GetCrocAddress()>>16) 
						<< " = " << readoutTimeDiff;
#endif
					if (readoutTimeDiff > allowedReadoutTime) {
						event_data.readoutInfo += (unsigned short)1; // "Timeout Error"
						mnvdaq.critStream() << "Readout is taking longer than allowed! -> " 
							<< readoutTimeDiff;
						mnvdaq.critStream() << "Terminating readout at CROC Addr: " << 
							(tmpCroc->GetCrocAddress()>>16);
						break; // Exit croc loop
					}
				}
			} //croc loop
		} //continueRunning Check
#endif // NEWREADOUT CHECK		
		/**********************************************************************************/
		/*   Wait for trigger thread to join in threaded operation.                       */
		/**********************************************************************************/
#if THREAD_ME
		for (int i=0;i<thread_count;i++) {
			data_threads[i]->join();
		}
#endif // endif THREAD_ME

		// Successfully read the electronics, increment the event counter!
		// Record the event counter value into the event data structure.	
		event_data.gate = ++gate; // Record "gate" number.

		/**********************************************************************************/
		/*  Re-enable the IRQ for the next trigger.                                       */
		/**********************************************************************************/
		// Interrupt configuration is already stored in the CRIM objects.
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "Re-enabling global IRQ bits...";
#endif
		// Loop over CRIM indices...
		for (int i=1; i<=currentController->GetCrimVectorLength(); i++) {
			try {
				int error = daq->ResetGlobalIRQEnable(i); 
				if (error) throw error;
			} catch (int e) {
				std::cout << "Error in main!  Failed to ResetGlobalIRQ!";
				std::cout << "  Status code = " << e << std::endl;
				mnvdaq.fatalStream() << "Error in main!  Failed to ResetGlobalIRQ!";
				mnvdaq.fatalStream() << "  Status code = " << e;
				exit (e);
			}
		}

		// The two nodes should share error information to record in the DAQ Header.
		// Cannot start with 0 value (no error state is 0) - set a dummy bit.
		event_data.readoutInfo  += (unsigned short int)0x8;
		soldierToWorker_error[0] = (unsigned short int)0;
		workerToSoldier_error[0] = (unsigned short int)0;
#if MASTER&&(!SINGLEPC) // Soldier Node
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeStart = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Starting error synch.";
#endif
		// Write readout info (errors) to the worker node	 
		soldierToWorker_error[0] = event_data.readoutInfo;
		if (write(soldierToWorker_socket_handle,soldierToWorker_error,sizeof(soldierToWorker_error)) == -1) {	 
			mnvdaq.fatalStream() << "socket write error: soldierToWorker_error!";	 
			perror("write error: soldierToWorker_error");	 
			break;	// break out of main acquisition loop to prevent garbage data taking
		}
		// Read the readout info (errors) from the worker node	 
		while (!workerToSoldier_error[0]) {	 
			int read_val = read(workerToSoldier_socket_connection,workerToSoldier_error,sizeof(workerToSoldier_error));	 
			if ( read_val != sizeof(workerToSoldier_error) ) {	 
				mnvdaq.fatalStream() << "server read error: cannot get workerToSoldier_error!";
				mnvdaq.fatalStream() << "  socket readback data size = " << read_val;	 
				perror("server read error: workerToSoldier_error");	 
				continueRunning = false;
				break;
			}
		}
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeEnd = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Finished error synch.";
		mnvdaq.debugStream() << "->Required time = " << (debugTimeEnd - debugTimeStart);
#endif
		if (!continueRunning)
			break;

#if DEBUG_SOCKETS
		mnvdaq.debugStream() << "Got the error value from the Worker = " << workerToSoldier_error[0];
#endif 
#endif
#if (!MASTER)&&(!SINGLEPC) // Worker Node
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeStart = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Starting error synch.";
#endif
		// Write readout info (errors) to the soldier node	 
		workerToSoldier_error[0] = event_data.readoutInfo;
		if (write(workerToSoldier_socket_handle,workerToSoldier_error,sizeof(workerToSoldier_error)) == -1) {	 
			mnvdaq.fatalStream() << "socket write error: workerToSoldier_error!";	 
			perror("write error: workerToSoldier_error");	 
			break;	// break out of main acquisition loop to prevent garbage data taking
		}
		// Read the readout info (errors) from the soldier node	 
		while (!soldierToWorker_error[0]) {	 
			int read_val = read(soldierToWorker_socket_connection,soldierToWorker_error,sizeof(soldierToWorker_error));	 
			if ( read_val != sizeof(soldierToWorker_error) ) {	 
				mnvdaq.fatalStream() << "server read error: cannot get soldierToWorker_error!";
				mnvdaq.fatalStream() << "  socket readback data size = " << read_val;	 
				perror("server read error: soldierToWorker_error");	 
				continueRunning = false;
				break;
			}
		}
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeEnd = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Finished error synch.";
		mnvdaq.debugStream() << "->Required time = " << (debugTimeEnd - debugTimeStart);
#endif
		if (!continueRunning)
			break;

#if DEBUG_SOCKETS
		mnvdaq.debugStream() << " Got the error value ifrom the Soldier = " << soldierToWorker_error[0];
#endif 
#endif
		// Only first three bits are valid in DAQHeader v5->v8.
		// bit0 = timeout error (both nodes)
		// bit1 = error on crate 0
		// bit2 = error on crate 1
#if MULTIPC 
		event_data.readoutInfo = (unsigned short int)( 0x7 & ( workerToSoldier_error[0] | soldierToWorker_error[0] ) );
#else 
		event_data.readoutInfo &= 0x7;
#endif
#if DEBUG_TIMING
		mnvdaq.debugStream() << "Final set of ErrorFlags =  " << event_data.readoutInfo;
#endif

		// Reset the sequencer latch in v9+ CRIM's; Must do all CRIM's because they get TCALB *independently*. 
		for (crim_iter = crim_vector->begin(); crim_iter != crim_vector->end(); crim_iter++) {
			try {
				int error = daq->ResetSequencerControlLatch((*crim_iter)->GetCrimID());
				if (error) throw error;
			} catch (int e) {
				std::cout << "Error in minervadaq::main()!" << std::endl;
				mnvdaq.critStream() << "Error in minervadaq::main()!";
				continueRunning = false;
			}
		}

		// The soldier node must wait for a "done" signal from the worker node before attaching 
		// the end-of-gate header bank.  We will use a cross-check on the gate value to be sure 
		// the nodes are aligned. TODO - test synch write & listen functions w/ return values... 
		soldierToWorker_gate[0] = 0;
		workerToSoldier_gate[0] = 0;
#if MASTER&&(!SINGLEPC) // Soldier Node
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeStart = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Starting gate synch.";
#endif
		// Write gate to the worker node	 
		soldierToWorker_gate[0] = gate;
		if (write(soldierToWorker_socket_handle,soldierToWorker_gate,sizeof(soldierToWorker_gate)) == -1) {	 
			mnvdaq.fatalStream() << "socket write error: soldierToWorker_gate!";	 
			perror("write error: soldierToWorker_gate");	 
			break;	// break out of main acquisition loop to prevent garbage data taking
		}
		// Read the gate from the worker node	 
		while (!workerToSoldier_gate[0]) {	 
			int read_val = read(workerToSoldier_socket_connection,workerToSoldier_gate,sizeof(workerToSoldier_gate));	 
			if ( read_val != sizeof(workerToSoldier_gate) ) {	 
				mnvdaq.fatalStream() << "server read error: cannot get workerToSoldier_gate!";
				mnvdaq.fatalStream() << "  socket readback data size = " << read_val;	 
				perror("server read error: workerToSoldier_gate");	 
				continueRunning = false;
				break;
			}
		}
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeEnd = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Finished gate synch.";
		mnvdaq.debugStream() << "->Required time = " << (debugTimeEnd - debugTimeStart);
#endif
		if (!continueRunning)
			break;

#if DEBUG_SOCKETS
		mnvdaq.debugStream() << "Got the gate value from the Worker = " << workerToSoldier_gate[0];
#endif 
		if (gate != workerToSoldier_gate[0]) {
			mnvdaq.fatalStream() << "Soldier local gate = " << gate;
			mnvdaq.fatalStream() << "Worker remote gate = " << workerToSoldier_gate[0];
			mnvdaq.fatalStream() << "Gate number disagreement between nodes!  Aborting this subrun!";
			break;  // Exit the gate loop.
		} 
#endif
#if (!MASTER)&&(!SINGLEPC) // Worker Node
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeStart = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Starting gate synch.";
#endif
		// Write gate to the soldier node	 
		workerToSoldier_gate[0] = gate;
		if (write(workerToSoldier_socket_handle,workerToSoldier_gate,sizeof(workerToSoldier_gate)) == -1) {	 
			mnvdaq.fatalStream() << "socket write error: workerToSoldier_gate!";	 
			perror("write error: workerToSoldier_gate");	 
			break;	// break out of main acquisition loop to prevent garbage data taking
		}
		// Read the gate from the soldier node	 
		while (!soldierToWorker_gate[0]) {	 
			int read_val = read(soldierToWorker_socket_connection,soldierToWorker_gate,sizeof(soldierToWorker_gate));	 
			if ( read_val != sizeof(soldierToWorker_gate) ) {	 
				mnvdaq.fatalStream() << "server read error: cannot get soldierToWorker_gate!";
				mnvdaq.fatalStream() << "  socket readback data size = " << read_val;	 
				perror("server read error: soldierToWorker_gate");	 
				continueRunning = false;
				break;
			}
		}
#if DEBUG_TIMING
		gettimeofday(&debugstart, NULL);
		debugTimeEnd = (unsigned long long)(debugstart.tv_sec*1000000) + (unsigned long long)(debugstart.tv_usec);
		mnvdaq.debugStream() << "Finished gate synch.";
		mnvdaq.debugStream() << "->Required time = " << (debugTimeEnd - debugTimeStart);
#endif
		if (!continueRunning)
			break;
		
#if DEBUG_SOCKETS
		mnvdaq.debugStream() << "Got the gate value from the Soldier = " << soldierToWorker_gate[0];
#endif 
		if (gate != soldierToWorker_gate[0]) {
			mnvdaq.fatalStream() << "Worker local gate   = " << gate;
			mnvdaq.fatalStream() << "Soldier remote gate = " << soldierToWorker_gate[0];
			mnvdaq.fatalStream() << "Gate disagreement between nodes!  Aborting this subrun!";
			break;  // Exit the gate loop.
		} 
#endif

		// Get time for end of gate & readout...
		gettimeofday(&readend, NULL);
		stopTime    = (unsigned long long)(readend.tv_sec);
		stopReadout = (unsigned long long)(readend.tv_sec*1000000) + 
			(unsigned long long)(readend.tv_usec);
		// Update readout time diff
		readoutTimeDiff = (int)stopReadout - (int)startReadout;
#if DEBUG_TIMING
		mnvdaq.debugStream() << "Total readout time for this node (possible header value) = " << readoutTimeDiff;
		
#endif
#if SINGLEPC||MASTER // Soldier Node or Singleton
		/*************************************************************************************/
		/* Write the End-of-Event Record to the event_handler and then to the event builder. */
		/*************************************************************************************/
		// Build DAQ Header bank.  
		int bank = 3; //DAQ Data Bank (DAQ Header)
		event_data.feb_info[1] = daq->GetController()->GetID();
		event_data.feb_info[4] = bank; 
		event_data.minosSGATE  = daq->GetMINOSSGATE();
		event_data.readoutTime = readoutTimeDiff;
		event_data.triggerTime = startReadout;
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "Contacting the EventBuilder from Main...";
#endif
		// Contact event builder service.
		daq->ContactEventBuilder(&event_data, -1, attach, sys_id);
#if TIME_ME
		gettimeofday(&gate_stop_time,NULL);
		double duration = (gate_stop_time.tv_sec*1e6+gate_stop_time.tv_usec) - 
			(gate_start_time.tv_sec*1e6+gate_start_time.tv_usec);
		if (!(gate%100)) {
			std::cout << "Start Time: " << (gate_start_time.tv_sec*1000000+gate_start_time.tv_usec) << 
				" Stop Time: " << (gate_stop_time.tv_sec*1e6+gate_start_time.tv_usec) << 
				" Run Time: " << (duration/1e6) << std::endl;
		}
#endif
		// Increment the Global Gate value and log it.
		PutGlobalGate(++event_data.globalGate);
		// Write the SAM File.
		lastEvent = event_data.globalGate - 1; // Fencepost, etc.
		WriteSAM(sam_filename, firstEvent, lastEvent, fileroot,  
			detector, config_filename, runningMode, gate, runNumber, subRunNumber,
			startTime, stopTime);
		WriteLastTrigger(lasttrigger_filename, runNumber, subRunNumber, gate,
			triggerType, event_data.triggerTime);
#endif
	} //end of gates loop

	// Close sockets for multi-PC synchronization.
#if !SINGLEPC
	int cl1 = close(workerToSoldier_socket_handle);
	int cl2 = close(soldierToWorker_socket_handle);
	mnvdaq.infoStream() << "Closing workerToSoldier socket... " << cl1;
	mnvdaq.infoStream() << "Closing soldierToWorker socket... " << cl2;
#endif
	// Report end of subrun...
#if SINGLEPC||MASTER // Single PC or Soldier Node
	mnvdaq.infoStream() << "Sending Frame.";
	sentSentinel = SendSentinel(daq, &event_data, attach, sys_id);
	
	std::cout << " Last Frame Type " << event_data.feb_info[4] << std::endl;
	mnvdaq.infoStream() << " Last Frame Type " << event_data.feb_info[4];
	std::cout << " Last Event = " << lastEvent << std::endl;
	mnvdaq.infoStream() << "Last Event = " << lastEvent;
#endif 
	// Report total run time in awkward units... end of run time == end of last gate time.
	unsigned long long totalstart = ((unsigned long long)(runstart.tv_sec))*1000000 +
                        (unsigned long long)(runstart.tv_usec);
	unsigned long long totalend   = ((unsigned long long)(readend.tv_sec))*1000000 +
                        (unsigned long long)(readend.tv_usec);
	unsigned long long totaldiff  = totalend - totalstart;
	printf(" \n\nTotal acquisition time was %llu microseconds.\n\n",totaldiff);
	mnvdaq.info("Total acquisition time was %llu microseconds.",totaldiff);
#endif // end if TAKE_DATA

	/**********************************************************************************/
	/*       delete the acquire functions                                             */
	/**********************************************************************************/
	delete daq;

#if TIME_ME
	gettimeofday(&stop_time,NULL);
	double duration = (double) (stop_time.tv_sec*1e6+stop_time.tv_usec)-
		(start_time.tv_sec*1e6+start_time.tv_usec);
	cout<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
		<<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<endl;
#endif

	// Clean up the log4cpp file.
	log4cpp::Category::shutdown();

	/**********************************************************************************/
	/*              End of execution.                                                 */
	/*                let the calling process know if sentinel is coming from me      */
	/**********************************************************************************/
	return (sentSentinel) ? EXIT_CLEAN_SENTINEL : EXIT_CLEAN_NOSENTINEL;
}


bool SendSentinel(acquire_data *daq, event_handler *event_data, et_att_id attach, et_sys_id sys_id)
{
	event_data->feb_info[4] = 5; // Sentinel
	return daq->ContactEventBuilder(event_data, 0, attach, sys_id);
}

int TakeData(acquire_data *daq, event_handler *evt, et_att_id attach, et_sys_id sys_id, 
	std::list<readoutObject*> *readoutObjects, const int allowedTime, const bool readFPGA, 
	const int nReadoutADC, const bool zeroSuppress)
{
/*! \fn int TakeData(acquire_data *daq, event_handler *evt, et_att_id attach, et_sys_id sys_id,
 *		std::list<readoutObject*> *readoutObjects, const int allowedTime, const bool readFPGA,
 *		const int nReadoutADC) 
 * 
 * Read the electronics and retrieve all requested data for one gate.
 *
 *  \param *daq, a pointer to the acquire_data object governing this DAQ acquisition
 *  \param *evt, a pointer to the event_handler structure containing information
 *		about the data being handled.
 *  \param attach, the ET attachemnt to which data will be stored
 *  \param sys_id, the ET system handle
 *  \param std::list<readoutObject*> *readoutObjects, a pointer to the list of hardware to be read out.
 *  \param const int allowedTime, the total allowed time to readout an event (if more is taken, readout is 
 *	truncated and an error flag is added to the DAQ Header).
 *  \param const bool readFPGA, a flag that dictates whether we read the FPGA's.
 *  \param const int nReadoutADC, a flag that sets the deepest N hits to be read out.
 */
	int dataTaken = 0;

	try {
		dataTaken = daq->WriteAllData(evt, attach, sys_id, readoutObjects, allowedTime, 
			readFPGA, nReadoutADC, zeroSuppress);
		if (dataTaken) throw dataTaken;
	} catch (int e) {
		std::cout << "Data taking failed in minervadaq main::TakeData!" << std::endl;
		mnvdaq.critStream() << "Data taking failed in minervadaq main::TakeData!";
		return e; 
	}

	return dataTaken;
}


int TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id, int thread, 
	et_att_id  attach, et_sys_id  sys_id, bool readFPGA, int nReadoutADC) 
{ // Be wary of channel / chain naming snafu here too...
/*!
 *  \fn int TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id, int thread,
 *                et_att_id  attach, et_sys_id  sys_id, bool readFPGA, int nReadoutADC)
 *
 *  This function executes the necessary commands to complete an acquisition sequence.
 *
 *  Code is available for threaded and unthreaded operating modes.
 *  
 *  \param *daq, a pointer to the acquire_data object governing this DAQ acquisition
 *  \param *evt, a pointer to the event_handler structure containing information
 *               about the data being handled.
 *  \param croc_id, an integer with the CROC being serviced in this call
 *  \param channel_id, an integer with the channel (really chain) number being serviced in this cal
 *  \param thread, the thread number of this call
 *  \param attach, the ET attachemnt to which data will be stored
 *  \param sys_id, the ET system handle
 *  \param readFPGA, flag that determines whether we read the FPGA programming registers
 *  \param nReadoutADC, number of deepest pipeline hits to read
 * 
 * Returns a success integer (0 for success).
 */
#if TIME_ME
	struct timeval start_time, stop_time;
	gettimeofday(&start_time, NULL);
#endif

	/**********************************************************************************/
	/*  Local croc & crim variables for ease of computational manipulation.           */
	/**********************************************************************************/
	croc     *crocTrial    = daq->GetController()->GetCroc(croc_id);
	channels *channelTrial = daq->GetController()->GetCroc(croc_id)->GetChannel(channel_id);

	// A flag to let us know that we have successfully serviced this channel.  The functions 
	// return "0" if they are successful, so data_taken == true means we have not taken data!
	bool data_taken = true; 

	/**********************************************************************************/
	/* Get the FEB list for this channel and an iterator for the FEB loop.            */
	/**********************************************************************************/
	list<feb*> *feb_list = channelTrial->GetFebList(); //the feb's on this channel
	list<feb*>::iterator feb; //we want to loop over them when we get the chance...

	/**********************************************************************************/
	/*   The loops which govern the acquiring of data from the FEB's.                 */
	/*   The first waits until data is ready.                                         */
	/*   The second executes when data is ready to be acquired from the electronics   */
	/**********************************************************************************/
	while (!data_ready) { continue; } //wait for data to be ready

	while ((data_ready)&&(evt_record_available)) { //wait for data to become available
		//loop over all febs
		for (feb=feb_list->begin(); feb!=feb_list->end(); feb++) { //here it is, the feb loop
			/**********************************************************************************/
			/*          Take all data on the feb                                              */
			/**********************************************************************************/
			try {
				data_taken = daq->TakeAllData((*feb), channelTrial, crocTrial, evt, thread, 
					attach, sys_id, readFPGA, nReadoutADC); 
				if (data_taken) throw data_taken;
			} catch (bool e) {
				std::cout << "Problems taking data on FEB: " << (*feb)->GetBoardNumber() << std::endl;
				std::cout << "Leaving thread servicing CROC: " << (crocTrial->GetCrocAddress()>>16) <<
					" Chain: " << channel_id << std::endl;
				mnvdaq.critStream() << "Problems taking data on FEB: " << (*feb)->GetBoardNumber();
				mnvdaq.critStream() << "Leaving thread servicing CROC: " << (crocTrial->GetCrocAddress()>>16) <<
					" Chain: " << channel_id;
				return 1; 
			}
		} //feb loop
#if TIME_ME
		boost::mutex::scoped_lock lock(main_mutex); 
		gettimeofday(&stop_time,NULL);
		double duration = (double) (stop_time.tv_sec*1e6+stop_time.tv_usec) - 
			(start_time.tv_sec*1e6+start_time.tv_usec);
		take_data_extime_log << evt->gate << "\t" << thread << "\t" << 
			(start_time.tv_sec*1000000+start_time.tv_usec) << "\t" << 
			(stop_time.tv_sec*1000000+stop_time.tv_usec) << endl;
#endif

		if (!data_taken) { return 0; } //we're done processing this channel
	} //data ready loop
	return 0;
} // end TakeData


int TriggerDAQ(acquire_data *daq, unsigned short int triggerType, RunningModes runningMode, controller *tmpController) 
{
/*! \fn int TriggerDAQ(acquire_data *data, unsigned short int triggerType)
 *
 *  The function which arms and sets the trigger for each gate (really, it is setting the 
 *  data type for the gate).  Only for the OneShot mode does this involve "triggering" the 
 *  CRIMs.  In the other running modes, the gate signals are initiated by an external source.  
 *  In all running modes, we must handle the interrupt signals generated on the CRIM though.  
 *  Because trigger types are not unique to running modes (e.g., we take both pedestal and 
 *  numi spill triggers in MixedBeamPedestal mode), we need to know both.  For some gates 
 *  (e.g. OneShot), we will need to send software triggers on all CRIMs for pedestal triggers 
 *  and for others (e.g. MixedBeamPedestal), we will only want to trigger the master CRIM.  
 *  Synchronization must be provided by an electrical connection in this case!  This scheme 
 *  will only work for v8 CRIM firmware.
 *
 *  \param *daq a pointer to the acquire_data object which governs this DAQ Execution.
 *  \param triggerType Identifies the gate data type (trigger type).
 *  \param runningMode Identifies the mode of the subrun.
 *  \param *tmpController Pointer to the controller object (for accessing all CRIMs).
 *
 * Returns a status integer (0 for success).
 */
#if TIME_ME
	struct timeval start_time, stop_time;
	gettimeofday(&start_time, NULL);
	if (!trigger_log.is_open()) {
		trigger_log.open("trigger_thread_log.csv");
	}
#endif
#if DEBUG_GENERAL
	mnvdaq.debugStream() << " ->Setting Trigger: " << triggerType;
#endif

	/***********************************************************************************/
	/* NOTE: For running mode == OneShot, we need to issue a software trigger on each  */
	/* CRIM.  For other running modes, the trigger is either external or issued by the */
	/* "master" CRIM.  For single PC mode, the master CRIM is the card with the lowest */
	/* address.  For the multi-PC mode, the master CRIM is the card in Crate 0 with    */
	/* the lowest address (or, at least the CRIM at the beginning of the CRIM vector). */ 
	/***********************************************************************************/
	vector<crim*> *crim_vector = tmpController->GetCrimVector(); 
	vector<crim*>::iterator crim = crim_vector->begin(); 
	int id = (*crim)->GetCrimID(); // Point to "master."
	// Now "Trigger"
	switch (runningMode) {
		case OneShot:
			for (crim = crim_vector->begin(); crim != crim_vector->end(); crim++) {
				id = (*crim)->GetCrimID();
				try {
					int error = daq->TriggerDAQ(triggerType, id);
					if (error) throw error;
				} catch (int e) {
					std::cout << "Error in minervadaq::TriggerDAQ()!" << std::endl;
					mnvdaq.critStream() << "Error in minervadaq::TriggerDAQ()!";
					return e;
				}
			}  
			try {
				int error = daq->WaitOnIRQ();    // wait for the trigger to be set (only returns if successful)
				if (error) throw error;
			} catch (int e) {
				std::cout << "Warning in minervadaq::TriggerDAQ!  IRQ Wait failed or timed out!" << std::endl;
				mnvdaq.warnStream() << "Warning in minervadaq::TriggerDAQ!  IRQ Wait failed or timed out!";
				return e;
			}
			break;
		case NuMIBeam:
		case Cosmics:
		case PureLightInjection:
		case MixedBeamPedestal:
		case MixedBeamLightInjection:
		case MTBFBeamMuon:
		case MTBFBeamOnly:
#if MASTER||SINGLEPC // Soldier Node or singleton...
			try {
				int error = daq->TriggerDAQ(triggerType, id); 
				if (error) throw error;
			} catch (int e) {
				std::cout << "Error in minervadaq::TriggerDAQ()!" << std::endl;
				mnvdaq.critStream() << "Error in minervadaq::TriggerDAQ()!";
				return e;
			}
#endif
			try {
				int error = daq->WaitOnIRQ();    // wait for the trigger to be set (only returns if successful)
				if (error) throw error;
			} catch (int e) {
				std::cout << "Warning in minervadaq::TriggerDAQ!  IRQ Wait failed or timed out!" << std::endl;
				mnvdaq.warnStream() << "Warning in minervadaq::TriggerDAQ!  IRQ Wait failed or timed out!";
				return e;
			}
			break;
		default:
			std::cout << "ERROR! Improper Running Mode = " << runningMode << std::endl;
			mnvdaq.critStream() << "Improper Running Mode defined = " << runningMode;
			return -4;
	}

#if ASSERT_INTERRUPT
	/**********************************************************************************/
	/*  Let the interrupt handler deal with an asserted interrupt.                    */
	/**********************************************************************************/
	try {
		int error = daq->AcknowledgeIRQ(); //acknowledge the IRQ (only returns if successful)
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in minervadaq::TriggerDAQ!  IACK error!" << std::endl;
		mnvdaq.critStream() << "Error in minervadaq::TriggerDAQ!  IACK error!";
		return e;
	}
#endif

#if DEBUG_GENERAL
	mnvdaq.debugStream() << " Data Ready! ";
#endif
#if RUN_SLEEPY
	// This sleep is here because we return too quickly - the FEBs are still digitizing.
	// Digitization takes ~300 microseconds.  All of our time function options 
	// for sleep vary as a function of OS scheduling issues and none are very stable.
	// A tight sleep time can only really affect MTest since it is only called once per gate.
#if defined(HAVE_NANOSLEEP)
	timespec tmReq;
	tmReq.tv_sec = (time_t)(0);
	tmReq.tv_nsec = 300 * 1000;
	(void)nanosleep(&tmReq, (timespec *)NULL); // Typically ~1 ms (sometimes ~2).
#else
	usleep(300); // Typically ~1 ms (sometimes ~2).
#endif
#endif // run sleepy

	// Tell the data acquiring threads that data is available for processing.	
	data_ready = true; 

#if TIME_ME
	gettimeofday(&stop_time,NULL);
	double duration =(double) (stop_time.tv_sec*1000000+stop_time.tv_usec)-
		(start_time.tv_sec*1000000+start_time.tv_usec);
	trigger_log<<(start_time.tv_sec*1000000+start_time.tv_usec)<<"\t"
		<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<"\t"<<(duration/1000000)<<endl;
#endif
	return 0;
} // end TriggerDAQ


unsigned long long GetGlobalGate()
{                       
/*! \fn unsigned long long GetGlobalGate()
 *
 * This function gets the value of the global gate from the data file used for tracking.  
 * On mnvdaq build machines, that file is: /work/conditions/global_gate.dat.              
 */
	unsigned long long ggate;
	fstream global_gate("/work/conditions/global_gate.dat");
	try {
		if (!global_gate) throw (!global_gate);
		global_gate >> ggate;
	} catch (bool e) {
		std::cout << "Error in minervadaq::main opening global gate data!\n";
		mnvdaq.fatalStream() << "Error opening global gate data!";
		continueRunning = false;
	}
	global_gate.close();
	return ggate;
} 


void PutGlobalGate(unsigned long long ggate)
{
/*! \fn void PutGlobalGate(unsigned long long ggate)
 *
 * This funciton writes a new value into the global gate data log.
 * On mnvdaq build machines, that file is: /work/conditions/global_gate.dat.              
 */
	fstream global_gate("/work/conditions/global_gate.dat");
	try {
		if (!global_gate) throw (!global_gate);
		global_gate << ggate;
	} catch (bool e) {
		std::cout << "Error in minervadaq::main opening global gate data!" << std::endl;
		mnvdaq.fatalStream() << "Error opening global gate data!";
		continueRunning = false;
	}
	global_gate.close();
}


int CreateSocketPair(int &workerToSoldier_socket_handle, int &soldierToWorker_socket_handle )
{
/*! \fn void CreateSocketPair(int &workerToSoldier_socket_handle, int &soldierToWorker_socket_handle )
 * 
 * This function creates a pair of sockets for gate synchronization between a pair of MINERvA 
 * DAQ nodes.
 */
	workerToSoldier_socket_handle = socket (PF_INET, SOCK_STREAM, 0);
	soldierToWorker_socket_handle = socket (PF_INET, SOCK_STREAM, 0);
	if (workerToSoldier_socket_handle == -1) { 
		perror("socket"); 
		mnvdaq.fatalStream() << "workerToSoldier_socket_handle == -1!";
		return 1; 
	}
	if (soldierToWorker_socket_handle == -1) { 
		perror("socket"); 
		mnvdaq.fatalStream() << "soldierToWorker_socket_handle == -1!";
		return 1; 
	}
	mnvdaq.infoStream() << "Soldier/Master-node Multi-PC workerToSoldier_socket_handle: " <<
		workerToSoldier_socket_handle;
	mnvdaq.infoStream() << "Soldier/Master-node Multi-PC soldierToWorker_socket_handle: " <<
		soldierToWorker_socket_handle;
	return 0; // success
}


int SetupSocketService(struct sockaddr_in &socket_service, struct hostent *node_info, 
        std::string hostname, const int port )
{
/*! \fn void SetupSocketService(struct sockaddr_in &socket_service, struct hostent *node_info,
 *		std::string hostname, const int port )
 *
 * This function sets up a socket service.
 */
	socket_service.sin_family = AF_INET;
	node_info = gethostbyname(hostname.c_str());
	if (node_info == NULL) {
		mnvdaq.fatalStream() << "No node to connect to at " << hostname;
		std::cout << "No worker node to connect to at " << hostname << std::endl; 
		return 1; 
	}
	else socket_service.sin_addr = *((struct in_addr *) node_info->h_addr);
	socket_service.sin_port = htons(port); 
	mnvdaq.infoStream() << "Set up socket service on port " << port;
	return 0; // success
}

int WriteSAM(const char samfilename[], 
	const unsigned long long firstEvent, const unsigned long long lastEvent, 
	const string datafilename, const int detector, const char configfilename[], 
	const int runningMode, const int eventCount, const int runNum, const int subNum,  
	const unsigned long long startTime, const unsigned long long stopTime)
{
/*! \fn int WriteSAM(const char samfilename[], 
 * 		const unsigned long long firstEvent, const unsigned long long lastEvent,
 *		const string datafilename, const int detector, const char configfilename[],
 *		const int runningMode, const int eventCount,
 *		const unsigned long long startTime, const unsigned long long stopTime)
 *
 * Write the metadata file for the current subrun.  Returns a success int (0 for success).
 */
	FILE *sam_file;

	if ( (sam_file=fopen(samfilename,"w")) ==NULL) {
		std::cout << "minervadaq::main(): Error!  Cannot open SAM file for writing!" << std::endl;
		mnvdaq.fatalStream() << "Error opening SAM file for writing!";
		return 1;
	}

	fprintf(sam_file,"from SamFile.SamDataFile import SamDataFile\n\n");
	fprintf(sam_file,"from SamFile.SamDataFile import ApplicationFamily\n");
	fprintf(sam_file,"from SamFile.SamDataFile import CRC\n");
	fprintf(sam_file,"from SamFile.SamDataFile import SamTime\n");
	fprintf(sam_file,"from SamFile.SamDataFile import RunDescriptorList\n");
	fprintf(sam_file,"from SamFile.SamDataFile import SamSize\n\n");
	fprintf(sam_file,"import SAM\n\n");
	fprintf(sam_file,"metadata = SamDataFile(\n");
	fprintf(sam_file,"fileName = '%s_RawData.dat',\n",datafilename.c_str());
	fprintf(sam_file,"fileType = SAM.DataFileType_ImportedDetector,\n");
	fprintf(sam_file,"fileFormat = 'binary',\n");
	fprintf(sam_file,"crc=CRC(666L,SAM.CRC_Adler32Type),\n");
	fprintf(sam_file,"group='minerva',\n");
#if MTEST
	fprintf(sam_file,"dataTier='binary-raw-test',\n");
#else
	fprintf(sam_file,"dataTier='binary-raw',\n");
#endif
	fprintf(sam_file,"runNumber=%d%04d,\n",runNum,subNum);
	fprintf(sam_file,"applicationFamily=ApplicationFamily('online','v09','v07-07-07'),\n"); //online, DAQ Heder, CVSTag
	fprintf(sam_file,"fileSize=SamSize('0B'),\n");
	fprintf(sam_file,"filePartition=1L,\n");
	switch (detector) { // Enumerations set by the DAQHeader class.
		case 0:
			fprintf(sam_file,"runType='unknowndetector',\n");
			break;
		case 1:
			fprintf(sam_file,"runType='pmtteststand',\n");
			break;
		case 2:
			fprintf(sam_file,"runType='trackingprototype',\n");
			break;
		case 4:
			fprintf(sam_file,"runType='testbeam',\n");
			break;
		case 8:
			fprintf(sam_file,"runType='frozendetector',\n");
			break;
		case 16:
			fprintf(sam_file,"runType='upstreamdetector',\n");
			break;
		case 32:
			fprintf(sam_file,"runType='minerva',\n");
			break;
		default:
			std::cout << "minervadaq::WriteSAM(): ERROR! Improper Detector defined!" << std::endl;
			mnvdaq.critStream() << "minervadaq::WriteSAM(): ERROR! Improper Detector defined!";
			return 1;
	}
	fprintf(sam_file,"params = Params({'Online':CaseInsensitiveDictionary");
	fprintf(sam_file,"({'triggerconfig':'%s',",configfilename);
	switch (runningMode) {
		case 0: //OneShot:
			fprintf(sam_file,"'triggertype':'oneshot',})}),\n");
			fprintf(sam_file,"datastream='pdstl',\n");
			break;
		case 1: //NuMIBeam:
			fprintf(sam_file,"'triggertype':'numibeam',})}),\n");
			fprintf(sam_file,"datastream='numib',\n");
			break;
		case 2: //Cosmics:
			fprintf(sam_file,"'triggertype':'cosmics',})}),\n");
			fprintf(sam_file,"datastream='cosmc',\n");
			break;
		case 3: //PureLightInjection:
			fprintf(sam_file,"'triggertype':'purelightinjection',})}),\n");
			fprintf(sam_file,"datastream='linjc',\n");
			break;
		case 4: //MixedBeamPedestal:
			fprintf(sam_file,"'triggertype':'mixedbeampedestal',})}),\n");
			fprintf(sam_file,"datastream='numip',\n");
			break;
		case 5: //MixedBeamLightInjection:
			fprintf(sam_file,"'triggertype':'mixedbeamlightinjection',})}),\n");
			fprintf(sam_file,"datastream='numil',\n");
			break;
		case 6: //MTBFBeamMuon:
			fprintf(sam_file,"'triggertype':'mtbfbeammuon',})}),\n");
			fprintf(sam_file,"datastream='bmuon',\n");
			break;
		case 7: //MTBFBeamOnly:
			fprintf(sam_file,"'triggertype':'mtbfbeamonly',})}),\n");
			fprintf(sam_file,"datastream='bonly',\n");
			break;
		default:
			std::cout << "minervadaq::WriteSAM(): ERROR! Improper Running Mode defined!" << std::endl;
			mnvdaq.critStream() << "minervadaq::WriteSAM(): ERROR! Improper Running Mode defined!";
			return 1;
	}
	fprintf(sam_file,"startTime=SamTime('%llu',SAM.SamTimeFormat_UTCFormat),\n", startTime);
	fprintf(sam_file,"endTime=SamTime('%llu',SAM.SamTimeFormat_UTCFormat),\n", stopTime);
	fprintf(sam_file,"eventCount=%d,\n",eventCount);
	fprintf(sam_file,"firstEvent=%llu,\n",firstEvent);
	fprintf(sam_file,"lastEvent=%llu,\n",lastEvent);
	fprintf(sam_file,"lumBlockRangeList=LumBlockRangeList([LumBlockRange(%llu,%llu)])\n", firstEvent, lastEvent);
	fprintf(sam_file,")\n");
	fclose(sam_file);

	return 0;
}

int WriteLastTrigger(const char filename[], const int run, const int subrun,
	const unsigned long long triggerNum, const int triggerType,
	const unsigned long long triggerTime)
/*! \fn int WriteLastTrigger(const int run, const int subrun,
 *        const char filename[], const unsigned long long triggerNum, 
 *		const int triggerType, const unsigned int triggerType
 *
 * Write the last trigger information to a file.  Returns a success int (0 for success).
 */
{
	FILE *file;

	if ( (file=fopen(filename,"w")) ==NULL) {
		std::cout << "minervadaq::main(): Error!  Cannot open last trigger file for writing!" << std::endl;
		mnvdaq.warnStream() << "Error opening last trigger file for writing!";
		return 1;
	}
	else
		mnvdaq.infoStream() << "Writing info for trigger " << triggerNum << " to file " << filename;

	fprintf(file, "run=%d\n",      run);
	fprintf(file, "subrun=%d\n",   subrun);
	fprintf(file, "number=%llu\n", triggerNum);
	fprintf(file, "type=%d\n",     triggerType);
	fprintf(file, "time=%llu\n",   triggerTime);
	
	fclose(file);
	
	return 0;
}

template <typename Any> int SynchWrite(int socket_handle, Any data[])
{
#if DEBUG_SOCKETS
	mnvdaq.debugStream() << " Entering SynchWrite for handle " << socket_handle << " and data " << data[0];
#endif          
	if (write(socket_handle,data,sizeof(data)) == -1) {
		mnvdaq.fatalStream() << "socket write error: SynchWrite!";
		perror("write error");
		continueRunning = false;
	}
#if DEBUG_SOCKETS
	mnvdaq.debugStream() << " Finished SynchWrite.";
#endif 
	return 0; // success
}


template <typename Any> int SynchListen(int socket_connection, Any data[])
{
#if DEBUG_SOCKETS
	mnvdaq.debugStream() << " Reading data in SynchListen...";
#endif          
	while (!data[0]) { 
		int read_val = read(socket_connection, data, sizeof(data));
		if ( read_val != sizeof(data) ) {
			mnvdaq.fatalStream() << "Server read error in SynchListen!";
			perror("server read error: done");
			continueRunning = false;
			break;
		}
#if DEBUG_SOCKETS
		mnvdaq.debugStream() << "  ->After read, new data: " << data[0];
#endif
	}
	return 0; // success
}

void quitsignal_handler(int signum)
/*! \fn void quitsignal_handler(int signum)
 *
 * Handles the SIGINT & SIGNUM signals (both of which should exit the process)
 * by setting a flag that tells the main loop to quit.  This ensures we always
 * get a clean close and that the sentinel gate is always put into the stream
 * (except in cases of hard crashes of this program).
 */
{
	continueRunning = false;
}


int minervasleep(int us) 
{
#if defined(HAVE_NANOSLEEP)
	timespec tmReq;
	tmReq.tv_sec = (time_t)(0);
	tmReq.tv_nsec = us * 1000;
	(void)nanosleep(&tmReq, (timespec *)NULL); // Typically ~1 ms (sometimes ~2).
#else   
	usleep(us); 
#endif          
	return 0;
}
