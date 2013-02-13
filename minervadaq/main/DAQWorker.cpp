#ifndef DAQWorker_cxx
#define DAQWorker_cxx

#include "DAQWorker.h"

log4cpp::Category& daqLogger = 
  log4cpp::Category::getInstance(std::string("daqLogger"));

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
  daqLogger.infoStream() << "  LED Level (encoded)    = " << args->ledLevel;
  daqLogger.infoStream() << "  LED Group (encoded)    = " << args->ledGroup;
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


DAQWorker::~DAQWorker()
{
  for (std::vector<ReadoutWorker*>::iterator p = readoutWorkerVect.begin();
      p != readoutWorkerVect.end();
      ++p ) {
    delete *p;
  }
  readoutWorkerVect.clear();
}

// void DAQWorker::SetUpET()  

/*
void DAQWorker::TakeData()
{
  // loop over gates
  readoutWorker->Reset();
  readoutWorker->Trigger();
  do {
    unsigned short dataBlockSize = readoutWorker->GetNextDataBlockSize();
    unsigned char* dataBlock     = readoutWorker->GetNextDataBlock( dataBlock );
    // declare block to ET
    // delete dataBlock;  // newed way down inside Channels object
  } while ( readoutWorker->MoveToNextChannel() );
}
*/

#endif
