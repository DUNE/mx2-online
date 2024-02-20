#ifndef ECROC_cpp
#define ECROC_cpp
/*! \file ECROC.cpp
*/

#include "ECROC.h"
#include "exit_codes.h"

log4cpp::Category& ECROCLog = log4cpp::Category::getInstance(std::string("ECROC"));

const unsigned short ECROC::RDFEDelayRegisterDelayMask = 0x03FF;
const unsigned short ECROC::RDFEDelayRegisterEnableMask = 0x8000;
const unsigned short ECROC::RDFEDelayRegisterEnableBit = 15;

//----------------------------------------
ECROC::ECROC(unsigned int address, const Controller* controller) :
  VMECommunicator( address, controller )
{
  this->commType = VMEModuleTypes::ECROC;
  timingSetupAddress           = this->address + VMEModuleTypes::ECROCTimingSetup;
  resetAndTestPulseMaskAddress = this->address + VMEModuleTypes::ECROCResetAndTestPulseMask;
  channelResetAddress          = this->address + VMEModuleTypes::ECROCChannelReset;
  fastCommandAddress           = this->address + VMEModuleTypes::ECROCFastCommand;
  testPulseAddress             = this->address + VMEModuleTypes::ECROCTestPulse;
  rdfePulseDelayAddress        = this->address + VMEModuleTypes::ECROCRdfePulseDelay;
  rdfePulseCommandAddress      = this->address + VMEModuleTypes::ECROCRdfePulseCommand;

  ECROCLog.setPriority(log4cpp::Priority::DEBUG); 

  MakeChannels(); 
}

//----------------------------------------
ECROC::~ECROC() 
{ 
  for (std::vector<EChannels*>::iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) 
    delete (*p);
  ECROCChannels.clear();
}

//----------------------------------------
unsigned int ECROC::GetAddress() const
{
  return this->address;
}

//----------------------------------------
unsigned int ECROC::GetCROCNumber() const
{
  return ( (this->address)>>VMEModuleTypes::ECROCAddressShift );
}

//----------------------------------------
//! Make, but do not initialize, the EChannels.
void ECROC::MakeChannels() 
{
  for ( unsigned int i=0; i<4; ++i ) { 
    EChannels *tmp = new EChannels( this->address, i, this->GetController() );
    ECROCChannels.push_back( tmp ); 
  }
}

//----------------------------------------
//! Remove EChannels with no FEBs from the container vector.
void ECROC::ClearEmptyChannels()
{
  std::vector<EChannels*> tempChannels; 
  for (std::vector<EChannels*>::iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) {
    if ( (*p)->GetNumFrontEndBoards() > 0 ) {
      tempChannels.push_back(*p);
    }
    else {
      delete (*p);
    }
  }
  ECROCChannels.clear();
  for (std::vector<EChannels*>::iterator p=tempChannels.begin();
      p!=tempChannels.end();
      p++) {
    ECROCChannels.push_back( *p );
  }
  tempChannels.clear();
}

//----------------------------------------
EChannels* ECROC::GetChannel( unsigned int i ) 
{ 
  return ECROCChannels[i];   // TODO : use an enum for this, perhaps add some bounds checks? or too slow?
}

//----------------------------------------
std::vector<EChannels*>* ECROC::GetChannelsVector() 
{
  return &ECROCChannels;
}

//----------------------------------------  
void ECROC::SetupTimingRegister( VMEModuleTypes::ECROCClockModes clockMode, 
    unsigned short testPulseDelayEnabled, 
    unsigned short testPulseDelayValue ) const
{
  unsigned short timingRegisterMessage  = clockMode;   	      // the clock mode  (0x8000 is the bitmask for bit 15 high)
  timingRegisterMessage |= (testPulseDelayEnabled & 0x1)<<12; // test pulse delay enable bit (bit 12)
  timingRegisterMessage |= testPulseDelayValue & 0x3FF;       // test pules delay values (in 18.9 ns units) bits 0-9
  timingRegisterMessage &= 0xFFFF;
#ifndef GOFAST
  ECROCLog.debugStream() << " Timing Register Message = 0x" << std::hex << timingRegisterMessage; 
#endif
  unsigned char command[] = { timingRegisterMessage & 0xFF, (timingRegisterMessage & 0xFF00)>>8 }; 
#ifndef GOFAST
  ECROCLog.debugStream() << " Timing Register Bytes   = 0x" << std::hex << (int)command[0] << ", 0x" << (int)command[1]; 
#endif
  int error = WriteCycle(2, command, timingSetupAddress, addressModifier, dataWidthReg );
  if( error ) throwIfError( error, "Failure writing to CROC Timing Register!");
}

//---------------------------------------- 
void ECROC::SetupResetAndTestPulseRegister( unsigned short resetEnable, unsigned short testPulseEnable ) const
{
  unsigned short resetAndTestPulseMaskRegisterMessage = (resetEnable & 0x1)<<8;  //the reset enable bit is 8
  resetAndTestPulseMaskRegisterMessage |= (testPulseEnable & 0x1);               //the test pulse enable bit is 0
#ifndef GOFAST
  ECROCLog.debugStream() << " Reset and Test Pulse Register Message = 0x" << std::hex << resetAndTestPulseMaskRegisterMessage; 
#endif
  unsigned char command[] = { resetAndTestPulseMaskRegisterMessage & 0xFF, (resetAndTestPulseMaskRegisterMessage & 0xFF00)>>8 }; 
#ifndef GOFAST
  ECROCLog.debugStream() << " Reset and Test Pulse Register Bytes   = 0x" << std::hex << (int)command[0] << ", 0x" << (int)command[1]; 
#endif
  int error = WriteCycle(2, command, resetAndTestPulseMaskAddress, addressModifier, dataWidthReg );
  if( error ) throwIfError( error, "Failure writing to CROC Reset and Test Pulse Register!");
}

//---------------------------------------- 
void ECROC::InitializeRegisters( VMEModuleTypes::ECROCClockModes clockMode, 
    unsigned short testPulseDelayValue,
    unsigned short testPulseDelayEnabled,
    unsigned short sequencerDelayValue,
    Modes::RunningModes runningMode) const
{
  using namespace Modes;
  SetupTimingRegister( clockMode, testPulseDelayEnabled, testPulseDelayValue );
  SetupResetAndTestPulseRegister( 0, 0 );
  // 120/12/2014 Geoff Savage
  // Turn off automatic RDFE for "cosmics" mode.
  switch (runningMode) {
    case Cosmics:
    case MTBFBeamMuon:
    case MTBFBeamOnly:
      SequencerDelayDisable();
      break;
    case OneShot:
    case NuMIBeam:
    case PureLightInjection:
    case MixedBeamPedestal:
    case MixedBeamLightInjection:
      SequencerDelayEnable();
      break;
    default:
      ECROCLog.fatalStream() << "InitializeRegisters: No Running Mode defined!";
      exit(EXIT_CONFIG_ERROR);
  }
  SetSequencerDelayValue( (sequencerDelayValue&0x01FF) ); // steps of 2.411 microseconds
}

//----------------------------------------
void ECROC::FastCommandOpenGate() const
{
  unsigned char command[] = {0xB1};
  int error = WriteCycle(1, command, fastCommandAddress, addressModifier, dataWidthReg );
  if( error ) throwIfError( error, "Failure writing to CROC FastCommand Register!");
}

//----------------------------------------
void ECROC::ClearAndResetStatusRegisters() const
{
  for (std::vector<EChannels*>::const_iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) 
    (*p)->ClearAndResetStatusRegister();
}

//----------------------------------------
void ECROC::ResetEventCounter() const
{
  for (std::vector<EChannels*>::const_iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) 
    (*p)->ResetEventCounter();
}

//----------------------------------------
void ECROC::EnableSequencerReadout() const
{
  for (std::vector<EChannels*>::const_iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) 
    (*p)->EnableSequencerReadout();
}

//----------------------------------------
void ECROC::DisableSequencerReadout() const
{
  for (std::vector<EChannels*>::const_iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) 
    (*p)->DisableSequencerReadout();
}

//----------------------------------------
void ECROC::ConfigureForStandardDataTaking() const
{
  for (std::vector<EChannels*>::const_iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) 
    (*p)->ConfigureForStandardDataTaking();
}

//----------------------------------------
void ECROC::UseSinglePipelineReadout() const
{
  for (std::vector<EChannels*>::const_iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) 
    (*p)->UseSinglePipelineReadout();
}

//----------------------------------------
void ECROC::SendSoftwareRDFE() const
{
#ifndef GOFAST
  ECROCLog.debugStream() << "SendSoftwareRDFE"; 
#endif

  unsigned char command[] = {0x1F};
  int error = WriteCycle(1, command, rdfePulseCommandAddress, addressModifier, dataWidthReg );
  if( error ) throwIfError( error, "Failure writing to CROC Software RDFE Register!");
}

//----------------------------------------
void ECROC::WaitForSequencerReadoutCompletion() const
{
  for (std::vector<EChannels*>::const_iterator p=ECROCChannels.begin();
      p!=ECROCChannels.end();
      p++) 
    (*p)->WaitForSequencerReadoutCompletion();
}

//----------------------------------------
void ECROC::Initialize(Modes::RunningModes runningMode) const
{
  ECROCLog.infoStream() << "Initializing ECROC 0x" << std::hex << this->address;
  unsigned short testPulseDelayEnabled = 0;  // we do not use the test pulse delay in data-taking
  unsigned short testPulseDelayValue   = 0;
  unsigned short sequencerDelayValue   = 511;   // x 2.4e-6 s
  this->ClearAndResetStatusRegisters();
  this->EnableSequencerReadout();
  this->InitializeRegisters( (VMEModuleTypes::ECROCClockModes)VMEModuleTypes::ECROCExternal, 
      testPulseDelayEnabled, testPulseDelayValue, sequencerDelayValue,
      runningMode );
}

//----------------------------------------
unsigned short ECROC::ReadSequencerPulseDelayRegister() const
{
  unsigned short configuration = 0;
  unsigned char receivedMessage[] = {0x0,0x0};

#ifndef GOFAST
  ECROCLog.debugStream() << "Read ReadSequencerPulseDelayRegister Address = " << 
    std::hex << rdfePulseDelayAddress;
#endif
  int error = ReadCycle( receivedMessage, rdfePulseDelayAddress, addressModifier, dataWidthReg); 
  if( error ) throwIfError( error, "Failure reading the RDFE Configuration!"); 
  configuration = receivedMessage[1]<<0x08 | receivedMessage[0];
#ifndef GOFAST
  ECROCLog.debugStream() << " Sequencer Delay Configuration = 0x" << 
    std::hex << configuration;
#endif

  return configuration;

}

//----------------------------------------
void ECROC::SetSequencerDelayeRegister( unsigned short configuration ) const
{
#ifndef GOFAST
  ECROCLog.debugStream() << "SetSequencerDelayeRegister for " << (*this) 
    << " value = 0x" << std::hex << configuration;
#endif
  unsigned char config[] = {0x0,0x0};
  config[0] = configuration & 0xFF;
  config[1] = (configuration & 0xFF00)>>8;
  int error = WriteCycle( 2, config, rdfePulseDelayAddress, addressModifier, dataWidthReg); 
  if( error ) throwIfError( error, "Failure writing to RDFE Pulse Delay register!"); 
}

//----------------------------------------
void ECROC::SequencerDelayEnableDisable( unsigned short bit ) const
{
  unsigned short configuration = this->ReadSequencerPulseDelayRegister();
  configuration = configuration & RDFEDelayRegisterDelayMask;
  configuration = configuration | (bit << RDFEDelayRegisterEnableBit);
#ifndef GOFAST
  ECROCLog.debugStream() << "SequencerDelayEnableDisable for " << (*this) 
    << " target value = 0x" << std::hex << configuration;
#endif
  this->SetSequencerDelayeRegister( configuration );
}

//----------------------------------------
void ECROC::SequencerDelayDisable() const
{
  this->SequencerDelayEnableDisable( (unsigned short)0 );
}

//----------------------------------------
void ECROC::SequencerDelayEnable() const
{
  this->SequencerDelayEnableDisable( (unsigned short)1 );
}

//----------------------------------------
void ECROC::SetSequencerDelayValue( unsigned short delay ) const
{
  unsigned short configuration = this->ReadSequencerPulseDelayRegister();
  configuration = configuration & RDFEDelayRegisterEnableMask;
  configuration = configuration | ( delay & RDFEDelayRegisterDelayMask );
#ifndef GOFAST
  ECROCLog.debugStream() << "SequencerDelayValue for " << (*this) 
    << " target value = 0x" << std::hex << configuration;
#endif
  this->SetSequencerDelayeRegister( configuration );
}

/*
12/10/2014 Geoff Savage
Additions for running in "cosmics" mode.
*/

void ECROC::FastCommandFEBTriggerRearm() const {
  unsigned char command[] = {0x85};
  int error = WriteCycle(1, command, fastCommandAddress, addressModifier, dataWidthReg );
  if( error ) throwIfError( error, "Failure writing to CROC FastCommand Register! For Trigger Rearm.");
#ifndef GOFAST
  ECROCLog.debugStream() << " FEB Trigger rearm fast command issued.";
#endif
}


#endif
