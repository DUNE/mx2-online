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

log4cpp::Category& readoutLogger = log4cpp::Category::getInstance(std::string("readoutLogger"));

//---------------------------
ReadoutWorker::ReadoutWorker( int theCrateID, log4cpp::Priority::Value priority, bool VMEInit ) :
  crateID(theCrateID),
  vmeInit(VMEInit)
{
  readoutLogger.setPriority(priority);

  controller = new Controller(0x00, crateID);
  int error = controller->Initialize();
  if ( 0 != error ) {
    readoutLogger.fatalStream() << "Controller contact error: " << error 
      << "; for Crate ID = " << crateID; 
    exit(error);
  }
  readoutLogger.debugStream() << "Made new ReadoutWokrer with crate ID = " << crateID 
    << "; VME Init = " << vmeInit
    << "; Logging Level = " << priority;
}

//---------------------------
ReadoutWorker::~ReadoutWorker() {
  readoutChannels.clear();
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
const Controller* ReadoutWorker::GetController() const
{
  return controller;
}

//---------------------------
void ReadoutWorker::InitializeCrate( RunningModes runningMode )
{
  readoutLogger.debugStream() << "Initialize Crate " << crateID << " for Running Mode: " << (RunningModes)runningMode;

  for( std::vector<CRIM*>::iterator p=crims.begin(); p!=crims.end(); ++p ) {
    (*p)->Initialize( runningMode );
  }
  for( std::vector<ECROC*>::iterator p=ecrocs.begin(); p!=ecrocs.end(); ++p ) {
    (*p)->Initialize();
    std::vector<EChannels*>* channels = (*p)->GetChannelsVector();
    readoutChannels.insert(readoutChannels.end(),channels->begin(),channels->end());
  }
  this->masterCRIM()->IRQEnable();
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

  ECROC *theECROC = new ECROC( address, this->controller );
  theECROC->ClearAndResetStatusRegisters();
  readoutLogger.debugStream() << " Adding FEBs to Channels...";
  theECROC->GetChannel( 0 )->SetupNFrontEndBoards( nFEBchan0 );
  readoutLogger.debugStream() << " Setup Channel 0 with " << nFEBchan0 << " FEBS.";
  theECROC->GetChannel( 1 )->SetupNFrontEndBoards( nFEBchan1 );
  readoutLogger.debugStream() << " Setup Channel 1 with " << nFEBchan1 << " FEBS.";
  theECROC->GetChannel( 2 )->SetupNFrontEndBoards( nFEBchan2 );
  readoutLogger.debugStream() << " Setup Channel 2 with " << nFEBchan2 << " FEBS.";
  theECROC->GetChannel( 3 )->SetupNFrontEndBoards( nFEBchan3 );
  readoutLogger.debugStream() << " Setup Channel 3 with " << nFEBchan3 << " FEBS.";
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
  CRIM* crim = new CRIM( address, this->controller );
  readoutLogger.debugStream() << " CRIM Status = 0x" << std::hex << crim->GetStatus();
  crims.push_back( crim );
  readoutLogger.debugStream() << "Added CRIM.";
}

//---------------------------
void ReadoutWorker::Trigger()
{
  readoutLogger.debugStream() << "ReadoutWorker::Trigger...";
  // Use a dummy trigger for now...
  for (std::vector<ECROC*>::iterator p=ecrocs.begin(); p!=ecrocs.end(); ++p) {
    (*p)->FastCommandOpenGate();
    (*p)->EnableSequencerReadout();
    (*p)->SendSoftwareRDFE();
    (*p)->WaitForSequencerReadoutCompletion();
  }

}

//---------------------------
void ReadoutWorker::Reset()
{
  currentChannel=readoutChannels.begin();
}


//---------------------------
bool ReadoutWorker::MoveToNextChannel()
{
  readoutLogger.debugStream() << "ReadoutWorker::MoveToNextChannel: Current Channel: " << **currentChannel; 
  currentChannel++;
  if (currentChannel == readoutChannels.end()) {
    readoutLogger.debugStream() << "Reached end of Channels.";
    return false;
  }
  readoutLogger.debugStream() << "New Channel: " << **currentChannel;
  return true;
}

//---------------------------
const EChannels * ReadoutWorker::CurrentChannel() const
{
  return (*currentChannel);
}

//---------------------------
unsigned short ReadoutWorker::GetNextDataBlockSize() const
{
  if (currentChannel != readoutChannels.end()) {
    return (*currentChannel)->ReadDPMPointer();
  }
  return 0;
}

//---------------------------
std::tr1::shared_ptr<SequencerReadoutBlock> ReadoutWorker::GetNextDataBlock( unsigned short blockSize ) const
{
  if (currentChannel == readoutChannels.end()) {
    readoutLogger.fatalStream() << "Attempting to read data from a NULL Channel!";
    exit( EXIT_CROC_UNSPECIFIED_ERROR );
  }
  std::tr1::shared_ptr<SequencerReadoutBlock> block(new SequencerReadoutBlock());
  block->SetData( (*currentChannel)->ReadMemory( blockSize ), blockSize );
  return block;
}

#endif
