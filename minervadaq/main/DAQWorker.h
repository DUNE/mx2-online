#ifndef DAQWorker_h
#define DAQWorker_h

#include <string>
#include "log4cppHeaders.h"
#include "ReadoutWorker.h"

struct DAQWorkerArgs {

  int runNumber;
  int subRunNumber;
  int numberOfGates;
  int runMode;
  int detector;
  int detectorConfigCode;
  int ledLevel;
  int ledGroup;
  int hardwareInitLevel;
  int networkPort;
  std::string etFileName;
  std::string logFileName;
  std::string samFileName;
  std::string hardwareConfigFileName;

};

log4cpp::Category& daqLogger = 
  log4cpp::Category::getInstance(std::string("daqLogger"));

class DAQWorker {
  private:  
    const DAQWorkerArgs* args;
    log4cpp::Appender* daqAppender;

    std::vector<ReadoutWorker*> readoutWorkerVect;

  public:
    explicit DAQWorker( const DAQWorkerArgs* daqArgs, 
        log4cpp::Appender* appender, log4cpp::Priority::Value priority );
    ~DAQWorker();

};


#endif
