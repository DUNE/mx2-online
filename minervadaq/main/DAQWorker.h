#ifndef DAQWorker_h
#define DAQWorker_h

#include <string>
#include "log4cppHeaders.h"
#include "ReadoutWorker.h"

struct DAQWorkerArgs {

  int runNumber;
  int subRunNumber;
  int numberOfGates;
  RunningModes runMode;
  DetectorTypes detector;
  int detectorConfigCode;
  unsigned char ledLevel;
  unsigned char ledGroup;
  int hardwareInitLevel;
  int networkPort;
  std::string etFileName;
  std::string logFileName;
  std::string samFileName;
  std::string dataFileName;
  std::string hardwareConfigFileName;

};


class DAQWorker {
  private:  
    const DAQWorkerArgs* args;
    log4cpp::Appender* appender;

    std::vector<ReadoutWorker*> readoutWorkerVect;

    // void Initialize();  // Prep VME hardware - add CROCs and CRIMs, Init Crate

    // bool EstablishETHeartBeat();

    /* unsigned long long GetGlobalGate(); */
    /* void PutGlobalGate( unsigned long long globalGate ); */

    // bool Trigger(); // set trigger type for header?, reset sequencer latch?, rearm interrupt stuff?

  public:
    explicit DAQWorker( const DAQWorkerArgs* theArgs, 
        log4cpp::Appender* theAppender, log4cpp::Priority::Value priority );
    ~DAQWorker();

    // void SetUpET();  // ?
    // void TakeData();

};


#endif
