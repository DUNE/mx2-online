#ifndef EventBuilder_cxx
#define EventBuilder_cxx

#include "EventBuilder.h"
#include "exit_codes.h"
#include <ctime>
#include <sys/time.h>
#include <signal.h>
#include <errno.h>

using namespace std;

/*
// How long the event builder will wait for new frames before declaring no more are coming.
// Only relevant after receiving SIGTERM/SIGINT (otherwise we just wait until we get the
// sentinel gate instead).
const int SECONDS_BEFORE_TIMEOUT = 60; 

DAQEvent *event;
*/

// TODO: Move the function decl to the header file when we retire the old event_builder.
sig_atomic_t waiting_to_quit;  
sig_atomic_t quit_now;        
void quitsignal_handler(int signum);

// log4cpp Variables - Needed throughout the event_builder functions.
log4cpp::Appender* eventBuilderAppender;
log4cpp::Category& rootCategory = log4cpp::Category::getRoot();
log4cpp::Category& eventbuilder = log4cpp::Category::getInstance(std::string("eventbuilder"));

int main(int argc, char **argv) 
{
  if (argc < 3) {
    printf("Usage: event_builder <et_filename> <rawdata_filename> <network port (default 1201)> <callback PID (default: no PID)>\n");
    printf("  Please supply the full path!\n");
    exit(EXIT_CONFIG_ERROR);
  }
  std::cout << "ET Filesystem          = " << argv[1] << std::endl;
  string output_filename(argv[2]);
  // Open the file for binary output.
  ofstream binary_outputfile(output_filename.c_str(),ios::out|ios::app|ios::binary); 
  int networkPort = 1201;
  if (argc > 3) networkPort = atoi(argv[3]);
  std::cout << "ET Network Port        = " << networkPort << std::endl;

  int callback_pid = 0;
  if (argc > 4)
  {
    callback_pid = atoi(argv[4]);
    std::cout << "Notifying process " << callback_pid << " when ready to accept events." << std::endl;
  }

  struct timeval hpnow; 
	gettimeofday(&hpnow,NULL);

  char log_filename[100]; 
  // TODO: Setup precompiler options for logs on Nearline, other machines, and timestamping.
	sprintf(log_filename, "/work/logs/EventBuilderLog.txt"); 

  eventBuilderAppender = new log4cpp::FileAppender("default", log_filename,false);
  eventBuilderAppender->setLayout(new log4cpp::BasicLayout());
  rootCategory.addAppender(eventBuilderAppender);
  rootCategory.setPriority(log4cpp::Priority::DEBUG);
  eventbuilder.setPriority(log4cpp::Priority::DEBUG);
  rootCategory.infoStream()   << "Starting the MINERvA DAQ Event Builder. ";
  eventbuilder.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
  eventbuilder.infoStream() << "Arguments to the Event Builder: ";
  eventbuilder.infoStream() << "  ET System              = " << argv[1];
  eventbuilder.infoStream() << "  Output Filename        = " << output_filename;
  eventbuilder.infoStream() << "  ET System Port         = " << networkPort;
  eventbuilder.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";

  char hostName[100];
  // TODO: Setup precompiler options for hostnames on multi-PC and various other locations.
  sprintf(hostName, "localhost");
  eventbuilder.infoStream() << "Configured for a Single-PC Build..."; 
  eventbuilder.infoStream() << "ET system host machine = " << hostName;

  // Set up the signal handler so we can always exit cleanly
  struct sigaction quit_action;
  quit_action.sa_handler = quitsignal_handler;
  sigemptyset (&quit_action.sa_mask);
  quit_action.sa_flags = SA_RESTART;		// restart interrupted system calls instead of failing with EINTR

  sigaction(SIGINT,  &quit_action, NULL);
  sigaction(SIGTERM, &quit_action, NULL);

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
    eventbuilder.fatal("event_builder::main(): et_producer: et_open problems\n");
    exit(EXIT_ETSTARTUP_ERROR);
  }
  et_open_config_destroy(openconfig);

/* ******************************************************
  // Check if ET is up and running.
#if !NEARLINE
  std::cout << "Running a DAQ Station..." << std::endl;
  std::cout << "  Waiting for ET..." << std::endl;
  eventbuilder.infoStream() << "Running a DAQ Station...";
  eventbuilder.infoStream() << "  Waiting for ET...";
  unsigned int oldheartbeat, newheartbeat;
  id = (et_id *) sys_id;
  oldheartbeat = id->sys->heartbeat;
  int counter = 0;
  do {
    // Give ET a chance to start...
    // For modern DAQ operations, we take care of this beforehand.
    // So set this check to use a very short sleep period!
    std::cout << "  Synching heartbeat..." << std::endl;
    eventbuilder.infoStream() << "  Synching heartbeat...";
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
    eventbuilder.fatalStream() << "Error in event_builder::main()!";
    eventbuilder.fatalStream() << "ET System did not start properly!  Exiting...";
    exit(EXIT_ETSTARTUP_ERROR);
  } 
#endif

  // Set the level of debug output that we want (everything).
  et_system_setdebug(sys_id, ET_DEBUG_INFO);

  // Create & attach to a new station for making the final output file.
  std::cout << "Creating new station for output..." << std::endl;
#if NEARLINEPRO||NEARLINEBCK
  et_station_create(sys_id,&cu_station,"RIODEJANEIRO",sconfig);
  eventbuilder.infoStream() << "Creating new station RIODEJANEIRO for output...";
#elif NEARLINEDEV
  et_station_create(sys_id,&cu_station,"ROCHESTER",sconfig);
  eventbuilder.infoStream() << "Creating new station ROCHESTER for output...";
#else
  et_station_create(sys_id,&cu_station,"CHICAGO_UNION",sconfig);
  eventbuilder.infoStream() << "Creating new station CHICAGO_UNION for output...";
#endif
  std::cout << "Attaching to new station..." << std::endl;
  if (et_station_attach(sys_id, cu_station, &attach) < 0) {
    printf("event_builder::main(): et_producer: error in station attach\n");
    system("sleep 10s");
    exit(EXIT_ETSTARTUP_ERROR);
  }

  // send the SIGUSR1 signal to the specified process signalling that ET is ready
  std::cout << "Sending ready signal to ET system..." << std::endl;
  eventbuilder.infoStream() << "Sending ready signal to ET system...";
  int failure;
  if (callback_pid)
  {
    failure = kill(callback_pid, SIGUSR1);
    if (failure)
    {
      printf("Warning: signal was not delivered to parent process.  Errno: %d\n", failure);
      eventbuilder.warnStream() << "Signal was not delivered to parent process.  Errno: " << failure;
      fflush(stdout);
    }

  }

  // Request an event from the ET service.
  std::cout << " Starting!" << std::endl;
  std::cout << "\n If there is beam and 60 seconds goes by and the DAQ doesn't start, please " << std::endl; 
  std::cout << " skip to the next subrun or stop and try again." << std::endl;
  std::cout << "\n If the event builder exits cleanly and no events were taken, check the " << std::endl; 
  std::cout << " electronics for errors!" << std::endl;
  std::cout << "\n In either case, please note the run and subrun and email them to Gabe Perdue: " << std::endl;
  std::cout << "\t perdue AT fnal DOT gov" << std::endl;
  std::cout << std::endl;
  int evt_counter = 0;
  bool continueRunning = true;
  while ((et_alive(sys_id)) && continueRunning) {
    struct timespec time;
    //printf("time: %d.%i\n", time.tv_sec, time.tv_nsec);

    // there are two different circumstances under which we will acquire events.
    //
    // the first is normal operation: minervadaq is running smoothly; we just
    // take events from ET until we reach the sentinel gate, then quit.
    //
    // the second is when minervadaq crashes.  in this case the run control
    // (or the user who is running the DAQ via shell scripts) will inform this
    // process that it shouldn't expect the sentinel by sending the SIGINT (ctrl-c)
    // or SIGTERM signal (sent by 'kill <pid>').  when that happens, we will collect
    // any outstanding frames currently in the system, then wait
    // a maximum of 60 seconds (customizable in event_builder.h) for new frames
    // before declaring that no more data is coming and that the event builder
    // should quit.

    if (!waiting_to_quit)
    {
      // case 1: try to get an event but return immediately.

      time.tv_sec  = 0;
      time.tv_nsec = 1000; // wait 1 microsecond

      // sleep to avoid a busy-wait.
      // commenting this sleep out for now - this will keep the CPU engaged 
      // more or less full time, but keeps the event builder running in time 
      // with the main acquisition sequence and avoids any possibility of pile
      // up.  still, keep an eye on this...
      //nanosleep( &time, NULL );

      // if no events are available, this will return ET_ERROR_EMTPY.
      // since it's not ET_OK, it will force us to go around and ask
      // for another event (the 'continue' is below the specific error
      // handling that follows below).  note that the 'time' parameter
      // is ignored in this mode.
      status = et_event_get(sys_id, attach, &pe, ET_ASYNC, &time);
    }
    else if (waiting_to_quit && !quit_now)
    {
      // case 2: try to get an event, but time out after the specified interval.

      time.tv_sec = SECONDS_BEFORE_TIMEOUT;
      time.tv_nsec = 0;
      status = et_event_get(sys_id, attach, &pe, ET_TIMED, &time);

      // if we did indeed time out, it's time to quit.
      if (status == ET_ERROR_TIMEOUT)
        continueRunning = false;
    }
    else
    {
      // the user wants to shut down ASAP.
      break;
    }

    // socket errors need to be handled differently depending on locale.
    // for the nearline machines, it's not a tragedy if we miss an event or two.
    // therefore under those circumstances we just go on and try to get another event.
    // in the context of online data taking, however, it's a real problem.
    if ((status == ET_ERROR_WRITE) || (status == ET_ERROR_READ)) {
#if NEARLINE
      printf("Warning: socket error in event_builder::main() calling et_event_get().  Will retry.\n");
      eventbuilder.warn("Socket error in event_builder::main() calling et_event_get().  Will retry.\n");
      fflush(stdout);
#else
      printf("event_builder::main(): et_client: socket communication error\n");
      eventbuilder.fatal("event_builder::main(): et_client: socket communication error\n");
      continueRunning = false;
#endif
    }

    if (status == ET_ERROR_DEAD) {
      printf("event_builder::main(): et_client: ET system is dead\n");
      eventbuilder.fatal("event_builder::main(): et_client: ET system is dead\n");
      continueRunning = false;
    }
    else if (status == ET_ERROR_TIMEOUT) {
      printf("event_builder::main(): et_client: got timeout\n");
      eventbuilder.fatal("event_builder::main(): et_client: got timeout\n");
      continueRunning = false;
    }
    else if (status == ET_ERROR_WAKEUP) {
      printf("event_builder::main(): et_client: someone told me to wake up\n");
      eventbuilder.fatal("event_builder::main(): et_client: someone told me to wake up\n");
      continueRunning = false;
    }

    // if we didn't successfully get a frame, go round and try again.
    if (status != ET_OK)
      continue;

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
    eventbuilder.debugStream() << " event_builder::main(): Building final data buffers...";
    eventbuilder.debugStream() << "   Frame Data Type           = " << evt->feb_info[4];
    eventbuilder.debugStream() << "   Frame Length (header val) = " << evt->feb_info[5];
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
        eventbuilder.warnStream() << "WARNING!  TriP programming frames not supported by EventBuilder yet!";
        length = 0;
        break;
      case 5:
        length = DAQ_HEADER; // Sentinel Frame
        continueRunning = false;
        eventbuilder.infoStream() << "Found sentinel gate.  Ending data taking.";
        break;
      default:
        std::cout << "WARNING!  Unknown frame type in EventBuilder main!" << std::endl;
        eventbuilder.warnStream() << "WARNING!  Unknown frame type in EventBuilder main!";
        break;	
    }
    et_event_getdata(pe, &pdata); //get the event ready
    unsigned char final_buffer[length];
    unsigned char *tmp_buffer; 
#if DEBUG_BUFFERS
    eventbuilder.debugStream() << "   event_builder::main(): Final data buffer length = " << length;
#endif
    if ( (evt->feb_info[4]!=3)&&(evt->feb_info[4]!=5) ) {
      tmp_buffer = event->GetDataBlock();
#if DEBUG_BUFFERS
      eventbuilder.debugStream() << " event_builder::main(): Copying Data Header data into final buffer.";
#endif
      for (int data_index = 0; data_index < length; data_index++) {
        final_buffer[data_index] = tmp_buffer[data_index];
      }
      // Clean up memory - remove data_block created in MakeDataBlock
      event->DeleteDataBlock();
    } else { 
#if DEBUG_BUFFERS
      if (evt->feb_info[4]==3)
        eventbuilder.debugStream() << " event_builder::main(): Copying DAQ Header data into final buffer.";
      if (evt->feb_info[4]==5)
        eventbuilder.debugStream() << " event_builder::main(): Copying Sentinel frame data into final buffer.";
#endif
      for (int data_index = 0; data_index < length; data_index++) {
        final_buffer[data_index] = event->GetEventBlock(data_index);
      }
    }

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
    eventbuilder.fatal("et_producer: error in station detach\n");
    system("sleep 10s");
    exit(EXIT_ETSTARTUP_ERROR);
  }

  // Close ET
  if (et_close(sys_id) < 0) {
    printf("et_producer: error in ET close\n");
    eventbuilder.fatal("et_producer: error in ET close\n");
    system("sleep 10s");
    exit(EXIT_ETSTARTUP_ERROR);
  }
  binary_outputfile.close(); 

  eventbuilder.infoStream() << "Closing the Event Builder!";
  // Clean up the log4cpp file.
  log4cpp::Category::shutdown();
********************************** */
  return 0; // Success!
}

/*
int event_builder(event_handler *evt) 
{
#if CRATE0||CRATE1
  gate_print_freq = 1;
#endif 
#if (WH14T||WH14B)&&SINGLEPC
  gate_print_freq = 1;
#endif
#if MTEST
  gate_print_freq = 5;
#endif
#if DEBUG_REPORT_EVENT
  eventbuilder.debugStream() << "*************************************************************************"; 
  eventbuilder.debugStream() << "Processing Event Data in event_builder::main():";
  eventbuilder.debugStream() << "  GATE : "             << evt->gate;
  eventbuilder.debugStream() << "    CROC ----------: " << evt->feb_info[2];
  eventbuilder.debugStream() << "    CHAN ----------: " << evt->feb_info[3];
  eventbuilder.debugStream() << "    FEB -----------: " << evt->feb_info[6];
  eventbuilder.debugStream() << "    BANK ----------: " << evt->feb_info[4];
  eventbuilder.debugStream() << "    BUFFER_LENGTH -: " << evt->feb_info[5];
  eventbuilder.debugStream() << "    FIRMWARE ------: " << evt->feb_info[7];
  eventbuilder.debugStream() << "    DETECTOR ------: " << (int)evt->detectorType; 
  eventbuilder.debugStream() << "    CONFIG --------: " << evt->detectorConfig; 
  eventbuilder.debugStream() << "    RUN -----------: " << evt->runNumber;
  eventbuilder.debugStream() << "    SUB-RUN -------: " << evt->subRunNumber;
  eventbuilder.debugStream() << "    TRIGGER -------: " << evt->triggerType;
  eventbuilder.debugStream() << "    GLOBAL GATE ---: " << evt->globalGate;
  eventbuilder.debugStream() << "    TRIG TIME -----: " << evt->triggerTime;
  eventbuilder.debugStream() << "    ERROR ---------: " << evt->readoutInfo;
  eventbuilder.debugStream() << "    READOUT TIME --: " << evt->readoutTime;
  eventbuilder.debugStream() << "    MINOS ---------: " << evt->minosSGATE;
  eventbuilder.debugStream() << "    EMBEDDED LENGTH: " << (int)( evt->event_data[0] + (evt->event_data[1]<<8) );
  eventbuilder.debugStream() << "    DUMMY BYTE ----: " << (int)evt->event_data[10];
#endif
  MinervaHeader *tmp_header;
  int gate_counter = 0;	
  // 56?  TODO 54 registers in modern feb firmware, should replace with variable argument anyway...
  // Some possibility 56 is a legacy from attempts to read the FPGA's via FIFOBLT messages.
  feb *dummy_feb = new feb(6,1,(febAddresses)0,56); // Make a dummy feb for access to the header decoding functions. 
  if (evt->feb_info[4]==3) {
    gate_counter = evt->gate;
    if (!(gate_counter%gate_print_freq)) { 
      printf("Gate: %5d ; Trigger Time = %llu ; ", gate_counter, evt->triggerTime);
      fflush(stdout);
      eventbuilder.info("Gate: %5d ; Trigger Time = %llu", gate_counter, evt->triggerTime);
      switch(evt->triggerType) {
        case 0:
          printf("Trigger =   Unknown\n");
          eventbuilder.info("\tTrigger =   Unknown");
#if !MTEST
          printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
          eventbuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
          break;
        case 1:
          printf("Trigger =   OneShot\n"); 
          eventbuilder.info("\tTrigger =   OneShot"); 
#if !MTEST
          printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
              adcFrameCount, discFrameCount, fpgaFrameCount);
          eventbuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
              adcFrameCount, discFrameCount, fpgaFrameCount);
#endif
          if (adcFrameCount > adcFrameWarningCount) {
            printf("  WARNING - Excessive number of ADC Frames in a pedestal trigger!\n");
            eventbuilder.warn("  WARNING - Excessive number of ADC Frames in a pedestal trigger!");
          } 
          break;
        case 2:
          printf("Trigger =  LightInj\n"); 
          eventbuilder.info("\tTrigger =  LightInj"); 
#if !MTEST
          printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
          eventbuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
          break;
        case 8:
          printf("Trigger =    Cosmic\n"); 
          eventbuilder.info("\tTrigger =    Cosmic"); 
#if !MTEST
          printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
          eventbuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
          break;
        case 16:
          printf("Trigger =      NuMI\n"); 
          eventbuilder.info("\tTrigger =      NuMI"); 
#if !MTEST
          printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
          eventbuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
          break;
        case 32:
          printf("Trigger = MTBF Muon\n"); 
          eventbuilder.info("\tTrigger = MTBF Muon"); 
#if !MTEST
          printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
          eventbuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
          break;
        case 64:
          printf("Trigger = MTBF Beam\n"); 
          eventbuilder.info("\tTrigger = MTBF Beam"); 
#if !MTEST
          printf("  %4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames\n", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
          eventbuilder.info("\t%4d ADC Frames, %3d Disc. Frames, %3d FPGA Frames", 
              adcFrameCount, discFrameCount, fpgaFrameCount); 
#endif
          break;
        default:
          printf("Trigger incorrctly set!\n"); 
          eventbuilder.warn("Trigger incorrctly set!\n"); 
      }
      fflush(stdout);
    }
    if (evt->readoutInfo) {
      if (evt->readoutInfo & 0x1) {
        printf("  Readout took too long - stopped early!\n");
        eventbuilder.crit("  Readout took too long - stopped early!\n");
        fflush(stdout);
      }
      if (evt->readoutInfo & 0x2) {
        printf("  Found an error on VME Crate 0!\n");
        eventbuilder.crit("  Found an error on VME Crate 0!\n");
        fflush(stdout);
      }
      if (evt->readoutInfo & 0x4) {
        printf("  Found an error on VME Crate 1!\n");
        eventbuilder.crit("  Found an error on VME Crate 1!\n");
        fflush(stdout);
      }
    }
    // Build the "DAQ" header
    tmp_header = new MinervaHeader(evt->feb_info[1], eventBuilderAppender); //the special constructor for the DAQ bank
    // Make the new event block
    event = new MinervaEvent(evt->detectorType, evt->detectorConfig, evt->runNumber, 
        evt->subRunNumber, evt->triggerType, evt->ledLevel, evt->ledGroup, evt->globalGate, 
        evt->gate, evt->triggerTime, evt->readoutInfo, evt->minosSGATE, evt->readoutTime, tmp_header, 
        adcFrameCount, discFrameCount, fpgaFrameCount, eventBuilderAppender); 
    // The call to MinervaEvent constructor automatically inserts the DAQ block into the event buffer.
    // Reset frame counters.
    adcFrameCount = discFrameCount = fpgaFrameCount = 0;
  } else if (evt->feb_info[4]==5) {
    // Build the "Sentinel" Frame
    // Set the "firmware" version to 1, contained frame data length to 48.  (48 empty bytes right now.)
    eventbuilder.infoStream() << "Making the Sentinel Frame.  Bank Type = " << evt->feb_info[4];
    tmp_header = new MinervaHeader(evt->feb_info[1], 0, 0, evt->feb_info[4], 0, 1, 0, 48, eventBuilderAppender); 
    // Make the new "event" block
    event = new MinervaEvent(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, tmp_header, 0, 0, 0, eventBuilderAppender); 
    // The call to MinervaEvent constructor automatically inserts the block into the event buffer.

  } else {
    event = new MinervaEvent();

    // Sort the event data
    // Compute the length of the frame as encoded within itself.
    int info_length = (int)( evt->event_data[0] + (evt->event_data[1]<<8) + 2); // Data + Frame CRC
    switch (evt->feb_info[4]) {
      case 0: // ADC Data
        // Compare DPM Pointer Value (+CRC) to frame length embedded in the data itself.		
        if ( CheckBufferLength(evt->feb_info[5]+2, info_length) ) {
          std::cout << "Buffer length error for the ADC's!" << std::endl;
          eventbuilder.fatalStream() << "Buffer length error for the ADC's!";
          exit(EXIT_FEB_UNSPECIFIED_ERROR);
        }
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
        // Compare DPM Pointer Value (+CRC) to frame length embedded in the data itself.		
        if ( CheckBufferLength(evt->feb_info[5]+2, info_length) ) {
          std::cout << "Buffer length error for the Disciminators!" << std::endl;
          eventbuilder.fatalStream() << "Buffer length error for the Discriminators!";
          exit(EXIT_FEB_UNSPECIFIED_ERROR);
        }
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
        // Compare DPM Pointer Value (+CRC) to frame length embedded in the data itself.		
        if ( CheckBufferLength(evt->feb_info[5]+2, info_length) ) {
          std::cout << "Buffer length error for the FPGA's!" << std::endl;
          eventbuilder.fatalStream() << "Buffer length error for the FPGA's!";
          exit(EXIT_FEB_UNSPECIFIED_ERROR);
        }
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
        eventbuilder.critStream() << "Error in event_builder::main()!";
        eventbuilder.critStream() << "Received a DAQ event bank on a current event!";
        return (-1);
      case 4:
        std::cout << "Error in event_builder::main()!" << std::endl;
        std::cout << "TriP Programming Frames not supported yet!" << std::endl;
        eventbuilder.critStream() << "Error in event_builder::main()!";
        eventbuilder.critStream() << "TriP Programming Frames not supported yet!";
        return (-1);
      default:
        std::cout << "Error in event_builder::main()!" << std::endl;
        std::cout << "Failed Event Bank!" << std::endl;
        eventbuilder.critStream() << "Error in event_builder::main()!";
        eventbuilder.critStream() << "Failed Event Bank!";
        return (-1);
    }
  }

#if DEBUG_REPORT_EVENT
  eventbuilder.debugStream() << "Completed event_builder::main()! Processed Event Data!";
#endif
  // Clean up memory.
  delete dummy_feb;
  delete tmp_header;

  return 0;
}  


void HandleErrors(int success) 
{ 
  try  {
    if (success<0) throw (success);
  } catch (int e) {
    perror("server read");
    eventbuilder.fatal("server read error in HandleErrors");
    exit(EXIT_UNSPECIFIED_ERROR);
  }
} 


int CheckBufferLength(int length, int frame_length) 
{
  if (length != frame_length) {
    std::cout << "Buffer length, frame length disparity in event_builder::CheckBufferLength!" << endl;
    eventbuilder.critStream() << "Buffer length, frame length disparity in event_builder::CheckBufferLength!";
    return 1;
  }
  return 0;
}


template <class X> MinervaHeader* BuildBankHeader(event_handler *evt, X *frame)
{
  int feb_number = frame->GetFEBNumber(); //get the feb number from which this frame came
  int length     = evt->event_data[0] + (evt->event_data[1]<<8) + 2; // Data + CRC

  //now we've got everything we need to make up the event headers
  MinervaHeader *tmp_header; //declare a new data bank header
  if (evt->feb_info[4]==3) {
    std::cout << "Should not have passed DAQ block to BuildBlockHeader!" << std::endl;
    eventbuilder.fatalStream() << "Should not have passed DAQ block to BuildBlockHeader!";
    exit (-1);
  } else {
#if DEBUG_BANKHEADER
    eventbuilder.debugStream() << "  ----------BuildBankHeader----------";
    eventbuilder.debugStream() << "  crateID                       : " << evt->feb_info[1];
    eventbuilder.debugStream() << "  crocID                        : " << evt->feb_info[2];
    eventbuilder.debugStream() << "  chanID                        : " << evt->feb_info[3];
    eventbuilder.debugStream() << "  bank                          : " << evt->feb_info[4];
    eventbuilder.debugStream() << "  feb_number (from frame header): " << feb_number;
    eventbuilder.debugStream() << "  feb_number (from feb_info)    : " << evt->feb_info[6];
    eventbuilder.debugStream() << "  firmware                      : " << evt->feb_info[7];
    eventbuilder.debugStream() << "  hit                           : " << evt->feb_info[8];
    eventbuilder.debugStream() << "  length                        : " << length;
#endif          
    tmp_header = new MinervaHeader(evt->feb_info[1], evt->feb_info[2], evt->feb_info[3],
        evt->feb_info[4], feb_number, evt->feb_info[7],
        evt->feb_info[8], length); // Compose a regular data block header.
  }
  return tmp_header; //return the header
};


template <class X> void DecodeBuffer(event_handler *evt, X *frame, int i, int length)
{
#if DEBUG_DECODEBUFFER
  eventbuilder.debugStream() << "  DecodeBuffer Parameters: ";
  eventbuilder.debugStream() << "   byte offset: " << i;
  eventbuilder.debugStream() << "   msg length:  " << length;
#endif
  frame->message = new unsigned char [length];
  for (int j = 0; j < length;j ++) {
    frame->message[j] = 0;
  }
  for (int j = 0; j < length; j++) {
#if DEBUG_DECODEBUFFER
    eventbuilder.debugStream() << "    byte: " << j+i;
#endif
    unsigned char tmp = evt->event_data[(j+i)];
    frame->message[j]=tmp; //copy to a local buffer for processing
#if DEBUG_DECODEBUFFER
    eventbuilder.debugStream() << "    frame->message: " << (int)frame->message[j];
    eventbuilder.debugStream() << "              data? " << (int)tmp;
#endif
  }
#if DEBUG_DECODEBUFFER
  eventbuilder.debugStream() << "    Loaded Message";
#endif
  frame->CheckForErrors(); //check for header errors
#if DEBUG_DECODEBUFFER
  eventbuilder.debugStream() << "    Checked for Errors, going to DecodeHeader";
#endif
  frame->DecodeHeader(); //find feb number in header
#if DEBUG_DECODEBUFFER
  eventbuilder.debugStream() << "  Done Decoding the Buffer";
#endif
};
*/

void quitsignal_handler(int signum)
{
  // the use of STDERR is a bit "dangerous" in the sense that we might be inserting
  // this message into the middle of stuff in the STDERR buffer.  the worst that
  // can happen is that another message is broken in half with our message in the middle:
  // hence the flushes and the extra line breaks for readability.
  if (waiting_to_quit)
  {
    fflush(stderr);
    fprintf(stderr, "\n\nShutdown request acknowledged.  Will close down as soon as possible.\n\n");
    fflush(stderr);

    quit_now = true;
  }
  else
  {
    fflush(stderr);
    fprintf(stderr, "\n\nInstructed to close.\nNote that any events remaining in the buffer will first be cleared, and then we will wait 60 seconds to be sure there are no more.\nIf you really MUST close down NOW, issue the signal again (ctrl-C or 'kill <this process's PID>').\n\n");
    fflush(stderr);

    waiting_to_quit = true;

    // be sure to re-enable the signal!
    // (it's blocked by default when the handler is called)
    signal (signum, quitsignal_handler);
  }
}
#endif
