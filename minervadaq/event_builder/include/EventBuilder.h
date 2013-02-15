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

/*

struct event_handler { //the structure to hold the data
  bool quit, new_event, done; // we need some status info 
  unsigned char		detectorType;   // Enumerated in the DAQHeader Class 
  unsigned short int	detectorConfig; // Number of modules in the detector
  unsigned int		runNumber;      // Run series demarcator.
  unsigned int		subRunNumber;   // Run within a series.
  unsigned short int	triggerType;    // Mask to select 8 least significant bits
  unsigned char		ledLevel;       // Sets OnePE vs. MaxPE in header.
  unsigned char		ledGroup;       // Which LED group is fired? - Valid for 2009 LED box.
  unsigned long long	globalGate;     // Total gate for the detector.
  unsigned long long	gate;           // Gate within a subrun.
  unsigned long long	triggerTime;    // Time in microseconds after the epoch. 		
  unsigned short int	readoutInfo;    // Readout type and errors... break these up? timingVio is obsolete
  unsigned int 		minosSGATE;     // Only 28 significant bits.
  unsigned int            readoutTime;    // We will only report 24 bits (DAQ Header v8+).
  unsigned int feb_info[9]; // 0: link_no, 1: crate_no, 2: croc_no, 3: chan_no, 4: bank, 5: buffer length, 
6: feb number, 7: feb firmware, 8: hits; //hardware info & data type 
  unsigned char event_data[FEB_DISC_SIZE]; // the data we're going to process - largest possible frame? 
}; 

int event_builder(event_handler *evt); //a helper function which sorts data into the event

template <class X> void DecodeBuffer(event_handler *evt, X *frame, int i, int length); 

template <class X> MinervaHeader* BuildBankHeader(event_handler *evt, X *frame); 

int CheckBufferLength(int length, int frame_length); 

void HandleErrors(int i); 

*/

#endif
