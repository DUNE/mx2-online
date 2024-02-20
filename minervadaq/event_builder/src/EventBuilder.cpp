#ifndef EventBuilder_cxx
#define EventBuilder_cxx
/*! \file EventBuilder.cpp
*/

#include "log4cppHeaders.h"
#include "EventBuilder.h"
#include "exit_codes.h"
#include <ctime>
#include <sys/time.h>
#include <signal.h>
#include <errno.h>
#include <libgen.h>

using namespace std;

// How long the event builder will wait for new frames before declaring no more are coming.
// Only relevant after receiving SIGTERM/SIGINT (otherwise we just wait until we get the
// sentinel gate instead).
const int SECONDS_BEFORE_TIMEOUT = 60; 

DAQHeader *daqHeader;

sig_atomic_t waiting_to_quit;  
sig_atomic_t quit_now;        
void quitsignal_handler(int signum);

// log4cpp Variables - Needed throughout the EventBuilder functions.
log4cpp::Appender* eventBuilderAppender;
log4cpp::Category& rootCategory = log4cpp::Category::getRoot();
log4cpp::Category& eventbuilder = log4cpp::Category::getInstance(std::string("eventbuilder"));

/*!
  \brief Run an ET station that logs events to disk and passes them on to monitoring nodes.
  \author Gabriel Perdue
  \author Elaine Schulte
  \author Jeremy Wolcott
  */
int main(int argc, char *argv[]) 
{
  if (argc < 3) {
    printf("Usage: EventBuilder <et_filename> <rawdata_filename> <network port (default 1201)> <callback PID (default: no PID)>\n");
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

  char log_filename[300]; 
  // TODO: Setup precompiler options for logs on Nearline, other machines, and timestamping.
  #ifdef NEARLINE
  sprintf(log_filename, "/scratch/nearonline/var/logs/EventBuilderLog_%s.txt", basename(argv[1])); 
  #else
  sprintf(log_filename, "/work/data/logs/EventBuilderLog.txt"); 
  #endif
 
  std::cout << "Writing log file to: " << log_filename << std::endl;
 
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
  #ifdef NEARLINE
  sprintf(hostName, "mnvonline1.fnal.gov");
  #else  
  sprintf(hostName, "localhost");
  #endif
  eventbuilder.infoStream() << "Configured for a Single-PC Build..."; 
  eventbuilder.infoStream() << "ET system host machine = " << hostName;

  // Set up the signal handler so we can always exit cleanly
  struct sigaction quit_action;
  quit_action.sa_handler = quitsignal_handler;
  sigemptyset (&quit_action.sa_mask);
  quit_action.sa_flags = SA_RESTART;		// restart interrupted system calls instead of failing with EINTR

  // We will use custom singnal handlers to interact with the Run Control.
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
    printf("EventBuilder::main(): et_producer: et_open problems\n");
    eventbuilder.fatal("EventBuilder::main(): et_producer: et_open problems\n");
    exit(EXIT_ETSTARTUP_ERROR);
  }
  et_open_config_destroy(openconfig);

  // Check if ET is up and running.
  // Nearline nodes will attach to an existing system instead.
#if !NEARLINE
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
    eventbuilder.infoStream() << "  Synching heartbeat...";
    system("sleep 5s"); 
    if (!counter) {
      newheartbeat = id->sys->heartbeat;
    } else {
      oldheartbeat = newheartbeat;
      newheartbeat = id->sys->heartbeat;
    }
    counter++;  
  } while ((newheartbeat==oldheartbeat)&&(counter!=60));
  if (counter==60) {
    eventbuilder.fatalStream() << "Error in EventBuilder::main()!";
    eventbuilder.fatalStream() << "ET System did not start properly!  Exiting...";
    exit(EXIT_ETSTARTUP_ERROR);
  } 
#else
  // prevents compiler warnings.
  id = NULL;
#endif

  // Set the level of debug output that we want (everything).
  et_system_setdebug(sys_id, ET_DEBUG_INFO);

  // Create & attach to a new station for making the final output file.
#if NEARLINE
  et_station_create(sys_id,&cu_station,"RIODEJANEIRO",sconfig);
  eventbuilder.infoStream() << "Creating new station RIODEJANEIRO for output...";
#else
  et_station_create(sys_id,&cu_station,"CHICAGO_UNION",sconfig);
  eventbuilder.infoStream() << "Creating new station CHICAGO_UNION for output...";
#endif
  if (et_station_attach(sys_id, cu_station, &attach) < 0) {
    eventbuilder.fatal("EventBuilder::main(): et_producer: error in station attach!");
    system("sleep 10s");
    exit(EXIT_ETSTARTUP_ERROR);
  }

  // send the SIGUSR1 signal to the specified process signalling that ET is ready
  eventbuilder.infoStream() << "Sending ready signal to ET system...";
  int failure = 0;
  if (callback_pid) {
    failure = kill(callback_pid, SIGUSR1);
    if (failure) {
      eventbuilder.warnStream() << "Signal was not delivered to parent process.  Errno: " << failure;
    }
  }

  // Request an event from the ET service.
  eventbuilder.infoStream() << " Starting!";
  int evt_counter = 0;
  bool continueRunning = true;
  while ((et_alive(sys_id)) && continueRunning) {
    struct timespec time;

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
    // a maximum of 60 seconds (customizable in EventBuilder.h) for new frames
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
//      #ifdef NEARLINE
//      nanosleep( &time, NULL );
//      #endif

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
      eventbuilder.warn("Socket error in EventBuilder::main() calling et_event_get().  Will retry.\n");
#else
      eventbuilder.fatal("EventBuilder::main(): et_client: socket communication error\n");
      continueRunning = false;
#endif
    }

    if (status == ET_ERROR_DEAD) {
      eventbuilder.fatal("EventBuilder::main(): et_client: ET system is dead\n");
      continueRunning = false;
    }
    else if (status == ET_ERROR_TIMEOUT) {
      eventbuilder.fatal("EventBuilder::main(): et_client: got timeout\n");
      continueRunning = false;
    }
    else if (status == ET_ERROR_WAKEUP) {
      eventbuilder.fatal("EventBuilder::main(): et_client: someone told me to wake up\n");
      continueRunning = false;
    }
    else if (status == ET_ERROR_EMPTY || status == ET_ERROR_BUSY) {
      continue;  // continue silently here.  (see note on et_event_get() call above.)
    }

    if (status != ET_OK) {
      eventbuilder.warnStream() << "Got status " << status << " when I asked for an ET event!";
      continue;
    }

    EventHandler *evt;
    int pri;
    size_t len;
    int con[ET_STATION_SELECT_INTS];

    et_event_getdata(pe, (void **) &evt);
    et_event_getpriority(pe, &pri);
    et_event_getlength(pe, &len);
    et_event_getcontrol(pe, con);

    void *pdata;
    et_event_getdata(pe, &pdata); 

    evt_counter++;
    eventbuilder.debugStream() << "Now write the event to the binary output file...";
    eventbuilder.debugStream() << " Writing " << evt->dataLength << " bytes...";
    binary_outputfile.write((char *) evt->data, evt->dataLength);  
    binary_outputfile.flush();

    if (HeaderData::SentinelBank == (HeaderData::BankType)evt->leadBankType())
        continueRunning = false;

    #ifndef NEARLINE
    // Geoff Savage 14Dec21 - Return event to ET after writing event to file..
    // for whatever reason, the nearline event builder gets
    // super confused if the nearline station is et_event_put()ing
    // the events back into the stream.  (it always et_event_get()s
    // events of exactly 1 null byte regardless of what the
    // DAQ's Grand Central station is putting into the stream.)
    // this doesn't solve the root cause, which I couldn't find,
    // but it appears to at least manage the symptoms.
    // make sure that the other event builder, the "Chicago Union" station,
    // DOES et_event_put() however (so don't delete this code -- just leave
    // it in the preprocessor exclusions), or the events will back up
    // and none of them will ever make to the "Rio de Janeiro" station.
    eventbuilder.debugStream() << "Put the event back into the ET system...";
    status = et_event_put(sys_id, attach, pe); 
    #endif
  }

  eventbuilder.infoStream() << "Exited data collection loop, detaching..."; /* Smedley */
  // Detach from the station.
  if (et_station_detach(sys_id, attach) < 0) {
    eventbuilder.fatal("et_producer: error in station detach\n");
    system("sleep 10s");
    exit(EXIT_ETSTARTUP_ERROR);
  }

  eventbuilder.infoStream() << "Closing ET..."; /* Smedley */
  // Close ET
  if (et_close(sys_id) < 0) {
    eventbuilder.fatal("et_producer: error in ET close\n");
    system("sleep 10s");
    exit(EXIT_ETSTARTUP_ERROR);
  }

  eventbuilder.infoStream() << "Closing output file..."; /* Smedley */
  binary_outputfile.close(); 

  eventbuilder.infoStream() << "Closing the Event Builder!";
  log4cpp::Category::shutdown();
  return 0; 
}

//---------------------------------------------------------------------
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
