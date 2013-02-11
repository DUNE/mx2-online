#ifndef daqmain_h
#define daqmain_h

#include "log4cppHeaders.h"

struct DAQWorkerArgs * parseArgs( const int& argc, char * argv[], const std::string& controllerID );


#endif
