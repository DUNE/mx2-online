#ifndef DAQWorker_h
#define DAQWorker_h

#include "log4cppHeaders.h"
#include "EventHandler.h"
#include "ReadoutWorker.h"
#include "et.h"          // the event transfer stuff
#include "et_private.h"  // event transfer private data types
#include "et_data.h"     // data structures 

/* #include <cstddef> */
/* #include <cstdlib> */
/* #include <assert.h> */

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
    const bool *const status;

    std::vector<ReadoutWorker*> readoutWorkerVect;

    et_att_id      attach; 
    et_sys_id      sys_id; 
    bool ContactEventBuilder(EventHandler *handler);

    void Initialize();  
    bool WriteToSAMFile();
    bool WriteLastTrigger();
    bool WriteLastTrigger(int triggerNum, int triggerType, unsigned long long triggerTime);
    bool DeclareDAQHeaderToET(int triggerNum, int triggerType, 
        unsigned long long triggerTime);

    unsigned long long GetGlobalGate();
    bool PutGlobalGate( unsigned long long globalGate );

    // The CROC-E DAQ receives "globs" of data spanning entire chains.
    template <class X> struct EventHandler * CreateEventHandler( X *dataBlock );
    void DestroyEventHandler( struct EventHandler * handler );


  public:
    explicit DAQWorker( const DAQWorkerArgs* theArgs, 
        log4cpp::Priority::Value priority, bool *status );
    ~DAQWorker();

    int SetUpET();  
    void TakeData();
    bool CloseDownET();
    bool SendSentinel();

};


#endif
