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
#include <string>
#include <sstream>

#include <boost/ref.hpp>
#include <boost/thread/mutex.hpp>
#include <ctime>
#include <sys/time.h>

#define THREAD_COUNT 4  /*!< a thread count var if we aren't finding the # of threads needed */
#if MASTER||SINGLE_PC // Soldier Node
#define CONTROLLER_ID 0
#elif (!MASTER)&&(!SINGLE_PC) // Worker Node
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
	detector                 = (0x1)<<4;  // TODO - REMOVE: For header debugging... the Upstream Detector.
	detectorConfig           = 0xBABE;    // TODO - REMOVE: For header debugging...
	LEDLevel                 = 3;         // TODO - REMOVE: MaxPE - For debugging purposes...
	LEDGroup                 = 1;         // TODO - REMOVE: LEDALL - For debugging purposes...
	string fileroot          = "testme";  // For logs, etc.  
	string strtemp           = "unknown";
	char config_filename[100]; sprintf(config_filename,"unknown"); // For SAM.
	string et_filename       = "/work/data/etsys/testme";  
	string log_filename      = "/work/data/logs/testme.txt"; 
	char sam_filename[100]; sprintf(sam_filename,"/work/data/sam/testme.py");
	FILE *sam_file;
	unsigned long long firstEvent, lastEvent;

	/*********************************************************************************/
	/* Process the command line argument set.                                        */
	/*********************************************************************************/
	// TODO - We need to add to the command line argument set...
	//  li box config - led groups activated
	//  li box config - pulse height
	// TODO - Add support for the total seconds flag?...
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
			et_filename  = "/work/data/etsys/" + fileroot;
			// TODO - Alter log filename for worker/solider node...
			log_filename = "/work/data/logs/" + fileroot + ".txt";
			sprintf(sam_filename,"/work/data/sam/%s.py",fileroot.c_str());
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
	mnvdaq.infoStream() << "See Event/MinervaEvent/xml/DAQHeader.xml for codes.";
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


	/*********************************************************************************/
	/* Now set up ET for use in writing the first-pass memory mapped data file.      */
	/*********************************************************************************/
	et_att_id      attach;
	et_sys_id      sys_id;
	et_id          *id;
	et_openconfig  openconfig;

	// Configuring the ET system is the first thing we must do.
	et_open_config_init(&openconfig);

#if MULTI_PC
	// Set the remote host.
	et_open_config_setmode(openconfig, ET_HOST_AS_REMOTE); // Remote (multi-pc) mode only.

	// Set this ET client for remote operation.
	et_open_config_sethost(openconfig, "mnvonlinemaster.fnal.gov");  // Remote (multi-pc) mode only.
	// Set to the current host machine name. 
	// Currently (2010.January.1), setting IP addresses explicitly doesn't work quite right.

	// Set direct connection.
	et_open_config_setcast(openconfig, ET_DIRECT);  // Remote (multi-pc) mode only.

	// Set the server port.
	et_open_config_setserverport(openconfig, 1091); // Remote (multi-pc) mode only.
#endif

	// Open it.
	if (et_open(&sys_id, et_filename.c_str(), openconfig) != ET_OK) {
		printf("et_producer: et_open problems\n");
		mnvdaq.fatalStream() << "et_producer: et_open problems!";
		exit(1);
	}

	// Clean up.
	et_open_config_destroy(openconfig);

	// Set the debug level for output (everything).
	et_system_setdebug(sys_id, ET_DEBUG_INFO);

#if SINGLE_PC
	// Set up the heartbeat to make sure ET starts correctly.
	unsigned int oldheartbeat, newheartbeat;
	id = (et_id *) sys_id;
	oldheartbeat = id->sys->heartbeat;
	int counter = 0; 
	do {
		system("sleep 1s");
		if (!counter) {
			newheartbeat = id->sys->heartbeat;
		} else {
			oldheartbeat=newheartbeat;
			newheartbeat = id->sys->heartbeat;
		}
		counter++;
	} while ((newheartbeat==oldheartbeat)&&(counter!=50)); 
	// Notify the user if ET did not start properly & exit.
	if (counter==50) {
		std::cout << "ET System did not start properly!" << std::endl;
		mnvdaq.fatalStream() << "ET System did not start properly - bad heartbeat!";
		exit(-5);
	}   
#endif 

	// Attach to GRANDCENTRAL station since we are producing events.
	if (et_station_attach(sys_id, ET_GRANDCENTRAL, &attach) < 0) {
		printf("et_producer: error in station attach\n");
		mnvdaq.fatalStream() << "et_producer: error in station attach!";
		system("sleep 10s");
		exit(1);
	} 


	/*********************************************************************************/
	/*  Basic Socket Configuration for Worker && Soldier Nodes.                      */
	/*********************************************************************************/
#if MASTER&&(!SINGLE_PC) // Soldier Node
	// Create a TCP socket.
	gate_done_socket_handle   = socket (PF_INET, SOCK_STREAM, 0);
	global_gate_socket_handle = socket (PF_INET, SOCK_STREAM, 0);
	if (gate_done_socket_handle == -1) { perror("socket"); exit(EXIT_FAILURE); }
	if (global_gate_socket_handle == -1) { perror("socket"); exit(EXIT_FAILURE); }
	mnvdaq.infoStream() << "Soldier/Master-node Multi-PC gate_done_socket_handle  : " << 
		gate_done_socket_handle;
	mnvdaq.infoStream() << "Soldier/Master-node Multi-PC global_gate_socket_handle: " << 
		global_gate_socket_handle;
	// Set up the global_gate service. 
	global_gate_service.sin_family = AF_INET;
	string hostname="mnvonline1.fnal.gov"; // The worker node will listen for the global gate.
	worker_node_info = gethostbyname(hostname.c_str());
	if (worker_node_info == NULL) {
		mnvdaq.fatalStream() << "No worker node to connect to!"; 
		std::cout << "No worker node to connect to!\n"; return 1; 
	}
	else global_gate_service.sin_addr = *((struct in_addr *) worker_node_info->h_addr);
	global_gate_service.sin_port = htons (global_gate_port); 

	// Create an address for the gate_done listener.  The soldier listens for the gate done signal.
	gate_done_socket_address.s_addr = htonl(INADDR_ANY); 
	memset (&gate_done_service, 0, sizeof (gate_done_service));
	gate_done_service.sin_family = AF_INET;
	gate_done_service.sin_port = htons(gate_done_port); 
	gate_done_service.sin_addr = gate_done_socket_address;
	// Bind the gate_done socket to that address for the listener.
	if ((bind (gate_done_socket_handle, (const sockaddr*)&gate_done_service, 
			sizeof (gate_done_service)))) {
		mnvdaq.fatalStream() << "Error binding the gate_done socket!"; 
		perror ("bind"); exit(EXIT_FAILURE); 
	}
	// Enable connection requests on the gate_done socket for the listener.
	if (listen (gate_done_socket_handle, 10)) { 
		mnvdaq.fatalStream() << "Error listening on the gate_done socket!"; 
		perror("listen"); exit(EXIT_FAILURE); 
	}
#endif // end if MASTER&&(!SINGLE_PC)

#if (!MASTER)&&(!SINGLE_PC) // Worker Node
	gate_done_socket_handle   = socket (PF_INET, SOCK_STREAM, 0);
	global_gate_socket_handle = socket (PF_INET, SOCK_STREAM, 0);
	if (gate_done_socket_handle == -1) { perror("socket"); exit(EXIT_FAILURE); }
	if (global_gate_socket_handle == -1) { perror("socket"); exit(EXIT_FAILURE); }
	mnvdaq.infoStream() << "\nWorker/Slave-node Multi-PC gate_done_socket_handle  : " << 
		gate_done_socket_handle;
	mnvdaq.infoStream() << "Worker/Slave-node Multi-PC global_gate_socket_handle: " << 
		global_gate_socket_handle;
	// Set up the gate_done service. 
	gate_done_service.sin_family = AF_INET;
	string hostname="mnvonline0.fnal.gov"; // The soldier node will listen for the gate done signal.
	soldier_node_info = gethostbyname(hostname.c_str());
	if (soldier_node_info == NULL) { 
		mnvdaq.fatalStream() << "No soldier node to connect to!"; 
		std::cout << "No soldier node to connect to!\n"; return 1; 
	}
	else gate_done_service.sin_addr = *((struct in_addr *) soldier_node_info->h_addr);
	gate_done_service.sin_port = htons (gate_done_port); 

	// Create an address for the global_gate listener.  The worker listens for the global gate data.
	global_gate_socket_address.s_addr = htonl(INADDR_ANY); 
	memset (&global_gate_service, 0, sizeof (global_gate_service));
	global_gate_service.sin_family = AF_INET;
	global_gate_service.sin_port = htons(global_gate_port); 
	global_gate_service.sin_addr = global_gate_socket_address;
	// Bind the global_gate socket to that address for the listener.
	if ((bind (global_gate_socket_handle, (const sockaddr*)&global_gate_service, 
			sizeof (global_gate_service)))) { 
		mnvdaq.fatalStream() << "Error binding the global_gate socket!"; 
		perror ("bind"); exit(EXIT_FAILURE); 
	}
	// Enable connection requests on the global socket for the listener.
	if (listen (global_gate_socket_handle, 10)) { 
		mnvdaq.fatalStream() << "Error listening on the global_gate socket!"; 
		perror("listen"); exit(EXIT_FAILURE); 
	}
#endif // end if (!MASTER)&&(!SINGLE_PC)


	// Client-server connect - gate_done. 
	gate_done_socket_is_live = false;
#if MASTER&&(!SINGLE_PC) // Soldier Node
	std::cout << "\nPreparing make new server connection for gate_done synchronization...\n";
	std::cout << " gate_done_socket_is_live = " << gate_done_socket_is_live << std::endl; 
	mnvdaq.infoStream() << "Preparing make new server connection for gate_done synchronization...";
	mnvdaq.infoStream() << " gate_done_socket_is_live = " << gate_done_socket_is_live; 
	// Accept connection from worker node to supply end of event signalling.
	while (!gate_done_socket_is_live) {
		std::cout << " Waiting for worker node...\n";
		std::cout << " Ready to connect to gate_done_socket_handle: " << 
			gate_done_socket_handle << std::endl;
		mnvdaq.infoStream() << " Waiting for worker node...";
		mnvdaq.infoStream() << " Ready to connect to gate_done_socket_handle: " << 
			gate_done_socket_handle;
		struct sockaddr_in remote_address;
		socklen_t address_length;
		address_length = sizeof (remote_address);
		// Accept will wait for a connection...
		gate_done_socket_connection = 
			accept(gate_done_socket_handle, (sockaddr*)&remote_address, &address_length);
		if (gate_done_socket_connection == -1) {
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
		gate_done_socket_is_live = true;
	} // end while !gate_done_socket_is_live
	std::cout << " ->Connection complete at " << gate_done_socket_connection << 
		" with live status = " << gate_done_socket_is_live << "\n";
	mnvdaq.infoStream() << " ->Connection complete at " << gate_done_socket_connection << 
		" with live status = " << gate_done_socket_is_live;
#endif // end if MASTER&&(!SINGLE_PC)
#if (!MASTER)&&(!SINGLE_PC) // Worker Node
	// Initiate connection with "server" (soldier node).  Connect waits for a server response.
	if (connect(gate_done_socket_handle, (struct sockaddr*) &gate_done_service, 
			sizeof (struct sockaddr_in)) == -1) { 
		mnvdaq.fatalStream() << "Error in gate_done connect!";
		perror ("connect"); exit(EXIT_FAILURE); 
	}
	std::cout << " ->Returned from connect to gate_done!\n";
	mnvdaq.infoStream() << " ->Returned from connect to gate_done!";
#endif // end if (!MASTER)&&(!SINGLE_PC)

	
	// Client-server connect - global_gate. 
	global_gate_socket_is_live = false;
#if MASTER&&(!SINGLE_PC) // Soldier Node
	// Initiate connection with "server" (worker node).  Connect waits for a server response.
	if (connect(global_gate_socket_handle, (struct sockaddr*) &global_gate_service, 
			sizeof (struct sockaddr_in)) == -1) { 
		mnvdaq.fatalStream() << "Error in global_gate connect!";
		perror ("connect"); exit(EXIT_FAILURE); 
	}
	std::cout << " ->Returned from connect to global_gate!\n\n";
	mnvdaq.infoStream() << " ->Returned from connect to global_gate!";
#endif // end if MASTER&&(!SINGLE_PC)
#if (!MASTER)&&(!SINGLE_PC) // Worker Node
	std::cout << "\nPreparing make new server connection for global_gate synchronization...\n";
	std::cout << " global_gate_socket_is_live = " << global_gate_socket_is_live << std::endl; 
	mnvdaq.infoStream() << "Preparing make new server connection for global_gate synchronization...";
	mnvdaq.infoStream() << " global_gate_socket_is_live = " << global_gate_socket_is_live; 
	// Accept connection from worker node to supply global gate signalling.
	while (!global_gate_socket_is_live) {
		std::cout << " Waiting for soldier node...\n";
		std::cout << " Ready to connect to global_gate_socket_handle: " << 
			global_gate_socket_handle << std::endl;
		mnvdaq.infoStream() << " Waiting for soldier node...";
		mnvdaq.infoStream() << << " Ready to connect to global_gate_socket_handle: " << 
			global_gate_socket_handle;
		struct sockaddr_in remote_address;
		socklen_t address_length;
		address_length = sizeof (remote_address);
		// Accept will wait for a connection...
		global_gate_socket_connection = 
			accept(global_gate_socket_handle, (sockaddr*)&remote_address, &address_length);
		if (global_gate_socket_connection == -1) {
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
		global_gate_socket_is_live = true;
	} // end while !global_gate_socket_is_live
	std::cout << " ->Connection complete at " << global_gate_socket_connection << 
		" with live status = " << global_gate_socket_is_live << "\n\n";
	mnvdaq.infoStream() << " ->Connection complete at " << global_gate_socket_connection << 
		" with live status = " << global_gate_socket_is_live;
#endif // end if (!MASTER)&&(!SINGLE_PC)


	// Make an acquire data object containing functions for performing initialization and acquisition.
	acquire_data *daq = new acquire_data(et_filename, daqAppender, log4cpp::Priority::INFO); 
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
	mnvdaq.infoStream() << "Returned from electronics initialization.";


	/*********************************************************************************/
	/* If we've made it this far, it is safe to set up the SAM metadata file.        */
	/*********************************************************************************/
	struct timeval runstart, runend;
	gettimeofday(&runstart, NULL);
#if SINGLE_PC||MASTER // Single PC or Soldier Node
	fstream global_gate("/work/conditions/global_gate.dat"); 
	try {
		if (!global_gate) throw (!global_gate);
		global_gate >> global_gate_data[0];
	} catch (bool e) {
		std::cout << "Error in minervadaq::main opening global gate data!\n";
		mnvdaq.fatalStream() << "Error opening global gate data!";
		exit(-2000);
	}
	global_gate.close();
	std::cout << "Opened Event Log, First Event = " << global_gate_data[0] << std::endl;
	mnvdaq.infoStream() << "Opened Event Log, First Event = " << global_gate_data[0];
	firstEvent = global_gate_data[0];

	if ( (sam_file=fopen(sam_filename,"w")) ==NULL) {
		std::cout << "minervadaq::main(): Error!  Cannot open SAM file for writing!" << std::endl;
		mnvdaq.fatalStream() << "Error opening SAM file for writing!";
		exit(1);
	}
	fprintf(sam_file,"from SamFile.SamDataFile import SamDataFile\n\n");
	fprintf(sam_file,"from SamFile.SamDataFile import ApplicationFamily\n");
	fprintf(sam_file,"from SamFile.SamDataFile import CRC\n");
	fprintf(sam_file,"from SamFile.SamDataFile import SamTime\n");
	fprintf(sam_file,"from SamFile.SamDataFile import RunDescriptorList\n");
	fprintf(sam_file,"from SamFile.SamDataFile import SamSize\n\n");
	fprintf(sam_file,"import SAM\n\n");	
	fprintf(sam_file,"metadata = SamDataFile(\n");
	fprintf(sam_file,"fileName = '%s.dat',\n",fileroot.c_str());
	fprintf(sam_file,"fileType = SAM.DataFileType_ImportedDetector,\n");
	fprintf(sam_file,"fileFormat = SAM.DataFileFormat_BINARY,\n");
	fprintf(sam_file,"crc=CRC(666L,SAM.CRC_Adler32Type),\n");
	fprintf(sam_file,"group='minerva',\n");
	fprintf(sam_file,"dataTier='raw',\n");
	fprintf(sam_file,"runNumber=%d%04d,\n",runNumber,subRunNumber);
	fprintf(sam_file,"applicationFamily=ApplicationFamily('online','v05','v04-08-03'),\n"); //online, DAQ Heder, CVS Tag
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
			fprintf(sam_file,"runType='fullminerva',\n");
			break;
		default:
			std::cout << "minervadaq::main(): ERROR! Improper Running Mode defined!" << std::endl;
			exit(-4);
	}
	fprintf(sam_file,"params = Params({'Online':CaseInsensitiveDictionary");
	fprintf(sam_file,"({'triggerconfig':'%s',",config_filename); 
	switch (runningMode) {
		case OneShot:
			fprintf(sam_file,"'triggertype':'oneshot',})}),\n");
			fprintf(sam_file,"datastream='pdstl',\n");
                       	break;
		case NuMIBeam:
			fprintf(sam_file,"'triggertype':'numibeam',})}),\n");
			fprintf(sam_file,"datastream='numib',\n");
			break;
		case Cosmics:
			fprintf(sam_file,"'triggertype':'cosmics',})}),\n");
			fprintf(sam_file,"datastream='cosmc',\n");
			break;
		case PureLightInjection:
			fprintf(sam_file,"'triggertype':'purelightinjection',})}),\n");
			fprintf(sam_file,"datastream='linjc',\n");
			std::cout << "minervadaq::main(): Warning!  No LI control class exists yet!" << std::endl;
			break;
		case MixedBeamPedestal:
			// TODO - Test mixed beam-pedestal running!
			fprintf(sam_file,"'triggertype':'mixedbeampedestal',})}),\n");
			fprintf(sam_file,"datastream='numip',\n");
			std::cout << "minervadaq::main(): Warning!  Calling untested mixed mode beam-pedestal trigger types!" << 
				std::endl;
			break;
		case MixedBeamLightInjection:
			// TODO - Test mixed beam-li running!
			fprintf(sam_file,"'triggertype':'mixedbeamlightinjection',})}),\n");
			fprintf(sam_file,"datastream='numil',\n");
			std::cout << "minervadaq::main(): Warning!  Calling untested mixed mode beam-li trigger types!" << std::endl;
			std::cout << "minervadaq::main(): Warning!  No LI control class exists yet!" << std::endl;
			break; 
		default:
			std::cout << "minervadaq::main(): ERROR! Improper Running Mode defined!" << std::endl;
			exit(-4);
	}
	fprintf(sam_file,"startTime=SamTime('%llu',SAM.SamTimeFormat_UTCFormat),\n",
		(unsigned long long)(runstart.tv_sec));
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
	// TODO - use a while loop that also checks for a stop condition
	int gate;
	for (gate = 1; gate <= record_gates; gate++) { 
#if TIME_ME
		struct timeval gate_start_time, gate_stop_time;
		gettimeofday(&gate_start_time, NULL);
#endif
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "->Top of the Event Loop, starting Gate: " << gate;
#endif
		if (!(gate%100)) { std::cout << "   Acquiring Gate: " << gate << std::endl; }
		if (!(gate%1000)) { mnvdaq.infoStream() << "   Acquiring Gate: " << gate; }
		/**********************************************************************************/
		/*  Initialize the following data members of the event_handler structure          */
		/*    event_data:                                                                 */
		/*       event_data.feb_info[0-9] 0: link_no, 1: crate_no, 2: croc_no,            */
		/*                                  3: chan_no, 4: bank 5: buffer length          */
		/*                                  6: feb number, 7: feb firmware, 8: hits       */
		/**********************************************************************************/
		event_data.gate        = gate; // Record gate number.
		event_data.triggerTime = 0;    // Set after returning from the Trigger function.
		event_data.readoutInfo = 0;    // Error bits.
		event_data.minosSGATE  = 0;    // MINOS Start GATE in their time coordinates.
		event_data.ledLevel    = (unsigned char)LEDLevel; 
		event_data.ledGroup    = (unsigned char)LEDGroup; 
		for (int i=0;i<9;i++) {
			event_data.feb_info[i] = 0; // Initialize the FEB information block. 
		}
#if SINGLE_PC||(MASTER&&(!SINGLE_PC)) // Single PC or Soldier Node
		global_gate.open("/work/conditions/global_gate.dat"); 
		try {
			if (!global_gate) throw (!global_gate);
			global_gate >> global_gate_data[0];
		} catch (bool e) {
			std::cout << "Error in minervadaq::main opening global gate data!\n";
			mnvdaq.fatalStream() << "Error opening global gate data!";
			exit(-2000);
		}
		global_gate.close();
#if DEBUG_GENERAL
		mnvdaq.debugStream() << "    Global Gate: " << global_gate_data[0];
#endif
		event_data.globalGate = global_gate_data[0];
#endif // end if SINGLE_PC||((!MASTER)&&(!SINGLE_PC))
#if (!MASTER)&&(!SINGLE_PC) // Worker Node
		event_data.globalGate = global_gate_data[0] = 0;
#endif

		// soldier-worker global gate data synchronization.
#if MASTER&&(!SINGLE_PC) // Soldier Node
#if DEBUG_SOCKETS
		mnvdaq.debugStream() << " Writing global gate to soldier node to indicate readiness of trigger...";
#endif
		if (write(global_gate_socket_handle,global_gate_data,sizeof(global_gate_data)) == -1) { 
			mnvdaq.fatalStream() << "socket write error: global_gate!";
			perror("write error: global_gate"); 
			exit(EXIT_FAILURE);
		}
#if DEBUG_SOCKETS
		mnvdaq.debugStream() << " Finished writing global gate to worker node.";
#endif
#endif // end if MASTER && !SINGLE_PC
#if (!MASTER)&&(!SINGLE_PC) // Worker Node
#if DEBUG_SOCKETS
		mnvdaq.debugStream() << " Reading global gate from soldier node to indicate start of trigger...";
		mnvdaq.debugStream() << "  Initial global_gate_data   = " << global_gate_data[0];
		mnvdaq.debugStream() << "  global_gate_socket_is_live = " << global_gate_socket_is_live; 
#endif
		while (!global_gate_data[0]) { 
			// Read global gate data from the worker node 
			int read_val = read(global_gate_socket_connection,global_gate_data,sizeof(global_gate_data));
			if ( read_val != sizeof(global_gate_data) ) { 
				mnvdaq.fatalStream() << "server read error: cannot get global_gate!";
				mnvdaq.fatalStream() << "  socket readback data size = " << read_val;
				perror("server read error: done"); 
				exit(EXIT_FAILURE);
			}
#if DEBUG_SOCKETS
			mnvdaq.debugStream() << "  ->After read, new global_gate_data: " << global_gate_data[0];
#endif
		}
		event_data.globalGate = global_gate_data[0];
#endif // end if (!MASTER)&&(!SINGLE_PC)

		// Set the data_ready flag to false, we have not yet taken any data.
		data_ready = false; 

		// Reset the thread count if in threaded operation.
#if THREAD_ME
		thread_count = 0;
#endif
#if DEBUG_THREAD
		std::cout << "Launching the trigger thread." << std::endl;
#endif

		/**********************************************************************************/
		/* Trigger the DAQ, threaded or unthreaded.                                       */
		/**********************************************************************************/
		unsigned short int triggerType;
		switch (runningMode) {
			case OneShot:
				triggerType = Pedestal;
                        	break;
			case NuMIBeam:
				triggerType = NuMI;
				break;
			case Cosmics:
				// We need to reset the external trigger latch in Cosmic mode...
				for (croc_iter = croc_vector->begin(); croc_iter != croc_vector->end(); croc_iter++) {
					int crocID = (*croc_iter)->GetCrocID();
					try {
						unsigned char command[] = {0x85};
						int error = daq->WriteCROCFastCommand(crocID, command);
						if (error) throw error;
					} catch (int e) {
						mnvdaq.fatalStream() << "Error for CROC " <<
							((*croc_iter)->GetCrocAddress()>>16);
						mnvdaq.fatalStream() << "Cannot write to FastCommand register!";
						std::cout << "Error in minervadaq::main() for CROC " <<
							((*croc_iter)->GetCrocAddress()>>16) << std::endl;
						std::cout << "Cannot write to FastCommand register!" << std::endl;
						exit(e);
					}
				}
				triggerType = Cosmic;
				break;
			case PureLightInjection:
				triggerType = LightInjection;
				mnvdaq.warnStream() << "No LI control class implemented yet!";
				std::cout << "minervadaq::main(): Warning!  No LI control class implemented yet!" << std::endl;
				break;
			case MixedBeamPedestal:
				// TODO - Test mixed beam-pedestal running!
				if (gate%2) {
					triggerType = Pedestal;
				} else {
					triggerType = NuMI;
				}
				mnvdaq.warnStream() << "Calling untested mixed mode beam-pedestal trigger types!";
				break;
			case MixedBeamLightInjection:
				// TODO - Test mixed beam-li running!
				if (gate%2) {
					triggerType = LightInjection;
				} else {
					triggerType = NuMI;
				}
				mnvdaq.warnStream() << "Calling untested mixed mode beam-li trigger types!";
				mnvdaq.warnStream() << "No LI control class implemented yet!";
				std::cout << "minervadaq::main(): Warning!  No LI control class exists yet!" << std::endl;
				break; 
			default:
				std::cout << "minervadaq::main(): ERROR! Improper Running Mode defined!" << std::endl;
				mnvdaq.fatalStream() << "Improper Running Mode defined!";
				exit(-4);
		}
		event_data.triggerType = triggerType;
#if THREAD_ME
		// Careul about arguments with the threaded functions!  They are not exercised regularly.
		boost::thread trigger_thread(boost::bind(&TriggerDAQ,daq,triggerType,runningMode,currentController));
#elif NO_THREAD
		TriggerDAQ(daq, triggerType, runningMode, currentController);
#endif 

		// Make the event_handler pointer.
		event_handler *evt = &event_data;

		// Set the trigger time.
		struct timeval triggerNow;
		gettimeofday(&triggerNow, NULL);
		unsigned long long totaluseconds = ((unsigned long long)(triggerNow.tv_sec))*1000000 + 
			(unsigned long long)(triggerNow.tv_usec);
#if DEBUG_GENERAL
		mnvdaq.debugStream() << " ->Recording Trigger Time (gpsTime) = " << totaluseconds;
#endif
		event_data.triggerTime = totaluseconds;

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
		for (int i=0; i<no_crocs; i++) {
			croc_id = i+1;
			croc *tmpCroc = currentController->GetCroc(croc_id);
			for (int j=0; j<4 ;j++) { // Loop over FE Channels.
				if ((tmpCroc->GetChannelAvailable(j))&&(tmpCroc->GetChannel(j)->GetHasFebs())) {
					//
					// Threaded Option
					//
#if DEBUG_THREAD
					std::cout << " Launching data thread: " << croc_id << " " << j << std::endl;
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
						" Index: " << croc_id << " Channel: " << j;
#endif
					TakeData(daq,evt,croc_id,j,0,attach,sys_id);
#endif
				} //channel has febs
			} //channel
		} //croc

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

		/**********************************************************************************/
		/*  re-enable the IRQ for the next trigger                                        */
		/**********************************************************************************/
		// TODO - Take care we are only doing interrrupt *config* on master CRIMs...
		// Interrupt configuration is already stored in the CRIM objects.
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

#if SINGLE_PC||MASTER // Soldier Node
		/*************************************************************************************/
		/* Write the End-of-Event Record to the event_handler and then to the event builder. */
		/*************************************************************************************/
		// Build DAQ Header bank.
		// Get Trigger Time, Timing Violation Error (obsolete), MINOS SGATE
		int bank = 3; //DAQ Data Bank
		// TODO - find a way to get exceptions passed into the error bits.
		// TODO - read the CRIM MINOS register to get MINOS SGATE
		unsigned short error         = 0;
		unsigned int minos           = 123456789; // TODO - For deugging only... 
		event_data.feb_info[1] = daq->GetController()->GetID();
		event_data.feb_info[4] = bank; 
		event_data.readoutInfo = error; 
		event_data.minosSGATE  = minos;

#if DEBUG_GENERAL
		mnvdaq.debugStream() << "Preparing to contact the EventBuilder from Main...";
#endif
		// The soldier node must wait for a "done" signal from the 
		// worker node before attaching the end-of-event header bank.
#if !SINGLE_PC // Soldier Node
		gate_done[0] = false;
#if DEBUG_SOCKETS
		mnvdaq.debugStream() << "Preparing to end event...";
		mnvdaq.debugStream() << " Initial gate_done        = " << gate_done[0];
		mnvdaq.debugStream() << " gate_done_socket_is_live = " << gate_done_socket_is_live; 
#endif
		while (!gate_done[0]) { 
			// Read "done" from the worker node 
			if ((read(gate_done_socket_connection, gate_done, sizeof (gate_done)))!=sizeof(gate_done)) { 
				mnvdaq.fatalStream() << "server read error: cannot get gate_done!";
				perror("server read error: gate_done"); 
				exit(EXIT_FAILURE);
			}
#if DEBUG_SOCKETS
			mnvdaq.debugStream() << " After read, new gate_done: " << gate_done[0];
#endif
		}
#endif // end if !SINGLE_PC
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
#endif // end if SINGLE_PC || MASTER

#if (!MASTER)&&(!SINGLE_PC) // Worker Node
#if DEBUG_SOCKETS
		mnvdaq.debugStream() << " Writing to soldier node to indicate end of gate...";
#endif
		gate_done[0]=true;
		if (write(gate_done_socket_handle,gate_done,sizeof(gate_done)) == -1) { 
			mnvdaq.fatalStream() << "server write error: cannot put gate_done!";
			perror("server write error: gate_done"); 
			exit(EXIT_FAILURE);
		}
#endif // end if !MASTER && !SINGLE_PC

#if SINGLE_PC||(MASTER&&(!SINGLE_PC)) // Single PC or Soldier Node
		global_gate.open("/work/conditions/global_gate.dat"); 
		try {
			if (!global_gate) throw (!global_gate);
			event_data.globalGate++;
			global_gate << event_data.globalGate;
		} catch (bool e) {
			std::cout << "Error in minervadaq::main opening global gate data!" << std::endl;
			mnvdaq.fatalStream() << "Error opening global gate data!";
			exit(-2000);
		}
		global_gate.close();
#endif
	} //end of gates loop

#if !SINGLE_PC
	close(gate_done_socket_handle);
	close(global_gate_socket_handle);
#endif
#if SINGLE_PC||(MASTER&&(!SINGLE_PC)) // Single PC or Soldier Node
	global_gate.open("/work/conditions/global_gate.dat"); 
	try {
		if (!global_gate) throw (!global_gate);
		global_gate >> global_gate_data[0];
	} catch (bool e) {
		std::cout << "Error in minervadaq::main opening global gate data!\n";
		mnvdaq.fatalStream() << "Error opening global gate data!";
		exit(-2000);
	}
	global_gate.close();
	lastEvent = global_gate_data[0] - 1; // Fencepost, etc.
	std::cout << " Last Event = " << lastEvent << std::endl;
	mnvdaq.infoStream() << "Last Event = " << lastEvent;
#endif // end if SINGLE_PC||((!MASTER)&&(!SINGLE_PC))

	gettimeofday(&runend, NULL);
	unsigned long long totalstart = ((unsigned long long)(runstart.tv_sec))*1000000 +
                        (unsigned long long)(runstart.tv_usec);
	unsigned long long totalend   = ((unsigned long long)(runend.tv_sec))*1000000 +
                        (unsigned long long)(runend.tv_usec);

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

	// Close the SAM File.
#if SINGLE_PC||MASTER
	fprintf(sam_file,"endTime=SamTime('%llu',SAM.SamTimeFormat_UTCFormat),\n",
		(unsigned long long)(runend.tv_sec));
	fprintf(sam_file,"eventCount=%d,\n",(gate-1));
	fprintf(sam_file,"firstEvent=%llu,\n",firstEvent);
	fprintf(sam_file,"lastEvent=%llu,\n",lastEvent);
	fprintf(sam_file,"lumBlockRangeList=LumBlockRangeList([LumBlockRange(%llu,%llu)])\n",
		firstEvent, lastEvent);
	fprintf(sam_file,")\n");
	fclose(sam_file);
#endif
	// Clean up the log4cpp file.
	log4cpp::Category::shutdown();

	/**********************************************************************************/
	/*              End of execution                                                  */
	/**********************************************************************************/
	return success;
}


void TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id, int thread, 
	et_att_id  attach, et_sys_id  sys_id) 
{
/*!
 *  \fn void TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id, int thread,
 *                et_att_id  attach, et_sys_id  sys_id)
 *
 *  This function executes the necessary commands to complete an acquisition sequence.
 *
 *  Code is available for threaded and unthreaded operating modes.
 *  
 *  \param *daq, a pointer to the acquire_data object governing this DAQ acquisition
 *  \param *evt, a pointer to the event_handler structure containing information
 *               about the data being handled.
 *  \param croc_id, an integer with the CROC being serviced in this call
 *  \param channel_id, an integer with the channel number being serviced in this cal
 *  \param thread, the thread number of this call
 *  \param attach, the ET attachemnt to which data will be stored
 *  \param sys_id, the ET system handle
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

	// A flag to let us know that we have successfully serviced this channel (the functions 
	// return "0" if they are successful...)
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
			data_taken = daq->TakeAllData((*feb),channelTrial,crocTrial,evt,thread,attach,sys_id); 
#if DEBUG_THREAD
			data_monitor << "TakeAllData Returned" << std::endl;
#endif
			if (data_taken) { //and if you didn't succeed...(the functions return 0 if successful) 
				std::cout << "Problems taking data on FEB: " << 
					(*feb)->GetBoardNumber() << std::endl;
				std::cout << "Leaving thread servicing CROC: " << (crocTrial->GetCrocAddress()>>16) << 
					" channel: " << channel_id << std::endl;
				exit(-2000); 
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

		if (!data_taken) return; //we're done processing this channel
	} //data ready loop
} // end void TakeData


void TriggerDAQ(acquire_data *daq, unsigned short int triggerType, RunningModes runningMode, controller *tmpController) 
{
/*! \fn void TriggerDAQ(acquire_data *data, unsigned short int triggerType)
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

	/**********************************************************************************/
	/* Let the hardware tell us when the trigger has completed.                       */
	/**********************************************************************************/
	vector<crim*> *crim_vector = tmpController->GetCrimVector(); 
	vector<crim*>::iterator crim = crim_vector->begin();
	int id = (*crim)->GetCrimID();
	switch (runningMode) {
		case OneShot:
			for (crim = crim_vector->begin(); crim != crim_vector->end(); crim++) {
				id = (*crim)->GetCrimID();
				daq->TriggerDAQ(triggerType, id);
			}  
                       	break;
		case NuMIBeam:
		case Cosmics:
		case PureLightInjection:
		case MixedBeamPedestal:
		case MixedBeamLightInjection:
			daq->TriggerDAQ(triggerType, id); // Not strictly needed.
			break;
		default:
			std::cout << "ERROR! Improper Running Mode defined!" << std::endl;
			mnvdaq.fatalStream() << "Improper Running Mode defined!";
			exit(-4);
	}
	daq->WaitOnIRQ();    // wait for the trigger to be set (only returns if successful)

	/**********************************************************************************/
	/*  Let the interrupt handler deal with an asserted interrupt.                    */
	/**********************************************************************************/
	/*! \note  This uses the interrupt handler to handle an asserted interrupt 
	 *
	 */
#if ASSERT_INTERRUPT
	daq->AcknowledgeIRQ(); //acknowledge the IRQ (only returns if successful)
#endif

#if DEBUG_GENERAL
	mnvdaq.debugStream() << " Data Ready! ";
#endif
#if RUN_SLEEPY
	// This sleep is here because we return too quickly - the FEBs are still digitizing.
	// Smallest possible time with "sleep" command is probably something like ~1 ms
	// TODO - Put in a more clever wait function so we don't step on digitization on the FEBs.
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
} // end void TriggerDAQ


