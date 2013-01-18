/*! \file 
 *
 * ReadoutWorker.cpp:  Contains all of the functions needed for the 
 * initialization of DAQ electronics and execute an FEB acquisition.
 * Also contains the passing of data frames to the ET for further 
 * processing.
 */
#ifndef ReadoutWorker_cxx
#define ReadoutWorker_cxx

#include "ReadoutWorker.h"
#include "exit_codes.h"
//#include <sys/time.h>
//#include <signal.h>   // for sig_atomic_t

//---------------------------
ReadoutWorker::ReadoutWorker( int controllerID, log4cpp::Appender* appender, log4cpp::Priority::Value priority, bool vmeInit ) 
{
  this->controllerID = controllerID;
  rwAppender         = appender;
  vmeModuleInit      = vmeInit;
  readoutLogger.setPriority(priority);

  Controller *daqController = new Controller(0x00, controllerID, appender);
  int error = daqController->ContactController();
  if ( 0 != error ) {
    readoutLogger.fatalStream() << "Controller contact error: " << error; 
    exit(error);
  }
}

//---------------------------
ReadoutWorker::~ReadoutWorker() {
  for( std::vector<ECROC*>::iterator p=ecrocs.begin(); p!=ecrocs.end(); ++p ) {
    delete (*p);
  }
  ecrocs.clear();
  for( std::vector<CRIM*>::iterator p=crims.begin(); p!=crims.end(); ++p ) {
    delete (*p);
  }
  crims.clear();
  delete daqController; 
}

//---------------------------
void ReadoutWorker::InitializeCrate( RunningModes runningMode )
{
  readoutLogger.debugStream() << "Initialize Crate " << controllerID << " for Running Mode: " << (RunningModes)runningMode;

  InitializeCRIM( 0xE00000 /* "224" */, true, rwAppender );
}

//---------------------------
void ReadoutWorker::InitializeCRIM( unsigned int address, bool isMaster, log4cpp::Appender* appender )
{
  readoutLogger.debugStream() << "Initialize CRIM " << address << " with status == Master == " << isMaster;
  CRIM* crim = new CRIM( address, isMaster, appender, daqController );

  // TODO configure
  readoutLogger.debugStream() << " CRIM Status = " << crim->GetStatus();

  crims.push_back( crim );
}

#endif
