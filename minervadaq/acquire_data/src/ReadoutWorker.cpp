#ifndef ReadoutWorker_cxx
#define ReadoutWorker_cxx

#include "ReadoutWorker.h"
#include "exit_codes.h"
#include <time.h>
//#include <sys/time.h>
//#include <signal.h>   // for sig_atomic_t

log4cpp::Category& readoutLogger = log4cpp::Category::getInstance(std::string("readoutLogger"));

//---------------------------
ReadoutWorker::ReadoutWorker( log4cpp::Priority::Value priority, bool VMEInit ) :
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

  readoutLogger.debugStream() << "Enabling IRQ for master CRIM.";
  this->MasterCRIM()->IRQEnable();
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
unsigned long long ReadoutWorker::Trigger()
{
  readoutLogger.debugStream() << "ReadoutWorker::Trigger...";
  this->ClearAndResetStatusRegisters();

  // Basically, "OneShot"
  this->OpenGateFastCommand();
  // Run Sleepy - the FEBs need >= 400 microseconds for 8 hits to digitize.
  // nanosleep runs about 3x slower than the stated time (so 100 us -> 300 us)
  if (!MicroSecondSleep(100)) return 0;

  // This sequence is mode dependent...
  for (std::vector<VMECrate*>::iterator p=crates.begin(); p!=crates.end(); ++p) {
    (*p)->EnableSequencerReadout();
    (*p)->SendSoftwareRDFE();
    (*p)->WaitForSequencerReadoutCompletion();
    (*p)->DisableSequencerReadout();
  }

  struct timeval run;
  gettimeofday(&run, NULL);
  unsigned long long start = (unsigned long long)(run.tv_sec*1000000)
    + (unsigned long long)(run.tv_usec);

  return start;
}

//---------------------------
void ReadoutWorker::OpenGateFastCommand()
{
  for (std::vector<VMECrate*>::iterator p=crates.begin(); p!=crates.end(); ++p) 
    (*p)->OpenGateFastCommand();
}

//---------------------------
void ReadoutWorker::ClearAndResetStatusRegisters()
{
  for (std::vector<VMECrate*>::iterator p=crates.begin(); p!=crates.end(); ++p) 
    (*p)->ClearAndResetStatusRegisters();
}

//---------------------------
bool ReadoutWorker::MicroSecondSleep(int us)
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
    out << "Crate = " << (*p) << "; ";
  }
  return out;
}

#endif
