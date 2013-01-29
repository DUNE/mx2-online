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

  controller = new Controller(0x00, controllerID, appender);
  int error = controller->Initialize();
  if ( 0 != error ) {
    readoutLogger.fatalStream() << "Controller contact error: " << error; 
    exit(error);
  }
  readoutLogger.debugStream() << "Made new ReadoutWokrer with crate ID = " << controllerID 
    << "; VME Init = " << vmeInit
    << "; Logging Level = " << priority;
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
  delete controller; 
}

//---------------------------
Controller* ReadoutWorker::GetController() 
{
  return controller;
}

//---------------------------
void ReadoutWorker::InitializeCrate( RunningModes runningMode )
{
  readoutLogger.debugStream() << "Initialize Crate " << controllerID << " for Running Mode: " << (RunningModes)runningMode;

  for( std::vector<CRIM*>::iterator p=crims.begin(); p!=crims.end(); ++p ) {
    (*p)->Initialize( runningMode );
  }
  for( std::vector<ECROC*>::iterator p=ecrocs.begin(); p!=ecrocs.end(); ++p ) {
    (*p)->Initialize();
  }

}

//---------------------------
CRIM* ReadoutWorker::masterCRIM()
{
  CRIM* crim = NULL;
  if( crims.size() ) { 
    crim = crims[0];
  } else {
    readoutLogger.fatalStream() << "CRIM vector length is 0! Cannot return a master CRIM!";
    exit(EXIT_CRIM_UNSPECIFIED_ERROR);
  }
  return crim;
}

//---------------------------
void ReadoutWorker::AddECROC( unsigned int address, int nFEBchan0, int nFEBchan1, int nFEBchan2, int nFEBchan3 )
{
  if (address < (1<<ECROCAddressShift)) {
    address = address << ECROCAddressShift;
  }
  readoutLogger.debugStream() << "Adding ECROC with address = 0x" << std::hex << address << " and FEBs-to-Channel of (" 
    << std::dec << nFEBchan0 << ", " << nFEBchan1 << ", " << nFEBchan2 << ", " << nFEBchan3 << ")";
  if (nFEBchan0<0 || nFEBchan0>10) nFEBchan0 = 0;
  if (nFEBchan1<0 || nFEBchan1>10) nFEBchan1 = 0;
  if (nFEBchan2<0 || nFEBchan2>10) nFEBchan2 = 0;
  if (nFEBchan3<0 || nFEBchan3>10) nFEBchan3 = 0;

  ECROC *theECROC = new ECROC( address, this->rwAppender, this->controller );
  theECROC->ClearAndResetStatusRegisters();
  readoutLogger.debugStream() << " Adding FEBs to Channels...";
  theECROC->GetChannel( 0 )->SetupNFEBs( nFEBchan0 );
  readoutLogger.debugStream() << " Setup Channel 0";
  theECROC->GetChannel( 1 )->SetupNFEBs( nFEBchan1 );
  readoutLogger.debugStream() << " Setup Channel 1";
  theECROC->GetChannel( 2 )->SetupNFEBs( nFEBchan2 );
  readoutLogger.debugStream() << " Setup Channel 2";
  theECROC->GetChannel( 3 )->SetupNFEBs( nFEBchan3 );
  readoutLogger.debugStream() << " Setup Channel 3";
  ecrocs.push_back( theECROC );
  readoutLogger.debugStream() << "Added ECROC.";
}

//---------------------------
void ReadoutWorker::AddCRIM( unsigned int address )
{
  if (address < (1<<CRIMAddressShift)) {
    address = address << CRIMAddressShift;
  }
  readoutLogger.debugStream() << "Adding CRIM with address = 0x" << std::hex << address; 
  CRIM* crim = new CRIM( address, this->rwAppender, this->controller );
  readoutLogger.debugStream() << " CRIM Status = 0x" << std::hex << crim->GetStatus();
  crims.push_back( crim );
  readoutLogger.debugStream() << "Added CRIM.";
}

#endif
