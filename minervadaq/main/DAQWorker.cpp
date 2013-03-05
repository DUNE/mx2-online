#ifndef DAQWorker_cxx
#define DAQWorker_cxx

#include <fstream>

#include "EventHandler.h"
#include "DAQHeader.h"
#include "DAQWorker.h"

#include "exit_codes.h"

log4cpp::Category& daqLogger = 
log4cpp::Category::getInstance(std::string("daqLogger"));

//---------------------------------------------------------
DAQWorker::DAQWorker( const DAQWorkerArgs* theArgs, 
    log4cpp::Priority::Value priority,
    bool *theStatus ) :
  args(theArgs),
  status(theStatus)
{
  daqLogger.setPriority(priority);

  daqLogger.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
  daqLogger.infoStream() << "Arguments to MINERvA DAQ Worker: ";
  daqLogger.infoStream() << "  Run Number             = " << args->runNumber;
  daqLogger.infoStream() << "  Subrun Number          = " << args->subRunNumber;
  daqLogger.infoStream() << "  Total Gates            = " << args->numberOfGates;
  daqLogger.infoStream() << "  Running Mode (encoded) = " << args->runMode;
  daqLogger.infoStream() << "  Detector (encoded)     = " << args->detector;
  daqLogger.infoStream() << "  DetectorConfiguration  = " << args->detectorConfigCode;
  daqLogger.infoStream() << "  LED Level (encoded)    = " << (int)args->ledLevel;
  daqLogger.infoStream() << "  LED Group (encoded)    = " << (int)args->ledGroup;
  daqLogger.infoStream() << "  ET Filename            = " << args->etFileName;
  daqLogger.infoStream() << "  SAM Filename           = " << args->samFileName;
  daqLogger.infoStream() << "  LOG Filename           = " << args->logFileName;
  daqLogger.infoStream() << "  Configuration File     = " << args->hardwareConfigFileName;
  daqLogger.infoStream() << "  VME Card Init. Level   = " << args->hardwareInitLevel;	
  daqLogger.infoStream() << "  ET System Port         = " << args->networkPort;	
  daqLogger.infoStream() << "See Event/MinervaEvent/xml/DAQHeader.xml for codes.";
  daqLogger.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";

  ReadoutWorker* readoutWorker = 
    new ReadoutWorker( 0, priority, (bool)args->hardwareInitLevel );
  readoutWorkerVect.push_back( readoutWorker );

  stateRecorder = new ReadoutStateRecorder( args, priority );
}

//---------------------------------------------------------
DAQWorker::~DAQWorker()
{
  for (std::vector<ReadoutWorker*>::iterator p = readoutWorkerVect.begin();
      p != readoutWorkerVect.end();
      ++p ) {
    delete *p;
  }
  readoutWorkerVect.clear();
  delete stateRecorder;
}

//---------------------------------------------------------
void DAQWorker::Initialize()
{
  daqLogger.infoStream() << "Initializing DAQWorker...";

  // Read in hardware config here. For now, hard code...

  readoutWorkerVect[0]->AddECROC( 2, 0, 5, 0, 0 );
  readoutWorkerVect[0]->AddCRIM( 224 );
  readoutWorkerVect[0]->InitializeCrate( args->runMode );
}

//---------------------------------------------------------
int DAQWorker::SetUpET()  
{
  daqLogger.infoStream() << "Setting up ET...";

  et_openconfig  openconfig;

  // Configuring the ET system is the first thing we must do.
  et_open_config_init(&openconfig);

  // Set the remote host. We operate the DAQ exclusively 
  // in "remote" mode even when running on only one PC.
  et_open_config_setmode(openconfig, ET_HOST_AS_REMOTE);  

  // Set to the host machine name. 
  et_open_config_sethost(openconfig, (args->hostName).c_str());
  daqLogger.infoStream() << "Setting ET host to " << args->hostName;

  // Set direct connection.
  et_open_config_setcast(openconfig, ET_DIRECT);  // Remote mode only.

  // Set the server port.
  et_open_config_setserverport(openconfig, args->networkPort); // Remote mode only.
  daqLogger.infoStream() << "Set ET server port to " << args->networkPort; 

  // Open it.
  daqLogger.infoStream() << "Trying to open ET system...";   
  if (et_open(&sys_id, (args->etFileName).c_str(), openconfig) != ET_OK) {
    daqLogger.fatalStream() << "et_producer: et_open problems!";
    return EXIT_UNSPECIFIED_ERROR;
  }
  daqLogger.infoStream() << "...Opened ET system!";  

  // Clean up.
  et_open_config_destroy(openconfig);

  // Set the debug level for output (everything).
  et_system_setdebug(sys_id, ET_DEBUG_INFO);

  // Attach to GRANDCENTRAL station since we are producing events.
  int etattstat = et_station_attach(sys_id, ET_GRANDCENTRAL, &attach); 
  if (etattstat < 0) {
    daqLogger.fatalStream() << "et_producer: error in station attach!";
    daqLogger.fatalStream() << " error code = " << etattstat;
    return etattstat;
  } 
  daqLogger.infoStream() << "Successfully attached to GRANDCENTRAL Station.";        

  return 0;
}

//---------------------------------------------------------
bool DAQWorker::ContactEventBuilder( EventHandler *handler )
{
  daqLogger.infoStream() << "Contacting Event Builder...";

  unsigned short length = handler->dataLength;

  while (et_alive(sys_id)) {
    daqLogger.debugStream() << "  ->ET is Alive!";
    et_event *pe;         // The event.
    EventHandler *pdata;  // The data for the event.
    int status = et_event_new(sys_id, attach, &pe, ET_SLEEP, NULL,
        sizeof(struct EventHandler)); // Get an event.
    if (status == ET_ERROR_DEAD) {
      daqLogger.crit("ET system is dead in acquire_data::ContactEventBuilder!");
      break;
    } else if (status == ET_ERROR_TIMEOUT) {
      daqLogger.crit("Got an ET timeout in acquire_data::ContactEventBuilder!");
      break;
    } else if (status == ET_ERROR_EMPTY) {
      daqLogger.crit("No ET events in acquire_data::ContactEventBuilder!");
      break;
    } else if (status == ET_ERROR_BUSY) {
      daqLogger.crit("ET Grandcentral is busy in acquire_data::ContactEventBuilder!");
      break;
    } else if (status == ET_ERROR_WAKEUP) {
      daqLogger.crit("ET wakeup error in acquire_data::ContactEventBuilder!");
      break;
    } else if ((status == ET_ERROR_WRITE) || (status == ET_ERROR_READ)) {
      daqLogger.crit("ET socket communication error in acquire_data::ContactEventBuilder!");
      break;
    } if (status != ET_OK) {
      daqLogger.fatal("ET et_producer: error in et_event_new in acquire_data::ContactEventBuilder!");
      return false;
    }
    // Put data into the event.
    if (status == ET_OK) {
      daqLogger.debugStream() << "Putting Event into ET System...";
      et_event_getdata(pe, (void **)&pdata); // Get the event ready.
      { 
        daqLogger.debugStream() << "-----------------------------------------------";
        daqLogger.debugStream() << "EventHandler_size: " << sizeof(struct EventHandler);
        daqLogger.debugStream() << "evt_size:          " << sizeof(handler);
        daqLogger.debugStream() << "Finished Processing Event Data:";
        for (int index = 0; index < length; index++) {
          daqLogger.debug("     Data Byte %02d = 0x%02X",
              index,(unsigned int)handler->data[index]);
        }
      }
      // TODO : memmove?
      // Also TODO : statically sized EventHandler is typically far too big. Dynamic?
      memcpy(pdata, handler, sizeof(struct EventHandler));
      et_event_setlength(pe, sizeof(struct EventHandler));
    } 

    // Put the event back into the ET system.
    status = et_event_put(sys_id, attach, pe); // Put the event away.
    if (status != ET_OK) {
      daqLogger.fatal("et_producer: put error in acquire_data::ContactEventBuilder!");
      return false;
    }
    if (!et_alive(sys_id)) {
      et_wait_for_alive(sys_id);
    }
    break; // Done processing the event. 
  } // while alive 

  daqLogger.debugStream() << "  Exiting acquire_data::ContactEventBuilder...";
  return true;
}

//---------------------------------------------------------
bool DAQWorker::CloseDownET()
{
  daqLogger.infoStream() << "Closing down ET...";

  if (et_station_detach(sys_id, attach) < 0) {
    daqLogger.fatal("et_producer: error in station detach\n");
    return false;
  }     

  return true;
}

//---------------------------------------------------------
void DAQWorker::TakeData()
{
  daqLogger.infoStream() << "Beginning Data Acquisition...";
  this->Initialize();

  while (stateRecorder->BeginNextGate()) {
    daqLogger.debugStream() << "Continue Running Status = " << (*status);
    if (!(*status)) break;

    unsigned long long triggerTime = 0;

    for (ReadoutWorkerIt readoutWorker=readoutWorkerVect.begin(); 
        readoutWorker!=readoutWorkerVect.end();
        ++readoutWorker) {

      ReadoutWorker * worker = (*readoutWorker);

      worker->Reset();
      triggerTime = worker->Trigger();
      do {
        unsigned short blockSize = worker->GetNextDataBlockSize();
        std::tr1::shared_ptr<SequencerReadoutBlock> block = worker->GetNextDataBlock( blockSize );
        // declare block to ET here
        // temp : turn the data into Frames just to look at in the log file:
        block->ProcessDataIntoFrames();
        daqLogger.debugStream() << "TakeData : Inspecting Frames for channel " << (*worker->CurrentChannel());
        while (block->FrameCount()) {
          LVDSFrame * frame = block->PopOffFrame();
          daqLogger.debugStream() << (*frame);
          frame->printReceivedMessageToLog();
          delete frame;
        }
      } while ( worker->MoveToNextChannel() );
    }

    stateRecorder->FinishGate();
    DeclareDAQHeaderToET();
  }

  daqLogger.infoStream() << "Finished Data Acquisition...";
}


//---------------------------------------------------------
void DAQWorker::DeclareDAQHeaderToET( HeaderData::BankType bankType )
{
  daqLogger.debugStream() << "Declaring Header to ET for bank type " << bankType;

  struct EventHandler * handler = NULL;
  std::tr1::shared_ptr<DAQHeader> daqhead = stateRecorder->GetDAQHeader( bankType );
  handler = CreateEventHandler<DAQHeader>( daqhead.get() );
  ContactEventBuilder( handler );
  DestroyEventHandler( handler );
}

//---------------------------------------------------------
void DAQWorker::SendSentinel()
{
  daqLogger.debugStream() << "Sending Sentinel Frame...";
  this->DeclareDAQHeaderToET( HeaderData::SentinelBank );
}


template <class X> struct EventHandler * DAQWorker::CreateEventHandler( X *dataBlock )
{
  struct EventHandler * handler = (struct EventHandler *)malloc( sizeof(struct EventHandler) );
  assert( NULL != handler );

  handler->dataLength = dataBlock->GetDataLength();
  // If data ever becomes dynamic, we need to new it here.
  memcpy( handler->data, dataBlock->GetData(), handler->dataLength ); // dest, src, length
  
  return handler;
}

void DAQWorker::DestroyEventHandler( struct EventHandler * handler )
{
  assert( NULL != handler );
  // If data ever becomes dynamic, we need to free it here.
  free( handler );
}


#endif
