//we're gonna need some threads to make this even remotely efficient...
#include <string>
#include <sstream>
#include <fstream>
#include <boost/thread/thread.hpp>
#include <boost/bind.hpp>
#include <boost/thread/mutex.hpp>
#include "eb_service.h"
#include "MinervaEvent.h" //the event structure
#include "MinervaEvent_templates.h"
#include "eb_service.h" //the header files needed to run the service
#include "et.h" //the event transfer stuff
#include "et_private.h" //event transfer private data types
#include "et_data.h" //data structures 

#include "feb.h"

#define MAX_CONNECTIONS 500

/*! \file
 *
 * The Event Builder is a separate process which will act as a 
 * simple local socket-based server process.  This will take in 
 * data from the main minervadaq program and process it into 
 * the final event model.  The final event will then be placed on
 * the Event Transfer system for storage.
 *
 * Elaine Schulte
 * Rutgers University
 * August 18, 2009
 *
 */

/*! \struct event_handler
 *
 * \brief Holds frame data and run associated data for passing around through
 * different functions 
 */
struct event_handler { //the structure to hold the data
  bool quit, new_event, done; /*!<we need some status info */
  unsigned int run_info[5]; /*!<0: detector, 1: configuration, 2: run number, 3: sub-run number, 4: trigger type */
  unsigned int gate_info[5];  /*!< 0: g_gate, 1: gate, 2: trig_time, 3: error, 4: minos; gate information */
  unsigned int feb_info[9]; /*!<0: link_no, 1: crate_no, 2: croc_no, 3: chan_no, 4: bank 
                       5: buffer length, 6: feb number, 7: feb firmware, 8: hits; //hardware info & data type */
  unsigned char event_data[FEB_HITS_SIZE]; /*!<the data we're going to process */
  //unsigned char event_data[FEB_HITS_SIZE]; /*!<the data we're going to process */
}; 

/*! a helper function which sorts data into the event */
int event_builder(event_handler *evt); //a helper function which sorts data into the event
/*! a template function for decoding the event buffers  */
template <class X> void DecodeBuffer(event_handler *evt, X *frame, int i, int length); //a template function for decoding 
                                                                //the event buffers
/*! a function which build the necessary/header for each data bank */
template <class X> MinervaHeader* BuildBankHeader(event_handler *evt, X *frame); //a class which build the necessary
                                                       //header for each data bank
void CheckBufferLength(int length, int frame_length); //just what it says
void HandleErrors(int i); //an error handling function

/*! It's just a sad fact of life that we're going to have to do this the old 
*fashion way.  We need some global variables (the real kind of global
*variables).
*/

bool quit, done;

MinervaEvent *event;
