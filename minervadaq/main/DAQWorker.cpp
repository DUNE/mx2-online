#ifndef DAQWorker_cxx
#define DAQWorker_cxx

#include <fstream>

#include "et.h"         // the event transfer stuff
#include "et_private.h" // event transfer private data types
#include "et_data.h"    // data structures 

#include "DAQWorker.h"

#include "exit_codes.h"

log4cpp::Category& daqLogger = 
  log4cpp::Category::getInstance(std::string("daqLogger"));

//---------------------------------------------------------
DAQWorker::DAQWorker( const DAQWorkerArgs* theArgs, 
    log4cpp::Priority::Value priority ) :
  args(theArgs)
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

  et_att_id      attach; 
  et_sys_id      sys_id; 
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
void DAQWorker::CloseDownET()
{
  daqLogger.infoStream() << "Closing down ET...";


}

//---------------------------------------------------------
void DAQWorker::TakeData()
{
  daqLogger.infoStream() << "Beginning Data Acquisition...";
  this->Initialize();

  for (int ngates = 0; ngates < args->numberOfGates; ++ngates) {
    if (!(ngates % 10)) daqLogger.infoStream() << "Taking data for gate " << ngates;

    for (ReadoutWorkerIt readoutWorker=readoutWorkerVect.begin(); 
        readoutWorker!=readoutWorkerVect.end();
        ++readoutWorker) {

      ReadoutWorker * worker = (*readoutWorker);

      worker->Reset();
      worker->Trigger();
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
    if (!WriteLastTrigger()) break;
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
bool DAQWorker::WriteLastTrigger()
{
  daqLogger.debugStream() << "Writing last trigger data to " << args->lastTriggerFileName;
  return true;
}

//---------------------------------------------------------
bool DAQWorker::DeclareDAQHeaderToET()
{
  daqLogger.debugStream() << "Declaring DAQ Header to ET...";

  unsigned long long ggate = this->GetGlobalGate();
  if (0 == ggate) return false;
  return PutGlobalGate(++ggate);
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
  /*! \fn void PutGlobalGate(unsigned long long ggate)
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
