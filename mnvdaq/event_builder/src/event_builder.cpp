#include "event_builder.h"
#include "event_builder_templates.h"

using namespace std;

#if DEBUG_THREAD
ofstream thread_log("eb_log.txt");
#endif

static int gate_counter    =  0;
const int  gate_print_freq = 10;

int main(int argc, char **argv) 
{
/*! \fn The main function for running the event builder. 
 * This function is the MINERvA-specific implementation 
 * of the generic et_producer class.  
 */
	if (argc != 3) {
		printf("Usage: event_builder <et_filename> <rawdata_filename>\n");
		printf("  Please supply the full path!\n");
		exit(1);
	}

	// Open the file for binary output.
	string output_filename(argv[2]);
	//output_filename = "/work/data/rawdata/" + output_filename + ".dat"; // this doesn't work for some reason...
	std::cout << "Ouptut Filename = " << output_filename << std::endl;
	std::cout << "ET Filesystem   = " << argv[1] << std::endl;
	ofstream binary_outputfile(output_filename.c_str(),ios::out|ios::app|ios::binary); 

	// int            event_size; // unused...
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

	// The station name for the DAQ Event Builder.
	// For some reason, using this creates problems for the DAQ.  Keep it commented out for now.
	//std::string station_name("CHICAGO_UNION");

	// Opening the ET system is the first thing we must do...
	et_open_config_init(&openconfig);
#if MULTI_PC
	et_open_config_setmode(&openconfig, ET_HOST_AS_REMOTE);
	et_open_config_setcast(openconfig, ET_DIRECT);
	et_open_config_sethost(openconfig, "mnvonlinemaster.fnal.gov"); // Adjust, etc.
	et_open_config_setserverport(openconfig, 1091); 
#endif

#if NEARLINE
	et_open_config_setmode(&openconfig, ET_HOST_AS_REMOTE);
	et_open_config_setcast(openconfig, ET_DIRECT);
	et_open_config_sethost(openconfig, "mnvonline1.fnal.gov"); // Adjust, etc.
	et_open_config_setserverport(openconfig, 1091);
	//station_name = "RIODEJANEIRO"; // For some reason, the DAQ has problems if we use these...
#endif

	if (et_open(&sys_id, argv[1], openconfig) != ET_OK) {
		printf("event_builder::main(): et_producer: et_open problems\n");
		exit(1);
	}
	et_open_config_destroy(openconfig);

	// Check if ET is up and running.
	// This evidently does not work for NearOnline stations?
	// It seems to work for both multi and single PC DAQ running...
#if !NEARLINE
	std::cout << "Running a DAQ Station..." << std::endl;
	unsigned int oldheartbeat, newheartbeat;
	id = (et_id *) sys_id;
	oldheartbeat = id->sys->heartbeat;
	int counter = 0;
	do {
		system("sleep 10s"); // Give ET a chance to start...
		if (!counter) {
			newheartbeat = id->sys->heartbeat;
		} else {
			oldheartbeat=newheartbeat;
			newheartbeat = id->sys->heartbeat;
		}
		counter++;  
	} while ((newheartbeat==oldheartbeat)&&(counter!=20));
	if (counter==20) {
		std::cout << "Error in event_builder::main()!" << std::endl;
		std::cout << "ET System did not start properly!  Exiting..." << std::endl;
		exit(-5);
	} 
#endif

	// Set the level of debug output that we want (everything).
	et_system_setdebug(sys_id, ET_DEBUG_INFO);

	// Create & attach to a new station for making the final output file.
#if NEARLINE
	et_station_create(sys_id,&cu_station,"RIODEJANEIRO",sconfig);
#else
	et_station_create(sys_id,&cu_station,"CHICAGO_UNION",sconfig);
#endif
	if (et_station_attach(sys_id, cu_station, &attach) < 0) {
		printf("event_builder::main(): et_producer: error in station attach\n");
		system("sleep 10s");
		exit(1);
	}

	// Request an event from the ET service.
	int evt_counter = 0;
	while ((et_alive(sys_id))) {
		struct timespec time;
		time.tv_sec = 60;
		status = et_event_get(sys_id, attach, &pe, ET_TIMED|ET_MODIFY, &time);
		if (status==ET_ERROR_TIMEOUT) break;
		if (status == ET_ERROR_DEAD) {
			printf("event_builder::main(): et_client: ET system is dead\n");
			exit(-1);
		}
		else if (status == ET_ERROR_TIMEOUT) {
			printf("event_builder::main(): et_client: got timeout\n");
			exit(-1);
		}
		else if (status == ET_ERROR_EMPTY) {
			printf("event_builder::main(): et_client: no events\n");
			exit(-1);
		}
		else if (status == ET_ERROR_BUSY) {
			printf("event_builder::main(): et_client: station is busy\n");
			exit(-1);
		}
		else if (status == ET_ERROR_WAKEUP) {
			printf("event_builder::main(): et_client: someone told me to wake up\n");
			exit(-1);
		}
		else if ((status == ET_ERROR_WRITE) || (status == ET_ERROR_READ)) {
			printf("event_builder::main(): et_client: socket communication error\n");
			exit(-1);
		}
		else if (status != ET_OK) {
			printf("event_builder::main(): et_client: get error\n");
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
		printf(" event_builder::main(): Building final data buffers...\n");
		printf("   Frame Data Type           = %d\n",evt->feb_info[4]);
		printf("   Frame Length (header val) = %d\n",evt->feb_info[5]);
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
				length = 0;
				break;
			default:
				std::cout << "WARNING!  Unknown frame type in EventBuilder main!" << std::endl;
				break;	
		}
		et_event_getdata(pe, &pdata); //get the event ready
		unsigned char final_buffer[length];
		unsigned char *tmp_buffer; 
#if DEBUG_BUFFERS
		printf("   event_builder::main(): Final data buffer length = %d\n",length);
#endif
		if (evt->feb_info[4]!=3) {
			tmp_buffer = event->GetDataBlock();
#if DEBUG_BUFFERS
			printf(" event_builder::main(): Copying Data Header data into final buffer...\n");
#endif
			for (int data_index = 0; data_index < length; data_index++) {
				final_buffer[data_index] = tmp_buffer[data_index];
			}
		} else { 
#if DEBUG_BUFFERS
			printf(" event_builder::main(): Copying DAQ Header data into final buffer...\n");
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
		if ( !( evt_counter%10000 ) ) {
			std::cout << "*****************************************************************" << std::endl; 
			std::cout << "  event_builder::main(): Event (Frame) Processed: " << evt_counter << std::endl;
		}
		delete event;
	}
	// Detach from the station.
	if (et_station_detach(sys_id, attach) < 0) {
		printf("et_producer: error in station detach\n");
		system("sleep 10s");
		exit(1);
	}

	// Close ET
	if (et_close(sys_id) < 0) {
		printf("et_producer: error in ET close\n");
		system("sleep 10s");
		exit(1);
	}
	binary_outputfile.close(); 

	return 0; // Success!
}


int event_builder(event_handler *evt) 
{
#if DEBUG_REPORT_EVENT
	std::cout << "*************************************************************************" << std::endl; 
	std::cout << "Processing Event Data in event_builder::main():"<< std::endl;
	std::cout << "  GATE : "<< evt->gate << std::endl;
	std::cout << "    CROC ----------: " << evt->feb_info[2] << std::endl;
	std::cout << "    CHAN ----------: " << evt->feb_info[3] << std::endl;
	std::cout << "    FEB -----------: " << evt->feb_info[6] << std::endl;
	std::cout << "    BANK ----------: " << evt->feb_info[4] << std::endl;
	std::cout << "    BUFFER_LENGTH -: " << evt->feb_info[5] << std::endl;
	std::cout << "    FIRMWARE ------: " << evt->feb_info[7] << std::endl;
	std::cout << "    DETECTOR ------: " << (int)evt->detectorType << std::endl; 
	std::cout << "    CONFIG --------: " << evt->detectorConfig << std::endl; 
	std::cout << "    RUN -----------: " << evt->runNumber << std::endl;
	std::cout << "    SUB-RUN -------: " << evt->subRunNumber << std::endl;
	std::cout << "    TRIGGER -------: " << evt->triggerType << std::endl;
	std::cout << "    GLOBAL GATE ---: " << evt->globalGate << std::endl;
	std::cout << "    TRIG TIME -----: " << evt->triggerTime << std::endl;
	std::cout << "    ERROR ---------: " << evt->readoutInfo << std::endl;
	std::cout << "    MINOS ---------: " << evt->minosSGATE << std::endl;
	std::cout << "    EMBEDDED LENGTH: " << (int)( evt->event_data[0] + (evt->event_data[1]<<8) ) << std::endl;
        std::cout << "    DUMMY BYTE ----: " << (int)evt->event_data[10] << std::endl;
#endif
	MinervaHeader *tmp_header;
	// 56?  TODO 54 registers in modern feb firmware, should replace with variable argument anyway...
	feb *dummy_feb = new feb(6,1,(febAddresses)0,56); // Make a dummy feb for access to the header decoding functions. 
	if (evt->feb_info[4]==3) {
		gate_counter++;
		if (!(gate_counter%gate_print_freq)) std::cout << "Gate: " << gate_counter << std::endl;
		// Build the "DAQ" header
		tmp_header = new MinervaHeader(evt->feb_info[1]); //the special constructor for the DAQ bank
		// Make the new event block
		event = new MinervaEvent(evt->detectorType, evt->detectorConfig, evt->runNumber, 
			evt->subRunNumber, evt->triggerType, evt->ledLevel, evt->ledGroup, evt->globalGate, 
			evt->gate, evt->triggerTime, evt->readoutInfo, evt->minosSGATE, tmp_header); 
		// The call to MinervaEvent constructor automatically inserts the DAQ block into the event buffer
	} else {
		event = new MinervaEvent();

		// Sort the event data
		int info_length = (int)( evt->event_data[0] + (evt->event_data[1]<<8) + 2); // Data + Frame CRC
		switch (evt->feb_info[4]) {
			case 0: // ADC Data
#if DEBUG_VERBOSE
				std::cout << "\nevent_builder::main(): ADC Values" << std::endl;
#endif
				// Compare embedded length (data) + CRC to info_length		
				CheckBufferLength(evt->feb_info[5]+2, info_length); 
				for (unsigned int i=0; i<evt->feb_info[5]; i+=info_length) {
					DecodeBuffer(evt, dummy_feb->GetADC(0), i, info_length);
					// Build the data block header.
					tmp_header = BuildBankHeader(evt, dummy_feb->GetADC(0));
					// Build event.
					event->MakeDataBlock(dummy_feb->GetADC(0), tmp_header);
				}
				break;
			case 1: // Discriminator Data
#if DEBUG_VERBOSE
				std::cout << "\nevent_builder::main(): DISC Values" << std::endl;
#endif
				// Compare embedded length (data) + CRC to info_length	
				CheckBufferLength(evt->feb_info[5]+2, info_length);
				for (unsigned int i = 0; i < evt->feb_info[5]; i+=info_length) {
					DecodeBuffer(evt,dummy_feb->GetDisc(), i, info_length);
					// Build the data block header.
					tmp_header = BuildBankHeader(evt, dummy_feb->GetDisc());
					// Build event.
					event->MakeDataBlock(dummy_feb->GetDisc(), tmp_header);
				}
				break;
			case 2: // FEB Data
#if DEBUG_VERBOSE
				std::cout << "\nevent_builder::main(): FPGA Programming Values" << std::endl;
#endif
				// Compare embedded length (data) + CRC to info_length				
				CheckBufferLength(evt->feb_info[5]+2, info_length);
				for (unsigned int i = 0; i < evt->feb_info[5]; i+=info_length) {
					DecodeBuffer(evt, dummy_feb, i, info_length);
					// Build the data block header
					tmp_header = BuildBankHeader(evt, dummy_feb);
					// Build event  
					event->MakeDataBlock(dummy_feb, tmp_header);
				}
				break;
			case 3: // DAQ Event Info (End of Record Bank)
				std::cout << "Error in event_builder::main()!" << std::endl;
				std::cout << "Received a DAQ event bank on a current event!" << std::endl;
				return (-1);
			case 4:
				std::cout << "Error in event_builder::main()!" << std::endl;
				std::cout << "TriP Programming Frames not supported yet!" << std::endl;
				return (-1);
			default:
				std::cout << "Error in event_builder::main()!" << std::endl;
				std::cout << "Failed Event Bank!" << std::endl;
				return (-1);
		}
	}

#if DEBUG_VERBOSE
	std::cout << "Completed event_builder::main()! Processed Event Data!" << std::endl;
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
		std::cout << "Buffer length, frame length disparity in event_builder::CheckBufferLength!." << endl;
		exit(-4);
	}
}

