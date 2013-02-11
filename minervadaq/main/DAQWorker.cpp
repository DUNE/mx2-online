#ifndef DAQWorker_cxx
#define DAQWorker_cxx

#include "DAQWorker.h"

log4cpp::Category& daqLogger = 
  log4cpp::Category::getInstance(std::string("daqLogger"));

DAQWorker::DAQWorker( const DAQWorkerArgs* theArgs, 
    log4cpp::Appender* theAppender, log4cpp::Priority::Value priority ) :
  args(theArgs),
  appender(theAppender)
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
    new ReadoutWorker( 0, appender, priority, (bool)args->hardwareInitLevel );
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


#endif
