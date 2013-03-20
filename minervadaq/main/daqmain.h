#ifndef daqmain_h
#define daqmain_h
/*! 
  \file daqmain.h
  \brief Header file for the Minerva DAQ entry point.
  \author Gabriel Perdue
*/

void SetUpSigAction();
void quitsignal_handler(int signum);

bool continueRunning; /*!< Global status var to capture SIGINT, etc. signals from the RunControl. */

#endif
