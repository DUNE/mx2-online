#ifndef DAQWorkerArgs_h
#define DAQWorkerArgs_h
/*! 
  \file DAQWorkerArgs.h
  \brief Define the DAQWorkerArgs struct - used to organzie command line flags.
  */

#include "ReadoutTypes.h"

/*! 
  \struct DAQWorkerArgs
  \brief Hold all the command line flags.
  \author Gabriel Perdue
  */
struct DAQWorkerArgs {

  int runNumber;      /*!< MINERvA Run Number */
  int subRunNumber;   /*!< MINERvA Subrun Number */
  int numberOfGates;  /*!< Target number of gates in the subrun. */
  Modes::RunningModes runMode;       /*!< Subrun strategy. */
  Detectors::DetectorTypes detector; /*!< Detector used to record data. */
  int detectorConfigCode;  /*!< The number of FEBs. */
  unsigned char ledLevel;  /*!< Zero, One, or Max PE */
  unsigned char ledGroup;  /*!< Which LED group is being used. */
  int hardwareInitLevel;   /*!< Should the DAQ configure VME module timing registers? */
  int networkPort;         /*!< Network port for communication with ET, DAQ nodes (just ET right now). */
  std::string etFileName;       /*!< ET system file name (memory mapped file) */
  std::string logFileName;      /*!< The DAQ log file. */
  std::string samPyFileName;    /*!< The SAM.py metadata file. */
  std::string samJSONFileName;  /*!< The SAM.JSON metadata file. */
  std::string dataFileName;     /*!< The RawData file. */
  std::string hardwareConfigFileName; /*!< Which configuration did the RunControl load? */
  std::string hostName;               /*!< What machine is the DAQ running on? */
  std::string lastTriggerFileName;    /*!< Log file for status communication with the RunControl. */
  std::string globalGateLogFileName;  /*!< Where are we tracking the global gate number? */

};

#endif
