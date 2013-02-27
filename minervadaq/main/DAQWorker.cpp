#ifndef DAQWorker_cxx
#define DAQWorker_cxx

#include "DAQWorker.h"

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
// void DAQWorker::SetUpET()  

//---------------------------------------------------------
void DAQWorker::TakeData()
{
  daqLogger.infoStream() << "Beginning Data Acquisition...";
  this->Initialize();

  // loop over gates
  for (ReadoutWorkerIt readoutWorker=readoutWorkerVect.begin(); 
      readoutWorker!=readoutWorkerVect.end();
      ++readoutWorker) {

    ReadoutWorker * worker = (*readoutWorker);

    worker->Reset();
    worker->Trigger();
    do {
      unsigned short blockSize = worker->GetNextDataBlockSize();
      std::tr1::shared_ptr<SequencerReadoutBlock> block = worker->GetNextDataBlock( blockSize );
      // declare block to ET
        block->ProcessDataIntoFrames();
        daqLogger.debugStream() << "TakeData : Inspecting Frames for channel " << worker->CurrentChannel();
        while (block->FrameCount()) {
          LVDSFrame * frame = block->PopOffFrame();
          daqLogger.debugStream() << (*frame);
          frame->printReceivedMessageToLog();
          delete frame;
        }
    } while ( worker->MoveToNextChannel() );

  }
}

#endif
