#include "event_builder.h"
//#include "event_builder_templates.h"
#include <ctime>
#include <sys/time.h>
#include <signal.h>
#include <errno.h>

using namespace std;

const int  adcFrameWarningCount = 600;
#if !MTEST
const int  gate_print_freq = 1;
#else
const int  gate_print_freq = 1;
#endif
static int adcFrameCount   = 0;
static int discFrameCount  = 0;
static int fpgaFrameCount  = 0;

// log4cpp Variables - Needed throughout the event_builder functions.
log4cpp::Appender* ebAppender;
log4cpp::Category& root     = log4cpp::Category::getRoot();
log4cpp::Category& ebuilder = log4cpp::Category::getInstance(std::string("ebuilder"));


int main(int argc, char **argv) 
{
/*! \fn The main function for running the event builder. 
 * This function is the MINERvA-specific implementation 
 * of the generic et_producer class.  
 */
	if (argc < 3) {
		printf("Usage: event_builder <et_filename> <rawdata_filename> <network port (default 1091)> <callback PID (default: no PID)>\n");
		printf("  Please supply the full path!\n");
		exit(1);
	}

	std::cout << "ET Filesystem          = " << argv[1] << std::endl;
	string output_filename(argv[2]);
	// Open the file for binary output.
	ofstream binary_outputfile(output_filename.c_str(),ios::out|ios::app|ios::binary); 
	int networkPort = 1091;
	if (argc > 3) networkPort = atoi(argv[3]);
	std::cout << "ET Network Port        = " << networkPort << std::endl;
	
	int callback_pid = 0;
	if (argc > 4)
	{
		callback_pid = atoi(argv[4]);
		std::cout << "Notifying process " << callback_pid << " when ready to accept events." << std::endl;
	}

	struct timeval hpnow; gettimeofday(&hpnow,NULL);
	char log_filename[100]; sprintf(log_filename,"./event_builder_%d_Log.txt",(int)hpnow.tv_sec); 
#if NEARLINE
#if NEARLINEPRO
	sprintf(log_filename,"/scratch/nearonline/logs/event_builder_nearline_%d_Log.txt",(int)hpnow.tv_sec);
#endif
#if NEARLINEDEV
	sprintf(log_filename,"/work/logs/event_builder_nearline_%d_Log.txt",(int)hpnow.tv_sec);
#endif
#else
	sprintf(log_filename,"/work/data/logs/event_builder_daq_%d_Log.txt",(int)hpnow.tv_sec);
#endif
	// Set up general logging utilities.
	ebAppender = new log4cpp::FileAppender("default", log_filename);
	ebAppender->setLayout(new log4cpp::BasicLayout());
	root.addAppender(ebAppender);
	root.setPriority(log4cpp::Priority::DEBUG);
	ebuilder.setPriority(log4cpp::Priority::DEBUG);
	root.infoStream()   << "Starting the MINERvA DAQ Event Builder. ";
	ebuilder.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
	ebuilder.infoStream() << "Arguments to the Event Builder: ";
	ebuilder.infoStream() << "  ET System              = " << argv[1];
	ebuilder.infoStream() << "  Output Filename        = " << output_filename;
	ebuilder.infoStream() << "  ET System Port         = " << networkPort;
	ebuilder.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";

	char hostName[100];
#if SINGLEPC
	sprintf(hostName, "localhost");
        std::cout << "Configured for a Single-PC Build..." << std::endl;  
	ebuilder.infoStream() << "Configured for a Single-PC Build..."; 
#endif

#if MULTIPC

#if WH14T||WH14B
	sprintf(hostName, "minervatest03.fnal.gov");
#endif

#if CRATE0||CRATE1||NEARLINEPRO
#if BACKUPNODE
	sprintf(hostName, "mnvonlinebck1.fnal.gov");
#else
	sprintf(hostName, "mnvonlinemaster.fnal.gov");
// if BACKUPNODE
#endif

#elif NEARLINEDEV
	sprintf(hostName, "mnvonlinemaster.fnal.gov");  // minervatest03.fnal.gov
// if CRATE0||CRATE1||NEARLINEPRO
#endif
	std::cout << "Configured for a Multi-PC Build..." << std::endl;
	ebuilder.infoStream() << "Configured for a Multi-PC Build...";
// if MULTIPC
#endif
	std::cout << "ET system host machine = " << hostName << std::endl;
	std::cout << "Ouptut Filename        = " << output_filename << std::endl;
	ebuilder.infoStream() << "ET system host machine = " << hostName;

	int            status;
	et_openconfig  openconfig;
	et_att_id      attach;
	et_sys_id      sys_id;
	et_stat_id     cu_station;
	et_statconfig  sconfig;
	et_event       *pe;
	et_id          *id;

	// The station which will attach event headers to the buffers in an event handler structure.
	et_station_config_init(&sconfig);
	et_station_config_setblock(sconfig,ET_STATION_BLOCKING);
	et_station_config_setselect(sconfig,ET_STATION_SELECT_ALL);
	et_station_config_setuser(sconfig,ET_STATION_USER_SINGLE);
	et_station_config_setrestore(sconfig,ET_STATION_RESTORE_OUT);

	// Opening the ET system is the first thing we must do...
	et_open_config_init(&openconfig);
	// We operate the DAQ exclusively in "remote" mode.
	et_open_config_setmode(&openconfig, ET_HOST_AS_REMOTE);
	et_open_config_setcast(openconfig, ET_DIRECT);
	et_open_config_sethost(openconfig, hostName); 
	et_open_config_setserverport(openconfig, networkPort); 

	if (et_open(&sys_id, argv[1], openconfig) != ET_OK) {
		printf("event_builder::main(): et_producer: et_open problems\n");
		ebuilder.fatal("event_builder::main(): et_producer: et_open problems\n");
		exit(1);
	}
	et_open_config_destroy(openconfig);

	// Check if ET is up and running.
#if !NEARLINE
	std::cout << "Running a DAQ Station..." << std::endl;
	std::cout << "  Waiting for ET..." << std::endl;
	ebuilder.infoStream() << "Running a DAQ Station...";
	ebuilder.infoStream() << "  Waiting for ET...";
	unsigned int oldheartbeat, newheartbeat;
	id = (et_id *) sys_id;
	oldheartbeat = id->sys->heartbeat;
	int counter = 0;
	do {
		// Give ET a chance to start...
		// For modern DAQ operations, we take care of this beforehand.
		// So set this check to use a very short sleep period!
		std::cout << "  Synching heartbeat..." << std::endl;
		ebuilder.infoStream() << "  Synching heartbeat...";
		system("sleep 5s"); 
		if (!counter) {
			newheartbeat = id->sys->heartbeat;
		} else {
			oldheartbeat=newheartbeat;
			newheartbeat = id->sys->heartbeat;
		}
		counter++;  
	} while ((newheartbeat==oldheartbeat)&&(counter!=60));
	if (counter==60) {
		std::cout << "Error in event_builder::main()!" << std::endl;
		std::cout << "ET System did not start properly!  Exiting..." << std::endl;
		ebuilder.fatalStream() << "Error in event_builder::main()!";
		ebuilder.fatalStream() << "ET System did not start properly!  Exiting...";
		exit(-5);
	} 
#endif

	// Set the level of debug output that we want (everything).
	et_system_setdebug(sys_id, ET_DEBUG_INFO);

	// Create & attach to a new station for making the final output file.
	std::cout << "Creating new station for output..." << std::endl;
#if NEARLINEPRO
	et_station_create(sys_id,&cu_station,"RIODEJANEIRO",sconfig);
	ebuilder.infoStream() << "Creating new station RIODEJANEIRO for output...";
#elif NEARLINEDEV
	et_station_create(sys_id,&cu_station,"ROCHESTER",sconfig);
	ebuilder.infoStream() << "Creating new station ROCHESTER for output...";
#else
	et_station_create(sys_id,&cu_station,"CHICAGO_UNION",sconfig);
	ebuilder.infoStream() << "Creating new station CHICAGO_UNION for output...";
#endif
	std::cout << "Attaching to new station..." << std::endl;
	if (et_station_attach(sys_id, cu_station, &attach) < 0) {
		printf("event_builder::main(): et_producer: error in station attach\n");
		system("sleep 10s");
		exit(1);
	}
	
	/* send the SIGUSR1 signal to the specified process signalling that ET is ready */
	std::cout << "Sending ready signal to ET system..." << std::endl;
	ebuilder.infoStream() << "Sending ready signal to ET system...";
	int failure;
	if (callback_pid)
	{
		failure = kill(callback_pid, SIGUSR1);
		if (failure)
		{
			printf("Warning: signal was not delivered to parent process.  Errno: %d\n", failure);
			ebuilder.warnStream() << "Signal was not delivered to parent process.  Errno: " << failure;
			fflush(stdout);
		}
			
	}

	// Request an event from the ET service.
	std::cout << "Starting!" << std::endl;
	std::cout << "\nIf 20 seconds goes by and the DAQ doesn't start, " << std::endl;
	std::cout << "please skip to the next subrun or stop and try again." << std::endl;
	std::cout << "\nIf the event builder exits cleanly and no events " << std::endl;
	std::cout << "were taken, check the electronics for errors!" << std::endl;
	std::cout << "\nIn either case, please note the run and subrun and " << std::endl;
	std::cout << "email them to Gabe Perdue: perdue AT fnal DOT gov" << std::endl;
	std::cout << std::endl;
	int evt_counter = 0;
	while ((et_alive(sys_id))) {
		struct timespec time;
#if MTEST
		time.tv_sec  = 3600; // Wait 60 minutes before the EB times out.
#else
		time.tv_sec  = 1200; // Wait 20 minutes before the EB times out.
#endif
		time.tv_nsec =    0;
		
		//printf("time: %d.%i\n", time.tv_sec, time.tv_nsec);
		status = et_event_get(sys_id, attach, &pe, ET_TIMED|ET_MODIFY, &time);
		if (status==ET_ERROR_TIMEOUT) break;

		// socket errors need to be handled differently depending on locale.
		// for the nearline machines, it's not a tragedy if we miss an event or two.
		// therefore under those circumstances we just go on and try to get another event.
		// in the context of online data taking, however, it's a real problem.
		if ((status == ET_ERROR_WRITE) || (status == ET_ERROR_READ)) {
#if NEARLINE
			printf("Warning: socket error in event_builder::main() calling et_event_get().  Will retry.\n");
			ebuilder.warn("Socket error in event_builder::main() calling et_event_get().  Will retry.\n");
			fflush(stdout);
			continue;
#else
			printf("event_builder::main(): et_client: socket communication error\n");
			ebuilder.fatal("event_builder::main(): et_client: socket communication error\n");
			exit(-1);
#endif
		}

		if (status == ET_ERROR_DEAD) {
			printf("event_builder::main(): et_client: ET system is dead\n");
			ebuilder.fatal("event_builder::main(): et_client: ET system is dead\n");
			exit(-1);
		}
		else if (status == ET_ERROR_TIMEOUT) {
			printf("event_builder::main(): et_client: got timeout\n");
			ebuilder.fatal("event_builder::main(): et_client: got timeout\n");
			exit(-1);
		}
		else if (status == ET_ERROR_EMPTY) {
			printf("event_builder::main(): et_client: no events\n");
			ebuilder.fatal("event_builder::main(): et_client: no events\n");
			exit(-1);
		}
		else if (status == ET_ERROR_BUSY) {
			printf("event_builder::main(): et_client: station is busy\n");
			ebuilder.fatal("event_builder::main(): et_client: station is busy\n");
			exit(-1);
		}
		else if (status == ET_ERROR_WAKEUP) {
			printf("event_builder::main(): et_client: someone told me to wake up\n");
			ebuilder.fatal("event_builder::main(): et_client: someone told me to wake up\n");
			exit(-1);
		}
		else if (status != ET_OK) {
			printf("event_builder::main(): et_client: get error.  Status code: %d\n", status);
			ebuilder.fatalStream() << "event_builder::main(): et_client: get error.  Status code: " << status;
			exit(-1);
		}

		event_handler *evt;
		int pri;
		size_t len;
		int con[ET_STATION_SELECT_INTS];
		
		et_event_getdata(pe, (void **) &evt);
		et_event_getpriority(pe, &pri);
		et_event_getlength(pe, &len);
		et_event_getcontrol(pe, con);
		event_builder(evt);

		void *pdata;
		int length;
#if DEBUG_BUFFERS
		ebuilder.debugStream() << " event_builder::main(): Building final data buffers...";
		ebuilder.debugStream() << "   Frame Data Type           = " << evt->feb_info[4];
		ebuilder.debugStream() << "   Frame Length (header val) = " << evt->feb_info[5];
#endif
		switch (evt->feb_info[4]) {
			case 0:
				length = 8 + evt->feb_info[5] + 2; // ADC; MINERvA Header + Data + CRC 
				break;
			case 1:
				length = 8 + evt->feb_info[5] + 2; // Discr; MINERvA Header + Data + CRC 
				break;
			case 2:
				length = 8 + evt->feb_info[5] + 2; // FPGA Prog; MINERvA Header + Data + CRC 
				break;
			case 3:
				length = DAQ_HEADER;
				break;
			case 4:
				length = evt->feb_info[5] + 2; // Data + CRC 
			 	std::cout << "WARNING!  TriP programming frames not supported by EventBuilder yet!" << std::endl;
			 	ebuilder.warnStream() << "WARNING!  TriP programming frames not supported by EventBuilder yet!";
				length = 0;
				break;
			default:
				std::cout << "WARNING!  Unknown frame type in EventBuilder main!" << std::endl;
				ebuilder.warnStream() << "WARNING!  Unknown frame type in EventBuilder main!";
				break;	
		}
		et_event_getdata(pe, &pdata); //get the event ready
		unsigned char final_buffer[length];
		unsigned char *tmp_buffer; 
#if DEBUG_BUFFERS
		ebuilder.debugStream() << "   event_builder::main(): Final data buffer length = " << length;
#endif
		if (evt->feb_info[4]!=3) {
			tmp_buffer = event->GetDataBlock();
#if DEBUG_BUFFERS
			ebuilder.debugStream() << " event_builder::main(): Copying Data Header data into final buffer.";
#endif
			for (int data_index = 0; data_index < length; data_index++) {
				final_buffer[data_index] = tmp_buffer[data_index];
			}
			// Clean up memory - remove data_block created in MakeDataBlock
			// Strongly suspect this is fixing a small memory leak... - 2010.May.4
			event->DeleteDataBlock();
		} else { 
#if DEBUG_BUFFERS
			ebuilder.debugStream() << " event_builder::main(): Copying DAQ Header data into final buffer.";
#endif
			for (int data_index = 0; data_index < length; data_index++) {
				final_buffer[data_index] = event->GetEventBlock(data_index);
			}
		}

#if !NEARLINE
		//memcpy (pdata, (void *) final_buffer, length);
		//et_event_setlength(pe,length);
#endif

		// Put the event back into the ET system.
		status = et_event_put(sys_id, attach, pe); 
		evt_counter++;
		// Now write the event to the binary output file.
		binary_outputfile.write((char *) final_buffer, length);  
		binary_outputfile.flush();
		delete event;
	}
	// Detach from the station.
	if (et_station_detach(sys_id, attach) < 0) {
		printf("et_producer: error in station detach\n");
		ebuilder.fatal("et_producer: error in station detach\n");
		system("sleep 10s");
		exit(1);
	}

	// Close ET
	if (et_close(sys_id) < 0) {
		printf("et_producer: error in ET close\n");
		ebuilder.fatal("et_producer: error in ET close\n");
		system("sleep 10s");
		exit(1);
	}
	binary_outputfile.close(); 

	ebuilder.infoStream() << "Closing the Event Builder!";
	// Clean up the log4cpp file.
	log4cpp::Category::shutdown();

	return 0; // Success!
}


int event_builder(event_handler *evt) 
{
#if DEBUG_REPORT_EVENT
	ebuilder.debugStream() << "*************************************************************************"; 
	ebuilder.debugStream() << "Processing Event Data in event_builder::main():";
	ebuilder.debugStream() << "  GATE : "             << evt->gate;
	ebuilder.debugStream() << "    CROC ----------: " << evt->feb_info[2];
	ebuilder.debugStream() << "    CHAN ----------: " << evt->feb_info[3];
	ebuilder.debugStream() << "    FEB -----------: " << evt->feb_info[6];
	ebuilder.debugStream() << "    BANK ----------: " << evt->feb_info[4];
	ebuilder.debugStream() << "    BUFFER_LENGTH -: " << evt->feb_info[5];
	ebuilder.debugStream() << "    FIRMWARE ------: " << evt->feb_info[7];
	ebuilder.debugStream() << "    DETECTOR ------: " << (int)evt->detectorType; 
	ebuilder.debugStream() << "    CONFIG --------: " << evt->detectorConfig; 
	ebuilder.debugStream() << "    RUN -----------: " << evt->runNumber;
	ebuilder.debugStream() << "    SUB-RUN -------: " << evt->subRunNumber;
	ebuilder.debugStream() << "    TRIGGER -------: " << evt->triggerType;
	ebuilder.debugStream() << "    GLOBAL GATE ---: " << evt->globalGate;
	ebuilder.debugStream() << "    TRIG TIME -----: " << evt->triggerTime;
	ebuilder.debugStream() << "    ERROR ---------: " << evt->readoutInfo;
	ebuilder.debugStream() << "    MINOS ---------: " << evt->minosSGATE;
	ebuilder.debugStream() << "    EMBEDDED LENGTH: " << (int)( evt->event_data[0] + (evt->event_data[1]<<8) );
        ebuilder.debugStream() << "    DUMMY BYTE ----: " << (int)evt->event_data[10];
#endif
	MinervaHeader *tmp_header;
	int gate_counter = 0;	
	// 56?  TODO 54 registers in modern feb firmware, should replace with variable argument anyway...
	feb *dummy_feb = new feb(6,1,(febAddresses)0,56); // Make a dummy feb for access to the header decoding functions. 
	if (evt->feb_info[4]==3) {
		gate_counter = evt->gate;
		// Set the "Trigger Time"
		struct timeval triggerNow;
		gettimeofday(&triggerNow, NULL);
		unsigned long long totaluseconds = ((unsigned long long)(triggerNow.tv_sec))*1000000 +
			(unsigned long long)(triggerNow.tv_usec);
		evt->triggerTime = totaluseconds;
		if (!(gate_counter%gate_print_freq)) { 
			printf("Gate: %5d ; Trigger Time = %llu ; ", gate_counter, evt->triggerTime);
			fflush(stdout);
			ebuilder.info("Gate: %5d ; Trigger Time = %llu", gate_counter, evt->triggerTime);
			switch(evt->triggerType) {
				case 0:
					printf("Trigger =   Unknown\n");
					ebuilder.info("\tTrigger =   Unknown");
#if !MTEST
					printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
					ebuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
					break;
				case 1:
					printf("Trigger =   OneShot\n"); 
					ebuilder.info("\tTrigger =   OneShot"); 
#if !MTEST
					printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
						adcFrameCount, discFrameCount, fpgaFrameCount);
					ebuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
						adcFrameCount, discFrameCount, fpgaFrameCount);
#endif
					if (adcFrameCount > adcFrameWarningCount) {
						printf("  WARNING - Excessive number of ADC Frames in a pedestal trigger!\n");
						ebuilder.warn("  WARNING - Excessive number of ADC Frames in a pedestal trigger!");
					} 
					break;
				case 2:
					printf("Trigger =  LightInj\n"); 
					ebuilder.info("\tTrigger =  LightInj"); 
#if !MTEST
					printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
					ebuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
					break;
				case 8:
					printf("Trigger =    Cosmic\n"); 
					ebuilder.info("\tTrigger =    Cosmic"); 
#if !MTEST
					printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
					ebuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
					break;
				case 16:
					printf("Trigger =      NuMI\n"); 
					ebuilder.info("\tTrigger =      NuMI"); 
#if !MTEST
					printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
					ebuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
					break;
				case 32:
					printf("Trigger = MTBF Muon\n"); 
					ebuilder.info("\tTrigger = MTBF Muon"); 
#if !MTEST
					printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
					ebuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
					break;
				case 64:
					printf("Trigger = MTBF Beam\n"); 
					ebuilder.info("\tTrigger = MTBF Beam"); 
#if !MTEST
					printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
					ebuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
						adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
					break;
				default:
					printf("Trigger incorrctly set!\n"); 
					ebuilder.warn("Trigger incorrctly set!\n"); 
			}
			fflush(stdout);
		}
		if (evt->readoutInfo) {
			if (evt->readoutInfo & 0x1) {
				printf("  Readout took too long - stopped early!\n");
				ebuilder.crit("  Readout took too long - stopped early!\n");
				fflush(stdout);
			}
			if (evt->readoutInfo & 0x2) {
				printf("  Found an error on VME Crate 0!\n");
				ebuilder.crit("  Found an error on VME Crate 0!\n");
				fflush(stdout);
			}
			if (evt->readoutInfo & 0x4) {
				printf("  Found an error on VME Crate 1!\n");
				ebuilder.crit("  Found an error on VME Crate 1!\n");
				fflush(stdout);
			}
		}
		// Build the "DAQ" header
		tmp_header = new MinervaHeader(evt->feb_info[1], ebAppender); //the special constructor for the DAQ bank
		// Make the new event block
		event = new MinervaEvent(evt->detectorType, evt->detectorConfig, evt->runNumber, 
			evt->subRunNumber, evt->triggerType, evt->ledLevel, evt->ledGroup, evt->globalGate, 
			evt->gate, evt->triggerTime, evt->readoutInfo, evt->minosSGATE, tmp_header, ebAppender); 
		// The call to MinervaEvent constructor automatically inserts the DAQ block into the event buffer.
		// Reset frame counters.
		adcFrameCount = discFrameCount = fpgaFrameCount = 0;
	} else {
		event = new MinervaEvent();

		// Sort the event data
		int info_length = (int)( evt->event_data[0] + (evt->event_data[1]<<8) + 2); // Data + Frame CRC
		switch (evt->feb_info[4]) {
			case 0: // ADC Data
				// Compare embedded length (data) + CRC to info_length		
				CheckBufferLength(evt->feb_info[5]+2, info_length); 
				for (unsigned int i=0; i<evt->feb_info[5]; i+=info_length) {
					DecodeBuffer(evt, dummy_feb->GetADC(0), i, info_length);
					// Build the data block header.
					tmp_header = BuildBankHeader(evt, dummy_feb->GetADC(0));
					// Build event.
					event->MakeDataBlock(dummy_feb->GetADC(0), tmp_header);
				}
				adcFrameCount++;
				break;
			case 1: // Discriminator Data
				// Compare embedded length (data) + CRC to info_length	
				CheckBufferLength(evt->feb_info[5]+2, info_length);
				for (unsigned int i = 0; i < evt->feb_info[5]; i+=info_length) {
					DecodeBuffer(evt, dummy_feb->GetDisc(), i, info_length);
					// Build the data block header.
					tmp_header = BuildBankHeader(evt, dummy_feb->GetDisc());
					// Build event.
					event->MakeDataBlock(dummy_feb->GetDisc(), tmp_header);
				}
				discFrameCount++;
				break;
			case 2: // FEB Data
				// Compare embedded length (data) + CRC to info_length				
				CheckBufferLength(evt->feb_info[5]+2, info_length);
				for (unsigned int i = 0; i < evt->feb_info[5]; i+=info_length) {
					DecodeBuffer(evt, dummy_feb, i, info_length);
					// Build the data block header
					tmp_header = BuildBankHeader(evt, dummy_feb);
					// Build event  
					event->MakeDataBlock(dummy_feb, tmp_header);
				}
				fpgaFrameCount++;
				break;
			case 3: // DAQ Event Info (End of Record Bank)
				std::cout << "Error in event_builder::main()!" << std::endl;
				std::cout << "Received a DAQ event bank on a current event!" << std::endl;
				ebuilder.critStream() << "Error in event_builder::main()!";
				ebuilder.critStream() << "Received a DAQ event bank on a current event!";
				return (-1);
			case 4:
				std::cout << "Error in event_builder::main()!" << std::endl;
				std::cout << "TriP Programming Frames not supported yet!" << std::endl;
				ebuilder.critStream() << "Error in event_builder::main()!";
				ebuilder.critStream() << "TriP Programming Frames not supported yet!";
				return (-1);
			default:
				std::cout << "Error in event_builder::main()!" << std::endl;
				std::cout << "Failed Event Bank!" << std::endl;
				ebuilder.critStream() << "Error in event_builder::main()!";
				ebuilder.critStream() << "Failed Event Bank!";
				return (-1);
		}
	}

#if DEBUG_REPORT_EVENT
	ebuilder.debugStream() << "Completed event_builder::main()! Processed Event Data!";
#endif
	// Clean up memory.
	delete dummy_feb;
	delete tmp_header;

	return 0;
}  


void HandleErrors(int success) 
{ 
/*! \fn a little event handler
 *
 * \param success the return value for an unsuccessful execution 
 *
 */
	try  {
		if (success<0) throw (success);
	} catch (int e) {
		perror("server read");
		ebuilder.fatal("server read error in HandleErrors");
		exit(EXIT_FAILURE);
	}
} 


void CheckBufferLength(int length, int frame_length) 
{
/*! \fn A function to make sure that the buffer length is correct. 
 *
 * \param length the returned buffer lenght
 * \param frame_length the lenght that the frame is supposed to be
 */
	if (length != frame_length) {
		std::cout << "Buffer length, frame length disparity in event_builder::CheckBufferLength!" << endl;
		ebuilder.fatalStream() << "Buffer length, frame length disparity in event_builder::CheckBufferLength!";
		exit(-4);
	}
}


template <class X> MinervaHeader* BuildBankHeader(event_handler *evt, X *frame)
{
/*! \fn 
 *
 * Templated function for building up the bank headers.
 *
 * \param event_handler *evt a copy of the event handler structure
 * \param X *frame the data frame
 */
	int feb_number = frame->GetFEBNumber(); //get the feb number from which this frame came
	int length     = evt->event_data[0] + (evt->event_data[1]<<8) + 2; // Data + CRC

	//now we've got everything we need to make up the event headers
	MinervaHeader *tmp_header; //declare a new data bank header
	if (evt->feb_info[4]==3) {
		std::cout << "Should not have passed DAQ block to BuildBlockHeader!" << std::endl;
		ebuilder.fatalStream() << "Should not have passed DAQ block to BuildBlockHeader!";
		exit (-1);
	} else {
#if DEBUG_BANKHEADER
		ebuilder.debugStream() << "  ----------BuildBankHeader----------";
		ebuilder.debugStream() << "  crateID                       : " << evt->feb_info[1];
		ebuilder.debugStream() << "  crocID                        : " << evt->feb_info[2];
		ebuilder.debugStream() << "  chanID                        : " << evt->feb_info[3];
		ebuilder.debugStream() << "  bank                          : " << evt->feb_info[4];
		ebuilder.debugStream() << "  feb_number (from frame header): " << feb_number;
		ebuilder.debugStream() << "  feb_number (from feb_info)    : " << evt->feb_info[6];
		ebuilder.debugStream() << "  firmware                      : " << evt->feb_info[7];
		ebuilder.debugStream() << "  hit                           : " << evt->feb_info[8];
		ebuilder.debugStream() << "  length                        : " << length;
#endif          
		tmp_header = new MinervaHeader(evt->feb_info[1], evt->feb_info[2], evt->feb_info[3],
			evt->feb_info[4], feb_number, evt->feb_info[7],
			evt->feb_info[8], length); // Compose a regular data block header.
	}
	return tmp_header; //return the header
};


template <class X> void DecodeBuffer(event_handler *evt, X *frame, int i, int length)
{
/*! \fn
 *
 * A templated function for decoding a data buffer
 *
 * \param event_handler *evt a pointer to the event handler structure
 * \param X *frame the data frame
 * \param int i byte offset
 * \param int length the message length 
 */
#if DEBUG_DECODEBUFFER
	ebuilder.debugStream() << "  DecodeBuffer Parameters: ";
	ebuilder.debugStream() << "   byte offset: " << i;
	ebuilder.debugStream() << "   msg length:  " << length;
#endif
	frame->message = new unsigned char [length];
	for (int j = 0; j < length;j ++) {
		frame->message[j] = 0;
	}
	for (int j = 0; j < length; j++) {
#if DEBUG_DECODEBUFFER
		ebuilder.debugStream() << "    byte: " << j+i;
#endif
		unsigned char tmp = evt->event_data[(j+i)];
		frame->message[j]=tmp; //copy to a local buffer for processing
#if DEBUG_DECODEBUFFER
		ebuilder.debugStream() << "    frame->message: " << (int)frame->message[j];
		ebuilder.debugStream() << "              data? " << (int)tmp;
#endif
	}
#if DEBUG_DECODEBUFFER
	ebuilder.debugStream() << "    Loaded Message";
#endif
	frame->CheckForErrors(); //check for header errors
#if DEBUG_DECODEBUFFER
	ebuilder.debugStream() << "    Checked for Errors, going to DecodeHeader";
#endif
	frame->DecodeHeader(); //find feb number in header
#if DEBUG_DECODEBUFFER
	ebuilder.debugStream() << "  Done Decoding the Buffer";
#endif
};


