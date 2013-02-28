#ifndef DAQWorker_cxx
#define DAQWorker_cxx

#include <fstream>

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
  if (et_station_attach(sys_id, ET_GRANDCENTRAL, &attach) < 0) {
    daqLogger.fatalStream() << "et_producer: error in station attach!";
    return EXIT_UNSPECIFIED_ERROR;
  } 
  daqLogger.infoStream() << "Successfully attached to GRANDCENTRAL Station.";        

  return 0;
}

//---------------------------------------------------------
void DAQWorker::ContactEventBuilder()
{
  daqLogger.infoStream() << "Contacting Event Builder...";

}

//---------------------------------------------------------
bool DAQWorker::CloseDownET()
{
  daqLogger.infoStream() << "Closing down ET...";

  // Detach from the station.
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

  for (int ngates = 0; ngates < args->numberOfGates; ++ngates) {
    daqLogger.debugStream() << "Continue Running Status = " << (*status);
    if (!(*status)) break;
    if (!(ngates % 10)) daqLogger.infoStream() << "Taking data for gate " << ngates;

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

    if (!WriteToSAMFile()) break;
    if (!WriteLastTrigger(ngates, 0/*trigtype*/, triggerTime)) break;
    if (!DeclareDAQHeaderToET()) break;
  }

  daqLogger.infoStream() << "Finished Data Acquisition...";
}

//---------------------------------------------------------
bool DAQWorker::WriteToSAMFile()
{
  daqLogger.debugStream() << "Writing SAM File...";
  unsigned long long ggate = this->GetGlobalGate();
  if (0 == ggate) return false;
  return true;
}

//---------------------------------------------------------
bool DAQWorker::WriteLastTrigger(int triggerNum, int triggerType, 
    unsigned long long triggerTime)
{
  daqLogger.debugStream() << "Writing last trigger data to " 
    << args->lastTriggerFileName;

  FILE *file;

  if ( NULL == (file=fopen((args->lastTriggerFileName).c_str(),"w")) ) {
    daqLogger.errorStream() << "Error opening last trigger file for writing!";
    return false;
  }
  else {
    if (!(triggerNum%10)) {
      daqLogger.infoStream() << "Writing info for trigger " << triggerNum 
        << " to file " << args->lastTriggerFileName;
    } else {
      daqLogger.debugStream() << "Writing info for trigger " << triggerNum 
        << " to file " << args->lastTriggerFileName;
    }
  }

  fprintf(file, "run=%d\n",      args->runNumber);
  fprintf(file, "subrun=%d\n",   args->subRunNumber);
  fprintf(file, "number=%d\n",   triggerNum);
  fprintf(file, "type=%d\n",     triggerType);
  fprintf(file, "time=%llu\n",   triggerTime);

  fclose(file);
  return true;
}

//---------------------------------------------------------
bool DAQWorker::DeclareDAQHeaderToET()
{
  daqLogger.debugStream() << "Declaring DAQ Header to ET...";

  /* DAQHeader(unsigned char det, unsigned short int config, int run, int sub_run, */
  /*     unsigned short int trig, unsigned char ledGroup, unsigned char ledLevel, */
  /*     unsigned long long g_gate, unsigned int gate, unsigned long long trig_time, */
  /*     unsigned short int error, unsigned int minos, unsigned int read_time, */
  /*     FrameHeader *header,  unsigned short int nADCFrames, unsigned short int nDiscFrames, */
  /*     unsigned short int nFPGAFrames); */

  // TODO: Magic numbers must die = make a file for bank encodings (3==DAQ,5==Sent)
  FrameHeader * frameHeader = new FrameHeader(0,0,0,3,0,0,0,daqHeaderSize);
  // DAQHeader * daqhead = new DAQHeader();
  // ContactEventBuilder

  // then, clean up the frame header and DAQ header...

  unsigned long long ggate = this->GetGlobalGate();
  if (0 == ggate) return false;
  return PutGlobalGate(++ggate);
}

//---------------------------------------------------------
bool DAQWorker::SendSentinel()
{
  daqLogger.debugStream() << "Sending Sentinel Frame...";

  // TODO: Magic numbers must die = make a file for bank encodings (3==DAQ,5==Sent)
  FrameHeader * frameHeader = new FrameHeader(0,0,0,5,0,0,0,daqHeaderSize);
  // DAQHeader * sentinel = new DAQHeader( frameHeader );
  // ContactEventBuilder
  
  // then, clean up the frame header and DAQ header...

  return true;
}


//---------------------------------------------------------
unsigned long long DAQWorker::GetGlobalGate()
{
  /*! \fn unsigned long long GetGlobalGate()
   *
   * This function gets the value of the global gate from the data file used for tracking.  
   */
  unsigned long long ggate = 0;
  std::fstream global_gate((args->globalGateLogFileName).c_str());
  try {
    if (!global_gate) throw (!global_gate);
    global_gate >> ggate;
  } 
  catch (bool e) {
    daqLogger.errorStream() << "Error opening global gate data!";
  }
  global_gate.close();
  daqLogger.debugStream() << "Got global gate " << ggate;
  return ggate;
}

//---------------------------------------------------------
bool DAQWorker::PutGlobalGate(unsigned long long ggate)
{
  /*! \fn bool PutGlobalGate(unsigned long long ggate)
   *
   * This funciton writes a new value into the global gate data log.
   */
  std::fstream global_gate((args->globalGateLogFileName).c_str());
  try {
    if (!global_gate) throw (!global_gate);
    global_gate << ggate;
  } 
  catch (bool e) {
    daqLogger.errorStream() << "Error opening global gate data!";
    return false;
  }
  global_gate.close();
  daqLogger.debugStream() << "Put global gate " << ggate;
  return true;
}

#endif
