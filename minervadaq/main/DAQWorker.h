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
  std::string hostName;
  std::string lastTriggerFileName;
  std::string globalGateLogFileName;

};


class DAQWorker {

  typedef std::vector<ReadoutWorker*> ReadoutWorkerVect;
  typedef std::vector<ReadoutWorker*>::iterator ReadoutWorkerIt;

  private:  
    const DAQWorkerArgs* args;

    std::vector<ReadoutWorker*> readoutWorkerVect;

    void Initialize();  // Prep VME hardware - add CROCs and CRIMs, Init Crate

    bool WriteToSAMFile();
    bool WriteLastTrigger();
    bool DeclareDAQHeaderToET();

    unsigned long long GetGlobalGate();
    bool PutGlobalGate( unsigned long long globalGate );

  public:
    explicit DAQWorker( const DAQWorkerArgs* theArgs, 
        log4cpp::Priority::Value priority );
    ~DAQWorker();

    int SetUpET();  
    void TakeData();
    void CloseDownET();

};


#endif
