#ifndef DAQWorkerUtils_h
#define DAQWorkerUtils_h
/*! \file DAQWorkerUtils.h
*/

#include "DAQWorkerArgs.h"
#include "DAQHeader.h"

#include <fstream>
#include <string>
#include <sstream>

/*! 
  \class DAQWorkerUtils
  \utilities class for odds and ends...
  \author Carrie McGivern
  */
class DAQWorkerUtils {

  private: 

  const DAQWorkerArgs* args;
  //DAQWorkerUtils* daqUtils;

  public:

  explicit DAQWorkerUtils( const DAQWorkerArgs* theArgs );
  ~DAQWorkerUtils();

  unsigned long long GetTimeInMicrosec() const;

};

#endif
