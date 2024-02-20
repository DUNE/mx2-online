#ifndef ReadoutStateRecorder_h
#define ReadoutStateRecorder_h
/*! \file ReadoutStateRecorder.h
*/

#include "log4cppHeaders.h"

#include "DAQWorkerArgs.h"
#include "DAQWorkerUtils.h"
#include "DAQHeader.h"

#include <fstream>
#include <string>
#include <sstream>
#include <tr1/memory>  // for shared_ptrs

/*! 
  \class ReadoutStateRecorder
  \brief Track gate info, calculate trigger types, and write gate logs 
  (SAM files, etc.).
  \author Gabriel Perdue
  */
class ReadoutStateRecorder {

  friend std::ostream& operator<<(std::ostream&, const ReadoutStateRecorder&);

  private: 

  int gate;
  Triggers::TriggerType triggerType;
  unsigned long long firstGate;
  unsigned long long globalGate;
  unsigned long long gateStartTime;
  unsigned long long gateFinishTime;
  unsigned long long subRunStartTime;
  unsigned long long subRunFinishTime;
  unsigned int MINOSSGATE;

  const DAQWorkerArgs* args;
  DAQWorkerUtils* daqUtils;
 
  void GetGlobalGateFromFile();
  void IncrememntGlobalGate();
  void WriteGlobalGateToFile();

  void WriteToSAMPYFile();
  void WriteToSAMJSONFile();
  void WriteLastTriggerDataToFile();
  void WriteLastTriggerDataToFileMTest();

  static const int DAQHeaderVersion;

  public:

  explicit ReadoutStateRecorder( const DAQWorkerArgs* theArgs, 
      log4cpp::Priority::Value priority ); 
  ~ReadoutStateRecorder();

  unsigned long long GetFirstGate() const;
  unsigned long long GetGlobalGate() const;
  unsigned long long GetSubRunStartTime() const;
  unsigned long long GetSubRunFinishTime() const;

  bool BeginNextGate();
  bool FinishGate();
  bool MoreGates();

  Triggers::TriggerType GetNextTriggerType(); // Get and set...
  Modes::RunningModes GetRunMode() const;

  void SetMINOSSGATE( unsigned int gateTime );
  void SetGateStartTime( unsigned long long theStartTime );
  void SetGateFinishTime( unsigned long long theFinishTime );

  std::tr1::shared_ptr<DAQHeader> GetDAQHeader( HeaderData::BankType bankType );

};

#endif
