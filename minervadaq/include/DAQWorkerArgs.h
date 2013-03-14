#ifndef DAQWorkerArgs_h
#define DAQWorkerArgs_h

#include "ReadoutTypes.h"

struct DAQWorkerArgs {

  int runNumber;
  int subRunNumber;
  int numberOfGates;
	Modes::RunningModes runMode;
	Detectors::DetectorTypes detector;
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

#endif
