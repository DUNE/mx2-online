#ifndef EventBuilder_h
#define EventBuilder_h
/*! 
  \file EventBuilder.h
  \author Gabriel Perdue
  \author Elaine Schulte
  \author Jeremy Wolcott

  \brief The EventBuilder logs events declared by the DAQ to file.

  The Event Builder is a separate process which will act as a 
  simple local socket-based server process that consumes data 
  for storage and publication to the monitoring framework.  
*/

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


#endif
