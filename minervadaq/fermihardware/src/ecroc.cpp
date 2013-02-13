#ifndef ecroc_cpp
#define ecroc_cpp

#include "ecroc.h"

/*********************************************************************************
* Class for creating CROC-E objects for use with the MINERvA data acquisition 
* system and associated software projects.
*
* Gabriel Perdue, The University of Rochester
**********************************************************************************/

// log4cpp category hierarchy.
log4cpp::Category& ecrocLog = log4cpp::Category::getInstance(std::string("ecroc"));

//----------------------------------------
ecroc::ecroc(unsigned int address, int ecrocid ) 
{
	vmeAddress       = address;
	id               = ecrocid;
	addressModifier  = cvA32_U_DATA;
	dataWidth        = cvD32;  // not clear we have one data width - is cvD16 for register reads
	dataWidthSwapped = cvD16_swapped;

	timingSetupAddress           = address + ecrocTimingSetup;
	resetAndTestPulseMaskAddress = address + ecrocResetAndTestPulseMask;
	channelResetAddress          = address + ecrocChannelReset;
	fastCommandAddress           = address + ecrocFastCommand;
	testPulseAddress             = address + ecrocTestPulse;
	rdfePulseDelayAddress        = address + ecrocRdfePulseDelay;
	rdfePulseCommandAddress      = address + ecrocRdfePulseCommand;

	SetupChannels(); 
	InitializeRegisters( crocExternal, (short unsigned int)0x0, (short unsigned int)0x0 );
}

//----------------------------------------
ecroc::~ecroc() 
{ 
	for (std::list<echannels*>::iterator p=ecrocChannels.begin();
			p!=ecrocChannels.end();
			p++) 
		delete (*p);
	ecrocChannels.clear();
}

//----------------------------------------
unsigned int ecroc::GetAddress() 
{
	return vmeAddress;
}

//----------------------------------------
int ecroc::GetCrocID() 
{
	return id;
}

//----------------------------------------
CVAddressModifier ecroc::GetAddressModifier() 
{
	return addressModifier;
}

//----------------------------------------
CVDataWidth ecroc::GetDataWidth() 
{
	return dataWidth;
}

//----------------------------------------
CVDataWidth ecroc::GetDataWidthSwapped() 
{
	return dataWidthSwapped;
}

//----------------------------------------
void ecroc::SetupChannels() 
{
	for ( unsigned int i=0; i<4; ++i ) { 
		echannels *tmp = new echannels( vmeAddress, i );
		ecrocChannels.push_back( tmp ); 
	}
}

//----------------------------------------
echannels* ecroc::GetChannel( unsigned int i ) { 
	echannels *tmp=0; 
	for (std::list<echannels*>::iterator p=ecrocChannels.begin(); 
			p!=ecrocChannels.end(); 
			++p) { 
		if ( i == (*p)->GetChannelNumber() ) tmp = (*p); 
	}
	return tmp; 
}

//----------------------------------------
std::list<echannels*>* ecroc::GetChannelsList() 
{
	return &ecrocChannels;
}

//----------------------------------------
unsigned int ecroc::GetTimingSetupAddress()
{
	return timingSetupAddress;
}

//----------------------------------------
unsigned short ecroc::GetTimingRegisterMessage() 
{
	return timingRegisterMessage;
}

//----------------------------------------
void ecroc::SetTimingRegisterMessage( crocClockModes clockMode, 
	unsigned short testPulseDelayEnabled, 
	unsigned short testPulseDelayValue )
{
	timingRegisterMessage  = clockMode;   	                    // the clock mode  (0x8000 is the bitmask for bit 15 high)
	timingRegisterMessage |= (testPulseDelayEnabled & 0x1)<<12; // test pulse delay enable bit (bit 12)
	timingRegisterMessage |= testPulseDelayValue & 0x3FF;       // test pules delay values (in 18.9 ns units) bits 0-9
	timingRegisterMessage &= 0xFFFF;
	ecrocLog.debugStream() << "    Timing Register = " << timingRegisterMessage; // TODO: hex!
}

//----------------------------------------
void ecroc::SetResetAndTestPulseRegisterMessage( unsigned short resetEnable, unsigned short testPulseEnable )
{
	resetAndTestPulseMaskRegisterMessage  = (resetEnable & 0x1)<<8;  //the reset enable bit is 8
	resetAndTestPulseMaskRegisterMessage |= (testPulseEnable & 0x1); //the test pulse enable bit is 0
}

//----------------------------------------
unsigned int ecroc::GetFastCommandAddress()
{
	return fastCommandAddress;
}

//----------------------------------------
unsigned short ecroc::GetFastCommandRegisterMessage()
{
	return fastCommandRegisterMessage;
}

//----------------------------------------
void ecroc::SetFastCommandRegisterMessage( unsigned short value ) 
{
	fastCommandRegisterMessage = value & 0xFF;
}

//----------------------------------------
void ecroc::InitializeRegisters( crocClockModes clockMode, 
		unsigned short testPulseDelayValue,
		unsigned short testPulseDelayEnabled ) 
{
	SetTimingRegisterMessage( clockMode, testPulseDelayEnabled, testPulseDelayValue );
	SetResetAndTestPulseRegisterMessage( 0, 0 );
}





#endif
