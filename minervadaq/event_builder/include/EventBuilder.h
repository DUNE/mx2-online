#ifndef EventBuilder_h
#define EventBuilder_h

#include <string>
#include <sstream>
#include <fstream>
#include <signal.h>
#include "DAQEvent.h" 
#include "DAQEventTemplates.h"
#include "eb_service.h"  // the header files needed to run the service
#include "et.h"          // the event transfer stuff
#include "et_private.h"  // event transfer private data types
#include "et_data.h"     // data structures 

#include "FEB.h"

/* #define MAX_CONNECTIONS 500 */

/*! \file
 *
 * The Event Builder is a separate process which will act as a 
 * simple local socket-based server process that consumes data 
 * for storage and publication to the monitoring framework.  
 */

// The CROC-E DAQ receives "globs" of data spanning entire chains.

struct EventHandler {
  unsigned char eventData[ MaxTotalDataPerChain ];
};


#endif
