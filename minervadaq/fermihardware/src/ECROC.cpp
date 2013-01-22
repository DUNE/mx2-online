#ifndef ECROC_cpp
#define ECROC_cpp

#include "ECROC.h"
#include "exit_codes.h"

/*********************************************************************************
* Class for creating CROC-E objects for use with the MINERvA data acquisition 
* system and associated software projects.
*
* Gabriel Perdue, The University of Rochester
**********************************************************************************/

log4cpp::Category& ECROCLog = log4cpp::Category::getInstance(std::string("ECROC"));

//----------------------------------------
ECROC::ECROC(unsigned int address, log4cpp::Appender* appender, Controller* controller) :
  VMECommunicator( address, appender, controller )
{
	timingSetupAddress           = this->address + ECROCTimingSetup;
	resetAndTestPulseMaskAddress = this->address + ECROCResetAndTestPulseMask;
	channelResetAddress          = this->address + ECROCChannelReset;
	fastCommandAddress           = this->address + ECROCFastCommand;
	testPulseAddress             = this->address + ECROCTestPulse;
	rdfePulseDelayAddress        = this->address + ECROCRdfePulseDelay;
	rdfePulseCommandAddress      = this->address + ECROCRdfePulseCommand;

	ECROCAppender = appender;
  if (ECROCAppender == 0 ) {
    std::cout << "ECROC Log Appender is NULL!" << std::endl;
    exit(EXIT_CROC_UNSPECIFIED_ERROR);
  }
  ECROCLog.setPriority(log4cpp::Priority::DEBUG); 

	MakeChannels(); 

	InitializeRegisters( crocExternal, (short unsigned int)0x0, (short unsigned int)0x0 );
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
unsigned int ECROC::GetAddress() 
{
	return this->address;
}

//----------------------------------------
void ECROC::MakeChannels() 
{
	for ( unsigned int i=0; i<4; ++i ) { 
		EChannels *tmp = new EChannels( this->address, i, ECROCAppender, this->GetController() );
		ECROCChannels.push_back( tmp ); 
	}
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
unsigned int ECROC::GetTimingSetupAddress()
{
	return timingSetupAddress;
}

//----------------------------------------
unsigned short ECROC::GetTimingRegisterMessage() 
{
	return timingRegisterMessage;
}

//----------------------------------------  // TODO: write to the hardware!
void ECROC::SetTimingRegisterMessage( crocClockModes clockMode, 
	unsigned short testPulseDelayEnabled, 
	unsigned short testPulseDelayValue )
{
	timingRegisterMessage  = clockMode;   	                    // the clock mode  (0x8000 is the bitmask for bit 15 high)
	timingRegisterMessage |= (testPulseDelayEnabled & 0x1)<<12; // test pulse delay enable bit (bit 12)
	timingRegisterMessage |= testPulseDelayValue & 0x3FF;       // test pules delay values (in 18.9 ns units) bits 0-9
	timingRegisterMessage &= 0xFFFF;
	ECROCLog.debugStream() << "    Timing Register = " << timingRegisterMessage; // TODO: hex!
}

//---------------------------------------- // TODO: write to the hardware!
void ECROC::SetResetAndTestPulseRegisterMessage( unsigned short resetEnable, unsigned short testPulseEnable )
{
	resetAndTestPulseMaskRegisterMessage  = (resetEnable & 0x1)<<8;  //the reset enable bit is 8
	resetAndTestPulseMaskRegisterMessage |= (testPulseEnable & 0x1); //the test pulse enable bit is 0
}

//----------------------------------------
unsigned int ECROC::GetFastCommandAddress()
{
	return fastCommandAddress;
}

//----------------------------------------
unsigned short ECROC::GetFastCommandRegisterMessage()
{
	return fastCommandRegisterMessage;
}

//---------------------------------------- // TODO: write to the hardware!
void ECROC::SetFastCommandRegisterMessage( unsigned short value ) 
{
	fastCommandRegisterMessage = value & 0xFF;
}

//---------------------------------------- // TODO: write to the hardware!
void ECROC::InitializeRegisters( crocClockModes clockMode, 
		unsigned short testPulseDelayValue,
		unsigned short testPulseDelayEnabled ) 
{
	SetTimingRegisterMessage( clockMode, testPulseDelayEnabled, testPulseDelayValue );
	SetResetAndTestPulseRegisterMessage( 0, 0 );
}

//----------------------------------------
void ECROC::FastCommandOpenGate()
{
  unsigned char command[] = {0xB1};
  int error = WriteCycle(1, command, fastCommandAddress, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Failure writing to CROC FastCommand Register!");
}

//----------------------------------------
void ECROC::ClearAndResetStatusRegisters()
{
	for (std::vector<EChannels*>::iterator p=ECROCChannels.begin();
			p!=ECROCChannels.end();
			p++) 
		(*p)->ClearAndResetStatusRegister();
}

//----------------------------------------
void ECROC::EnableSequencerReadout()
{
	for (std::vector<EChannels*>::iterator p=ECROCChannels.begin();
			p!=ECROCChannels.end();
			p++) 
		(*p)->EnableSequencerReadout();
}

//----------------------------------------
void ECROC::DisableSequencerReadout()
{
	for (std::vector<EChannels*>::iterator p=ECROCChannels.begin();
			p!=ECROCChannels.end();
			p++) 
		(*p)->DisableSequencerReadout();
}

//----------------------------------------
void ECROC::SendSoftwareRDFE()
{
  unsigned char command[] = {0x1F};
  int error = WriteCycle(1, command, rdfePulseCommandAddress, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Failure writing to CROC Software RDFE Register!");
}

//----------------------------------------
void ECROC::WaitForSequencerReadoutCompletion()
{
	for (std::vector<EChannels*>::iterator p=ECROCChannels.begin();
			p!=ECROCChannels.end();
			p++) 
		(*p)->WaitForSequencerReadoutCompletion();
}

//----------------------------------------
void ECROC::Initialize()
{
  ECROCLog.infoStream() << "Initializing ECROC 0x" << std::hex << this->address;
}

#endif
