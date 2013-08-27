#ifndef DAQWorkerUtils_cxx
#define DAQWorkerUtils_cxx
/*! \file DAQWorkerUtils.cpp:  
*/

#include "DAQWorkerUtils.h"
//#include <time.h>
#include <sys/time.h>


//---------------------------
DAQWorkerUtils::DAQWorkerUtils( const DAQWorkerArgs* theArgs ) :
  args(theArgs)
{

}

//---------------------------
DAQWorkerUtils::~DAQWorkerUtils() 
{

}

//---------------------------
unsigned long long DAQWorkerUtils::GetTimeInMicrosec() const
{
  struct timeval run;
  gettimeofday(&run, NULL);
  return (unsigned long long)(run.tv_sec*1000000) + (unsigned long long)(run.tv_usec);
}

//---------------------------

#endif
