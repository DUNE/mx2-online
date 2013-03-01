#ifndef EventBuilder_h
#define EventBuilder_h

#include <string>
#include <sstream>
#include <fstream>
#include <signal.h>
#include "EventHandler.h"
#include "DAQHeader.h" 
#include "eb_service.h"  // the header files needed to run the service
#include "et.h"          // the event transfer stuff
#include "et_private.h"  // event transfer private data types
#include "et_data.h"     // data structures 

#include "MinervaDAQtypes.h"

/*! \file
 *
 * The Event Builder is a separate process which will act as a 
 * simple local socket-based server process that consumes data 
 * for storage and publication to the monitoring framework.  
 */


#endif
