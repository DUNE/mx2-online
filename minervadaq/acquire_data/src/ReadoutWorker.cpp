#ifndef ReadoutWorker_cxx
#define ReadoutWorker_cxx

#include "ReadoutWorker.h"
#include "exit_codes.h"
#include <time.h>
//#include <sys/time.h>
//#include <signal.h>   // for sig_atomic_t

log4cpp::Category& readoutLogger = log4cpp::Category::getInstance(std::string("readoutLogger"));

//---------------------------
ReadoutWorker::ReadoutWorker( log4cpp::Priority::Value priority, 
    bool *theStatus, bool VMEInit ) :
  status(theStatus),
  vmeInit(VMEInit),
  runningMode((RunningModes)0)
{
  readoutLogger.setPriority(priority);
  readoutLogger.debugStream() << "Made new ReadoutWokrer."; 
}

//---------------------------
ReadoutWorker::~ReadoutWorker() {
  readoutChannels.clear();
  for ( std::vector<VMECrate*>::iterator p=crates.begin(); p!=crates.end(); ++p ) {
    (*p)->DisableSequencerReadout();
    delete (*p);
  }
  crates.clear();
}

//---------------------------
void ReadoutWorker::AddCrate( unsigned int crateID )
{
  VMECrate * crate = new VMECrate( crateID, log4cpp::Priority::DEBUG, vmeInit );
  crates.push_back( crate );
}

//---------------------------
void ReadoutWorker::InitializeCrates( RunningModes theRunningMode )
{
  runningMode = theRunningMode;
  readoutLogger.debugStream() << "InitializeCrates";

  for ( std::vector<VMECrate*>::iterator p=crates.begin(); 
      p!=crates.end();
      ++p ) {
    (*p)->Initialize( runningMode );
  } 

  for ( std::vector<VMECrate*>::iterator p=crates.begin(); 
      p!=crates.end();
      ++p ) {
    std::vector<ECROC*>* crocs = (*p)->GetECROCVector();
    for ( std::vector<ECROC*>::iterator q=crocs->begin();
        q!=crocs->end();
        ++q ) {
      std::vector<EChannels*>* channels = (*q)->GetChannelsVector();
      readoutChannels.insert(readoutChannels.end(),channels->begin(),channels->end());
    }
  } 
  EnableIRQ();
  readoutLogger.debugStream() << "Finished Crate Initialization for " << (*this);
}

//---------------------------
CRIM* ReadoutWorker::MasterCRIM() const
{
  VMECrate* crate = NULL;
  CRIM* crim = NULL;
  if ( crates.size() ) { 
    crate = crates[0];
    if ( crate->GetCRIMVector()->size() ) {
      crim = crate->GetCRIMVector(0);
    } 
    else {
      readoutLogger.fatalStream() << "CRIM vector length is 0! Cannot return a master CRIM!";
      exit(EXIT_CRIM_UNSPECIFIED_ERROR);
    }
  } 
  else {
    readoutLogger.fatalStream() << "CRATE vector length is 0! Cannot return a master CRIM!";
    exit(EXIT_CRIM_UNSPECIFIED_ERROR);
  }
  return crim;
}

//---------------------------
void ReadoutWorker::EnableIRQ() const
{
  readoutLogger.debugStream() << "Enabling IRQ for master CRIM.";
  this->MasterCRIM()->IRQEnable();
}

//---------------------------
bool ReadoutWorker::WaitForIRQ() const
{
  readoutLogger.debugStream() << "Wait for IRQ for master CRIM.";
  int success = this->MasterCRIM()->WaitForIRQ( status );
  if (0 == success) return true;
  return false;
}

//---------------------------
void ReadoutWorker::AcknowledgeIRQ() const
{
  readoutLogger.debugStream() << "Acknowledge IRQ for master CRIM.";
  this->MasterCRIM()->AcknowledgeIRQ();
}

//---------------------------
unsigned int ReadoutWorker::GetMINOSSGATE() const
{
  return this->MasterCRIM()->MINOSSGATE();
}

//---------------------------
std::vector<VMECrate*>* ReadoutWorker::GetVMECrateVector()
{
	return &crates;
}

//---------------------------
VMECrate* ReadoutWorker::GetVMECrateVector( int index )
{
	return crates[index];
}

//---------------------------
unsigned long long ReadoutWorker::GetNowInMicrosec() const
{
  struct timeval run;
  gettimeofday(&run, NULL);
  return (unsigned long long)(run.tv_sec*1000000) + (unsigned long long)(run.tv_usec);
}

//---------------------------
unsigned long long ReadoutWorker::Trigger( TriggerType triggerType )
{
  readoutLogger.debugStream() << "ReadoutWorker::Trigger for type = " 
    << triggerType;
  this->ClearAndResetStatusRegisters();

  // reset sequencer latch

  EnableIRQ();

  switch (triggerType) {
    case Pedestal:        // In pedestal-type modes, we trigger all CRIMs
    case ChargeInjection: // using software.
      SendSoftwareGate();
      break;
    case LightInjection: // Only trigger master w/software in LI.
      this->MasterCRIM()->SendSoftwareGate(); 
      break;             // In LI and all beam modes, we rely on LEMO connection
    case Cosmic:         // between the CRIMs because all gates must open 
    case NuMI:           // simultaneously. We need take no direct action and 
    case MTBFMuon:       // may just watch the interrupt (which we poll, and 
    case MTBFBeam:       // don't really use as an interrupt).
      break;
    default:
      readoutLogger.errorStream() << "Impossible Trigger Type!";
  }

  if (!WaitForIRQ()) return 0;

  // acknowledge IRQ

  // Run Sleepy - the FEBs need >= 400 microseconds for 8 hits to digitize.
  // nanosleep runs about 3x slower than the stated time (so 100 us -> 300 us)
  if (!MicroSecondSleep(100)) return 0;

  return this->GetNowInMicrosec();
}

//---------------------------
void ReadoutWorker::ResetSequencerLatch() const
{
  for (std::vector<VMECrate*>::const_iterator p=crates.begin(); p!=crates.end(); ++p) 
    (*p)->ResetSequencerLatch();
}

//---------------------------
void ReadoutWorker::SendSoftwareGate() const
{
  for (std::vector<VMECrate*>::const_iterator p=crates.begin(); p!=crates.end(); ++p) 
    (*p)->SendSoftwareGate();
}

//---------------------------
void ReadoutWorker::OpenGateFastCommand() const
{
  for (std::vector<VMECrate*>::const_iterator p=crates.begin(); p!=crates.end(); ++p) 
    (*p)->OpenGateFastCommand();
}

//---------------------------
void ReadoutWorker::ClearAndResetStatusRegisters() const
{
  for (std::vector<VMECrate*>::const_iterator p=crates.begin(); p!=crates.end(); ++p) 
    (*p)->ClearAndResetStatusRegisters();
}

//---------------------------
bool ReadoutWorker::MicroSecondSleep(int us) const
{
  timespec tmReq;
  tmReq.tv_sec = (time_t)(0);
  tmReq.tv_nsec = us * 1000;
  // if nanosleep is not available, use: usleep(us);
  (void)nanosleep(&tmReq, (timespec *)NULL); 

  return true;
}

//---------------------------
void ReadoutWorker::ResetCurrentChannel()
{
  currentChannel = readoutChannels.begin();
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
  readoutLogger.debugStream() << "Getting Data Block for " << (**currentChannel);
  std::tr1::shared_ptr<SequencerReadoutBlock> block(new SequencerReadoutBlock());
  block->SetData( (*currentChannel)->ReadMemory( blockSize ), blockSize );
  return block;
}

//-----------------------------
std::ostream& operator<<(std::ostream& out, const ReadoutWorker& s)
{
  for (std::vector<VMECrate*>::const_iterator p=s.crates.begin(); p!=s.crates.end(); ++p) {
    out << "Crate = " << (**p) << "; ";
  }
  return out;
}

#endif
