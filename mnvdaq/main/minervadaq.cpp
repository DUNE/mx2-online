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
	bool success             = false;     // Success state of the DAQ at exit,
	int record_gates         = -1;        // Run length in GATES.
	RunningModes runningMode = OneShot;
	int runMode              = 0;         // Same as OneShot...
	int runNumber            = 938;       // MINERvA!
	int subRunNumber         = 11;        // It goes to 11...
	int record_seconds       = -1;	      // Run length in SECONDS (Not Supported...)
	int detector             = 0;         // Default to UnknownDetector.
	int detectorConfig       = 0;
	int LEDLevel             = 0;
	int LEDGroup             = 0;
	int hardwareInit         = 1;         // Default to "init." (This will set VME card timing modes, etc., but not touch FEB's).
	string fileroot          = "testme";  // For logs, etc.  
	string strtemp           = "unknown"; // For SAM, temp.
	char config_filename[100]; sprintf(config_filename,"unknown"); // For SAM.
	string et_filename       = "/work/data/etsys/testme_RawData";  
	string log_filename      = "/work/data/logs/testme_Log.txt"; 
	char sam_filename[100]; sprintf(sam_filename,"/work/data/sam/testme_SAM.py");
	char data_filename[100]; sprintf(data_filename,"/work/data/sam/testme_RawData.dat");
	unsigned long long firstEvent, lastEvent;
	int networkPort          = 1091; // 1091-1096 (inclusive) currently open.
	int controllerErrCode;
	string str_controllerID  = "0";
#if MASTER||SINGLEPC // Soldier Node
	str_controllerID  = "0";
	controllerErrCode = 2;
#elif (!MASTER)&&(!SINGLEPC) // Worker Node
	str_controllerID  = "1";
	controllerErrCode = 4;
#endif
	unsigned long long startTime, stopTime;        // For SAM.  Done at second & microsecond-level precision.
	unsigned int       startReadout, stopReadout;  // For gate monitoring.  Done at second-level precision.

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
#if MULTIPC
	mnvdaq.infoStream() << "Configured for a Multi-PC Build...";	
#if MASTER
	mnvdaq.infoStream() << "->Configured as a Soldier Node...";	
#else
	mnvdaq.infoStream() << "->Configured as a Worker Node...";	
#endif
#endif
#if SINGLEPC
	mnvdaq.infoStream() << "Configured for a Single-PC Build...";	
#endif

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


	/*********************************************************************************/
	/* Now set up ET for use in writing the first-pass memory mapped data file.      */
	/*********************************************************************************/
	et_att_id      attach;
	et_sys_id      sys_id;
	et_id          *id;  // Unused in main?
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
		exit(1);
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
		exit(1);
	} 
	mnvdaq.infoStream() << "Successfully attached to GRANDCENTRAL Station.";	


	/*********************************************************************************/
	/*  Basic Socket Configuration for Worker && Soldier Nodes.                      */
	/*********************************************************************************/
#if MULTIPC
	workerToSoldier_port   += (unsigned short)(subRunNumber % 4); 
	soldierToWorker_port += (unsigned short)(subRunNumber % 4);
	mnvdaq.infoStream() << "Gate-Done Network Port   = " << workerToSoldier_port;
	mnvdaq.infoStream() << "Global-Gate Network Port = " << soldierToWorker_port;
#endif
#if MASTER&&(!SINGLEPC) // Soldier Node
	// Create a TCP socket.
	CreateSocketPair(workerToSoldier_socket_handle, soldierToWorker_socket_handle);
	// Set up the soldierToWorker service.
	SetupSocketService(soldierToWorker_service, worker_node_info, workerName, soldierToWorker_port ); 
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
		perror ("bind"); exit(EXIT_FAILURE); 
	} else {
		mnvdaq.infoStream() << "Finished binding the workerToSoldier socket.";
	}
	// Enable connection requests on the workerToSoldier socket for the listener.
	if (listen (workerToSoldier_socket_handle, 10)) { 
		mnvdaq.fatalStream() << "Error listening on the workerToSoldier socket!"; 
		perror("listen"); exit(EXIT_FAILURE); 
	} else {
		mnvdaq.infoStream() << "Enabled listening on the workerToSoldier socket.";
	}
#endif // end if MASTER&&(!SINGLEPC)

#if (!MASTER)&&(!SINGLEPC) // Worker Node
	CreateSocketPair(workerToSoldier_socket_handle, soldierToWorker_socket_handle);
	// Set up the workerToSoldier service. 
	SetupSocketService(workerToSoldier_service, soldier_node_info, soldierName, workerToSoldier_port ); 
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
		perror ("bind"); exit(EXIT_FAILURE); 
	} else {
		mnvdaq.infoStream() << "Finished binding the soldierToWorker socket.";
	}
	// Enable connection requests on the global socket for the listener.
	if (listen (soldierToWorker_socket_handle, 10)) { 
		mnvdaq.fatalStream() << "Error listening on the soldierToWorker socket!"; 
		perror("listen"); exit(EXIT_FAILURE); 
	} else {
		mnvdaq.infoStream() << "Enabled listening on the soldierToWorker socket.";
	}
#endif // end if (!MASTER)&&(!SINGLEPC)


	// Client-server connect - workerToSoldier. 
	workerToSoldier_socket_is_live = false;
#if MASTER&&(!SINGLEPC) // Soldier Node
	std::cout << "\nPreparing make new server connection for workerToSoldier synchronization...\n";
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
		if (workerToSoldier_socket_connection == -1) {
			// The call to accept failed. 
			if (errno == EINTR) {
				// The call was interrupted by a signal. Try again.
				continue;
			} else {
				// Something else went wrong.
				mnvdaq.fatalStream() << "Error in socket accept!"; 
				perror("accept");
				exit(EXIT_FAILURE);
			}
		}
		workerToSoldier_socket_is_live = true;
	} // end while !workerToSoldier_socket_is_live
	std::cout << " ->Connection complete at " << workerToSoldier_socket_connection << 
		" with live status = " << workerToSoldier_socket_is_live << "\n";
	mnvdaq.infoStream() << " ->Connection complete at " << workerToSoldier_socket_connection << 
		" with live status = " << workerToSoldier_socket_is_live;
#endif // end if MASTER&&(!SINGLEPC)
#if (!MASTER)&&(!SINGLEPC) // Worker Node
	// Initiate connection with "server" (soldier node).  Connect waits for a server response.
	if (connect(workerToSoldier_socket_handle, (struct sockaddr*) &workerToSoldier_service, 
			sizeof (struct sockaddr_in)) == -1) { 
		mnvdaq.fatalStream() << "Error in workerToSoldier connect!";
		perror ("connect"); exit(EXIT_FAILURE); 
	}
	std::cout << " ->Returned from connect to workerToSoldier!\n";
	mnvdaq.infoStream() << " ->Returned from connect to workerToSoldier!";
#endif // end if (!MASTER)&&(!SINGLEPC)

	
	// Client-server connect - soldierToWorker. 
	soldierToWorker_socket_is_live = false;
#if MASTER&&(!SINGLEPC) // Soldier Node
	// Initiate connection with "server" (worker node).  Connect waits for a server response.
	if (connect(soldierToWorker_socket_handle, (struct sockaddr*) &soldierToWorker_service, 
			sizeof (struct sockaddr_in)) == -1) { 
		mnvdaq.fatalStream() << "Error in soldierToWorker connect!";
		perror ("connect"); exit(EXIT_FAILURE); 
	}
	std::cout << " ->Returned from connect to soldierToWorker!\n\n";
	mnvdaq.infoStream() << " ->Returned from connect to soldierToWorker!";
#endif // end if MASTER&&(!SINGLEPC)
#if (!MASTER)&&(!SINGLEPC) // Worker Node
	std::cout << "\nPreparing make new server connection for soldierToWorker synchronization...\n";
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
		if (soldierToWorker_socket_connection == -1) {
			// The call to accept failed. 
			if (errno == EINTR) {
				// The call was interrupted by a signal. Try again.
				continue;
			} else {
				// Something else went wrong. 
				mnvdaq.fatalStream() << "Error in socket accept!"; 
				perror("accept");
				exit(EXIT_FAILURE);
			}
		}
		soldierToWorker_socket_is_live = true;
	} // end while !soldierToWorker_socket_is_live
	std::cout << " ->Connection complete at " << soldierToWorker_socket_connection << 
		" with live status = " << soldierToWorker_socket_is_live << "\n\n";
	mnvdaq.infoStream() << " ->Connection complete at " << soldierToWorker_socket_connection << 
		" with live status = " << soldierToWorker_socket_is_live;
#endif // end if (!MASTER)&&(!SINGLEPC)


	// Make an acquire data object containing functions for performing initialization and acquisition.
	acquire_data *daq = new acquire_data(et_filename, daqAppender, log4cpp::Priority::DEBUG, hardwareInit); 
	mnvdaq.infoStream() << "Got the acquire_data functions.";

	/*********************************************************************************/
	/*      Now initialize the DAQ electronics                                       */
	/*********************************************************************************/
#if THREAD_ME //TODO - Arguments probably wrong for threaded function here...
	boost::thread electronics_init_thread(boost::bind(&acquire_data::InitializeDaq,daq)); 
#else
	daq->InitializeDaq(CONTROLLER_ID, runningMode);
#endif // end if THREAD_ME
#if THREAD_ME
	electronics_init_thread.join(); //wait for the electronics initialization to finish 
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
	struct timeval runstart, gatend, gatestart;
	gettimeofday(&runstart, NULL);
	startTime = (unsigned long long)(runstart.tv_sec);
	// Set initial start & stop readout times.
	startReadout = stopReadout  = (runstart.tv_sec);
#if SINGLEPC||MASTER // Single PC or Soldier Node
	global_gate_data[0] = GetGlobalGate();
	std::cout << "Opened Event Log, First Event = " << global_gate_data[0] << std::endl;
	mnvdaq.infoStream() << "Opened Event Log, First Event = " << global_gate_data[0];
	firstEvent = global_gate_data[0];
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
	/*      The top of the Event Loop.  Events here are referred to as GATES.        */
	/*      Be mindful of this jargon - in ET, "events" are actually FRAMES.         */
	/*********************************************************************************/
	int  gate            = 0; // Increments only for successful readout. 
	int  triggerCounter  = 0; // Increments on every attempt...
	bool readFPGA        = true; 
	int  nReadoutADC     = 8;
	bool continueRunning = true;
	while ( (gate<record_gates) && continueRunning ) {
		triggerCounter++; // Not a gate counter - this updates trigger type in mixed mode.
		//continueRunning = true; //reset? TODO - fix
#if TIME_ME
		struct timeval gate_start_time, gate_stop_time;
		gettimeofday(&gate_start_time, NULL);
#endif
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "->Top of the Event Loop, starting Gate: " << gate;
#endif
		if (!((gate+1)%100)) { std::cout << "   Acquiring Gate: " << gate+1 << std::endl; }
		if (!((gate+1)%10)) { mnvdaq.infoStream() << "   Acquiring Gate: " << gate+1; }
		/**********************************************************************************/
		/*  Initialize the following data members of the event_handler structure          */
		/*    event_data:                                                                 */
		/*       event_data.feb_info[0-9] 0: link_no, 1: crate_no, 2: croc_no,            */
		/*                                  3: chan_no, 4: bank 5: buffer length          */
		/*                                  6: feb number, 7: feb firmware, 8: hits       */
		/**********************************************************************************/
		event_data.gate        = 0;  // Set only after successful readout. // TODO - Special value for failures?
		event_data.triggerTime = 0;  // Set after returning from the Trigger function.
		event_data.readoutInfo = 0;  // Error bits.
		event_data.minosSGATE  = 0;  // MINOS Start GATE in their time coordinates.
		event_data.ledLevel    = (unsigned char)LEDLevel; 
		event_data.ledGroup    = (unsigned char)LEDGroup; 
		for (int i=0;i<9;i++) {
			event_data.feb_info[i] = 0; // Initialize the FEB information block. 
		}
#if SINGLEPC||MASTER // Single PC or Soldier Node
		global_gate_data[0] = GetGlobalGate();
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "    Global Gate: " << global_gate_data[0];
#endif
		event_data.globalGate = global_gate_data[0];
#endif // end if SINGLEPC||((!MASTER)&&(!SINGLEPC))
#if (!MASTER)&&(!SINGLEPC) // Worker Node
		event_data.globalGate = global_gate_data[0] = 0;
#endif

		// soldier-worker global gate data synchronization.
#if MASTER&&(!SINGLEPC) // Soldier Node
		//SynchWrite(global_gate_socket_handle, global_gate_data);  
		if (write(soldierToWorker_socket_handle,global_gate_data,sizeof(global_gate_data)) == -1) {	 
			mnvdaq.fatalStream() << "socket write error: global_gate_data!";	 
			perror("write error: global_gate_data");	 
			exit(EXIT_FAILURE);	 
		}
#endif
#if (!MASTER)&&(!SINGLEPC) // Worker Node
		//SynchListen(global_gate_socket_connection, global_gate_data);
		while (!global_gate_data[0]) {	 
			// Read global gate data from the worker node	 
			int read_val = read(soldierToWorker_socket_connection,global_gate_data,sizeof(global_gate_data));	 
			if ( read_val != sizeof(global_gate_data) ) {	 
				mnvdaq.fatalStream() << "server read error: cannot get global_gate_data!";
				mnvdaq.fatalStream() << "  socket readback data size = " << read_val;	 
				perror("server read error: global_gate_data");	 
				exit(EXIT_FAILURE);	 
			}
		}
		event_data.globalGate = global_gate_data[0];
#endif 

		// Set the data_ready flag to false, we have not yet taken any data.
		data_ready = false; 

		// Reset the thread count if in threaded operation.
#if THREAD_ME
		thread_count = 0;
#endif

		/**********************************************************************************/
		/* Trigger the DAQ, threaded or unthreaded.                                       */
		/**********************************************************************************/
		gettimeofday(&gatestart, NULL);
		startReadout = (gatestart.tv_sec);
		unsigned short int triggerType;
		readFPGA    = true; // default to reading the FPGA programming registers
		nReadoutADC = 8;    // default to maximum possible
#if MTEST
		// We need to reset the external trigger latch for v85 (cosmic) FEB firmware.
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
				exit(e);
			}
		}
#endif
		// Convert to int should be okay - we only care about the least few significant bits.
		int readoutTimeDiff = (int)stopReadout - (int)startReadout; // stop updated at end of readout.
#if DEBUG_MIXEDMODE
		mnvdaq.debugStream() << "stopReadout time  = " << stopReadout;
		mnvdaq.debugStream() << "startReadout time = " << startReadout;
		mnvdaq.debugStream() << " time diff        = " << readoutTimeDiff;
#endif
		switch (runningMode) {
			case OneShot:
				triggerType = Pedestal;
                        	break;
			case NuMIBeam:
				triggerType = NuMI;
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
					exit(e);
				}
				triggerType = Cosmic;
				break;
			case PureLightInjection:
				triggerType = LightInjection;
				break;
			case MixedBeamPedestal:
				if (triggerCounter%2) { // Start with NuMI!
					triggerType = NuMI;
				} else {
					if ( readoutTimeDiff < 1 ) {
						triggerType = Pedestal;
						readFPGA    = false;
#if DEBUG_MIXEDMODE
						mnvdaq.debugStream() << "Okay to calib trigger...";
#endif
					} else {
						triggerType = NuMI;
						mnvdaq.infoStream() << "Aborting calib trigger!";
					}
				}
#if DEBUG_MIXEDMODE
				mnvdaq.debugStream() << " triggerType = " << triggerType;
#endif
				break;
			case MixedBeamLightInjection:
				if (triggerCounter%2) { // Start with NuMI!
					triggerType = NuMI;
				} else {
					if ( readoutTimeDiff < 1 ) {	
						triggerType = LightInjection;
						nReadoutADC = 1; // Deepest only.
#if DEBUG_MIXEDMODE
						mnvdaq.debugStream() << "Okay to calib trigger...";
#endif
					} else {
						triggerType = NuMI;
						mnvdaq.infoStream() << "Aborting calib trigger!";
					}
				}
#if DEBUG_MIXEDMODE
				mnvdaq.debugStream() << " triggerType = " << triggerType;
#endif
				break; 
			default:
				std::cout << "minervadaq::main(): ERROR! Improper Running Mode = " << runningMode << std::endl;
				mnvdaq.fatalStream() << "Improper Running Mode = " << runningMode;
				exit(-4);
		}
		event_data.triggerType = triggerType;
#if THREAD_ME
		// Careul about arguments with the threaded functions!  They are not exercised regularly.
		// TODO - find how to make boost thread functions return values.
		boost::thread trigger_thread(boost::bind(&TriggerDAQ,daq,triggerType,runningMode,currentController));
#elif NO_THREAD
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
			exit(1);
		}
#endif 

		// Make the event_handler pointer.
		event_handler *evt = &event_data;

		/**********************************************************************************/
		/*  Initialize loop counter variables                                             */
		/**********************************************************************************/
		int croc_id;
		int no_crocs = currentController->GetCrocVectorLength(); 

		/**********************************************************************************/
		/* Loop over crocs and then channels in the system.  Execute TakeData on each     */
		/* Croc/Channel combination of FEB's.  Here we assume that the CROCs are indexed  */
		/* from 1->N.  The routine will fail if this is false!                            */
		/**********************************************************************************/
		// TODO - It would be better to iterate over the CROC vector here rather loop over ID's.
		if (continueRunning) {
			for (int i=0; i<no_crocs; i++) {
				croc_id = i+1;
				croc *tmpCroc = currentController->GetCroc(croc_id);
				for (int j=0; j<4 ;j++) { // Loop over FE Chains.
					// TODO - relace GetChannel functions with GetChain functions?...
					if ((tmpCroc->GetChannelAvailable(j))&&(tmpCroc->GetChannel(j)->GetHasFebs())) {
						//
						// Threaded Option
						//
#if DEBUG_THREAD
						std::cout << " Launching data thread on CROC Addr: " << 
							(tmpCroc->GetCrocAddress()>>16) << " Chain " << j << std::endl;
#endif
#if THREAD_ME
#if TIME_ME
						struct timeval dummy;
						gettimeofday(&dummy,NULL);
						thread_launch_log<<thread_count<<"\t"<<gate<<"\t"
							<<(dummy.tv_sec*1000000+dummy.tv_usec)<<"\t"
							<<(gate_start_time.tv_sec*1000000+gate_start_time.tv_usec)<<endl;
#endif
#if DEBUG_THREAD
						std::cout << thread_count << std::endl;
#endif
						// TODO - how to get a return value from a boost thread function?
						// TODO - can we use a try-catch here?
						data_threads[thread_count] = 
							new boost::thread((boost::bind(&TakeData,boost::ref(daq),boost::ref(evt),croc_id,j,
							thread_count, attach, sys_id)));
#if DEBUG_THREAD	
						std::cout << "Success." << std::endl;
#endif 
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
							//event_data.readoutInfo = (unsigned short)1; // "VME Error"
							event_data.readoutInfo = (unsigned short)controllerErrCode; 
							std::cout << "Error Code " << e << " in minervadaq::main()!  ";
							std::cout << "Cannot TakeData for Gate: " << gate << std::endl;
							std::cout << "Failed to execute on CROC Addr: " << 
								(tmpCroc->GetCrocAddress()>>16) << " Chain: " << j << std::endl;
							mnvdaq.critStream() << "Error Code " << e << " in minervadaq::main()!  ";
							mnvdaq.critStream() << "Cannot TakeData for Gate: " << gate;
							mnvdaq.critStream() << "Failed to execute on CROC Addr: " << 
								(tmpCroc->GetCrocAddress()>>16) << " Chain: " << j;
							continueRunning = false;  // "Stop" gate loop.
							break;                    // Exit readout loop.
						}
#endif
					} //channel has febs
				} //channel
			} //croc
		} //continueRunning Check
		/**********************************************************************************/
		/*   Wait for trigger thread to join in threaded operation.                       */
		/**********************************************************************************/
#if THREAD_ME
		trigger_thread.join();
#if DEBUG_THREAD
		std::cout << "Getting ready to join threads..." << std::endl;
#endif
		for (int i=0;i<thread_count;i++) {
#if DEBUG_THREAD
			std::cout << " Joining thread " << i << endl;
#endif
			data_threads[i]->join();
#if DEBUG_THREAD
			std::cout << " ->Thread joined!" << std::endl;
#endif
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
		mnvdaq.infoStream() << "Re-enabling global IRQ bits...";
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

#if SINGLEPC||MASTER // Soldier Node
		/*************************************************************************************/
		/* Write the End-of-Event Record to the event_handler and then to the event builder. */
		/*************************************************************************************/
		// Build DAQ Header bank.  
		int bank = 3; //DAQ Data Bank (DAQ Header)
		event_data.feb_info[1] = daq->GetController()->GetID();
		event_data.feb_info[4] = bank; 
		event_data.minosSGATE  = daq->GetMINOSSGATE();

#if DEBUG_GENERAL
		mnvdaq.debugStream() << "Preparing to contact the EventBuilder from Main...";
#endif
		// The soldier node must wait for a "done" signal from the 
		// worker node before attaching the end-of-gate header bank.
#if !SINGLEPC   // Soldier Node
		gate_done_data[0] = false;
		//SynchListen(gate_done_socket_connection, gate_done); 
		while (!gate_done_data[0]) {	 
			// Read "done" from the worker node	 
			if ((read(workerToSoldier_socket_connection, gate_done_data, sizeof (gate_done_data)))!=sizeof(gate_done_data)) {	 
				mnvdaq.fatalStream() << "server read error: cannot get gate_done_data!";	 
				perror("server read error: gate_done_data");	 
				exit(EXIT_FAILURE);	 
			}
		}		
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
#endif // end if SINGLEPC || MASTER

#if (!MASTER)&&(!SINGLEPC) // Worker Node
		gate_done_data[0]=true;
		//SynchWrite(gate_done_socket_handle, gate_done);
		if (write(workerToSoldier_socket_handle,gate_done_data,sizeof(gate_done_data)) == -1) {	           
			mnvdaq.fatalStream() << "server write error: cannot put gate_done_data!";	 
			perror("server write error: gate_done_data");	 
			exit(EXIT_FAILURE);	 
		}
#endif 

#if SINGLEPC||(MASTER&&(!SINGLEPC)) // Single PC or Soldier Node
		// Increment the Global Gate value and log it.
		PutGlobalGate(++event_data.globalGate);
#endif

		// Get time for end of gate & readout...
		gettimeofday(&gatend, NULL);
		stopTime    = (unsigned long long)(gatend.tv_sec);
		stopReadout = (gatend.tv_sec);
		// Write the SAM File.
#if SINGLEPC||MASTER
		lastEvent = event_data.globalGate - 1; // Fencepost, etc.
		WriteSAM(sam_filename, firstEvent, lastEvent, fileroot,  
			detector, config_filename, runningMode, gate, runNumber, subRunNumber,
			startTime, stopTime);
#endif
	} //end of gates loop

	// Close sockets for multi-PC synchronization.
#if !SINGLEPC
	close(workerToSoldier_socket_handle);
	close(soldierToWorker_socket_handle);
#endif
	// Report end of subrun...
#if SINGLEPC||MASTER // Single PC or Soldier Node
	std::cout << " Last Event = " << lastEvent << std::endl;
	mnvdaq.infoStream() << "Last Event = " << lastEvent;
#endif 
	// Report total run time in awkward units... end of run time == end of last gate time.
	unsigned long long totalstart = ((unsigned long long)(runstart.tv_sec))*1000000 +
                        (unsigned long long)(runstart.tv_usec);
	unsigned long long totalend   = ((unsigned long long)(gatend.tv_sec))*1000000 +
                        (unsigned long long)(gatend.tv_usec);
	unsigned long long totaldiff  = totalend - totalstart;
	printf(" \n\nTotal acquisition time was %llu microseconds.\n\n",totaldiff);
	mnvdaq.info("Total acquisition time was %llu microseconds.",totaldiff);
#endif // end if TAKE_DATA

	/**********************************************************************************/
	/*   return the success status of the run                                         */
	/**********************************************************************************/
	success = true;

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
	/*              End of execution                                                  */
	/**********************************************************************************/
	return success;
}


int TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id, int thread, 
	et_att_id  attach, et_sys_id  sys_id, bool readFPGA, int nReadoutADC) 
{ // TODO - fix channel / chain naming snafu here too...
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
	// Files for monitoring acquisition.
	// These are mostly for use with multi-threaded debugging tasks...
#if DEBUG_THREAD
	ofstream data_monitor;
	stringstream threadno;
	threadno << thread;
	string filename;
	filename = "data_monitor_"+threadno.str();
	data_monitor.open(filename.c_str());
	time_t currentTime; time(&currentTime);
	data_monitor << "Thread Start Time:  " << ctime(&currentTime) << std::endl;
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

#if DEBUG_THREAD
	data_monitor << "Is data ready? " << data_ready << std::endl;
	data_monitor << " Bank Type?    " << evt->feb_info[4] << std::endl;
#endif

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
#if DEBUG_THREAD
				data_monitor << "TakeAllData Returned" << std::endl;
#endif
				if (data_taken) throw data_taken;
			} catch (bool e) {
				std::cout << "Problems taking data on FEB: " << (*feb)->GetBoardNumber() << std::endl;
				std::cout << "Leaving thread servicing CROC: " << (crocTrial->GetCrocAddress()>>16) <<
					" Chain: " << channel_id << std::endl;
				mnvdaq.critStream() << "Problems taking data on FEB: " << (*feb)->GetBoardNumber();
				mnvdaq.critStream() << "Leaving thread servicing CROC: " << (crocTrial->GetCrocAddress()>>16) <<
					" Chain: " << channel_id;
				return 1; // TODO - check error code for DAQHeader error bits.
			}
		} //feb loop
#if DEBUG_THREAD
		data_monitor << "Completed processing FEB's in this list." << std::endl;
#endif
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
	mnvdaq.infoStream() << " ->Setting Trigger: " << triggerType;
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
	int id = (*crim)->GetCrimID();
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
	// Smallest possible time with "sleep" command is probably something like ~1 ms
	// TODO - Put in a more clever wait function so we don't step on digitization on the FEBs.
	// One milisecond is too long - digitization only takes 300 microseconds.
	system("sleep 1e-3");
#endif

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


int GetGlobalGate()
{                       
/*! \fn int GetGlobalGate()
 *
 * This function gets the value of the global gate from the data file used for tracking.  
 * On mnvdaq build machines, that file is: /work/conditions/global_gate.dat.              
 */
	int ggate;
	fstream global_gate("/work/conditions/global_gate.dat");
	try {
		if (!global_gate) throw (!global_gate);
		global_gate >> ggate;
	} catch (bool e) {
		std::cout << "Error in minervadaq::main opening global gate data!\n";
		mnvdaq.fatalStream() << "Error opening global gate data!";
		exit(-2000);
	}
	global_gate.close();
	return ggate;
} 


void PutGlobalGate(int ggate)
{
/*! \fn void PutGlobalGate(int ggate)
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
		exit(-2000);
	}
	global_gate.close();
}


void CreateSocketPair(int &workerToSoldier_socket_handle, int &soldierToWorker_socket_handle )
{
/*! \fn void CreateSocketPair(int &workerToSoldier_socket_handle, int &soldierToWorker_socket_handle )
 * 
 * This function creates a pair of sockets for gate synchronization between a pair of MINERvA 
 * DAQ nodes.
 */
	workerToSoldier_socket_handle   = socket (PF_INET, SOCK_STREAM, 0);
	soldierToWorker_socket_handle = socket (PF_INET, SOCK_STREAM, 0);
	if (workerToSoldier_socket_handle == -1) { 
		perror("socket"); 
		mnvdaq.fatalStream() << "workerToSoldier_socket_handle == -1!";
		exit(EXIT_FAILURE); 
	}
	if (soldierToWorker_socket_handle == -1) { 
		perror("socket"); 
		mnvdaq.fatalStream() << "soldierToWorker_socket_handle == -1!";
		exit(EXIT_FAILURE); 
	}
	mnvdaq.infoStream() << "Soldier/Master-node Multi-PC workerToSoldier_socket_handle  : " <<
		workerToSoldier_socket_handle;
	mnvdaq.infoStream() << "Soldier/Master-node Multi-PC soldierToWorker_socket_handle: " <<
		soldierToWorker_socket_handle;
}


void SetupSocketService(struct sockaddr_in &socket_service, struct hostent *node_info, 
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
		exit(1); 
	}
	else socket_service.sin_addr = *((struct in_addr *) node_info->h_addr);
	socket_service.sin_port = htons(port); 
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
	fprintf(sam_file,"dataTier='binary-raw',\n");
	fprintf(sam_file,"runNumber=%d%04d,\n",runNum,subNum);
	fprintf(sam_file,"applicationFamily=ApplicationFamily('online','v05','v06-05-05'),\n"); //online, DAQ Heder, CVSTag
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


template <typename Any> void SynchWrite(int socket_handle, Any data[])
{
#if DEBUG_SOCKETS
	mnvdaq.debugStream() << " Entering SynchWrite for handle " << socket_handle << " and data " << data[0];
#endif          
	if (write(socket_handle,data,sizeof(data)) == -1) {
		mnvdaq.fatalStream() << "socket write error: SynchWrite!";
		perror("write error");
		exit(EXIT_FAILURE);
	}
#if DEBUG_SOCKETS
	mnvdaq.debugStream() << " Finished SynchWrite.";
#endif 
}


template <typename Any> void SynchListen(int socket_connection, Any data[])
{
#if DEBUG_SOCKETS
	mnvdaq.debugStream() << " Reading data in SynchListen...";
#endif          
	while (!data[0]) { 
		int read_val = read(socket_connection, data, sizeof(data));
		if ( read_val != sizeof(data) ) {
			mnvdaq.fatalStream() << "Server read error in SynchListen!";
			perror("server read error: done");
			exit(EXIT_FAILURE);
		}
#if DEBUG_SOCKETS
		mnvdaq.debugStream() << "  ->After read, new data: " << data[0];
#endif
	}
}


