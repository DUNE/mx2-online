#ifndef daqmain_cxx
#define daqmain_cxx
/*! 
  \file daqmain.cpp
  \brief Implementation file for the Minerva DAQ entry point.
  \author Gabriel Perdue
*/

#include <fstream>
#include <iostream>
#include <sstream>
#include <assert.h>

#include "log4cppHeaders.h"
#include "DAQWorker.h"
#include "DAQArgs.h"
#include "ReadoutTypes.h"
#include "exit_codes.h"
#include "daqmain.h"

// log4cpp message levels:
//	emergStream(), fatalStream(), alert..., crit..., error..., warn..., notice..., info..., debug...
log4cpp::Appender* baseAppender;
log4cpp::Category& rootCat = log4cpp::Category::getRoot();
log4cpp::Category& daqmain = log4cpp::Category::getInstance(std::string("daqmain"));

//---------------------------------------------------------------
int main( int argc, char * argv[] ) 
{
  struct DAQWorkerArgs * args = DAQArgs::ParseArgs( argc, argv, "0" );

  baseAppender = new log4cpp::FileAppender("default", args->logFileName, false);
  baseAppender->setLayout(new log4cpp::BasicLayout());
  rootCat.addAppender(baseAppender);
  rootCat.setPriority(log4cpp::Priority::DEBUG);
  daqmain.setPriority(log4cpp::Priority::DEBUG);
  daqmain.infoStream() << "Starting MinervaDAQ...";

  // set the signal handlers
  SetUpSigAction();

  continueRunning = true;
  DAQWorker * worker = new DAQWorker( args, log4cpp::Priority::DEBUG, &continueRunning );

  int error = 0;
  error = worker->SetUpET(); 
  bool sentSentinel = false;
  if (0 == error) {
    try {
      worker->InitializeHardware();
      worker->TakeData();
      sentSentinel = worker->SendSentinel();
      if (worker->CloseDownET()) {
        daqmain.infoStream() << "Detached from ET station..."; 
      }
      //SMEDLEY 3/9/2023
      else {
        daqmain.debugStream() << "DAQMain faield to detach from ET station...";
      }
      worker->CleanupHardware();
    }
    catch (FHWException &e) {
      worker->WriteExceptionToDB(e);
      daqmain.errorStream() << "Exception! " << e.what();

      // we always want to send this if we can
      if (!sentSentinel)
        sentSentinel = worker->SendSentinel();

    }
    catch (std::exception &e) {
      daqmain.errorStream() << "Exception! " << e.what();

      // we always want to send this if we can
      if (!sentSentinel)
        sentSentinel = worker->SendSentinel();
    }
 }
  else {
    daqmain.fatalStream() << "Failed to establish ET connection!";
  }

  daqmain.infoStream() << "Finished MinervaDAQ...";
  worker->WriteRunDataToDB();

  delete worker;
  delete args;
  log4cpp::Category::shutdown();

  //std::cout << "Sent sentinel: " << sentSentinel << std::endl;
  return (sentSentinel) ? EXIT_CLEAN_SENTINEL : EXIT_CLEAN_NOSENTINEL;
}

//---------------------------------------------------------------
//! Set up the signal handler so we can always exit cleanly.
void SetUpSigAction()
{
  struct sigaction quit_action;
  quit_action.sa_handler = quitsignal_handler;
  sigemptyset (&quit_action.sa_mask);
  // restart interrupted system calls instead of failing with EINTR
  quit_action.sa_flags = SA_RESTART;    

  sigaction(SIGINT,  &quit_action, NULL);
  sigaction(SIGTERM, &quit_action, NULL);
}

//---------------------------------------------------------------
//! Handle the SIGINT & SIGNUM signals (both of which should exit the process).
void quitsignal_handler(int signum)
{
  daqmain.debugStream() << "Quit Signal Received!"; //SMEDLEY 3/9/2023
  continueRunning = false;
}


#endif
