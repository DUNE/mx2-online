#ifndef crim_cpp
#define crim_cpp

#include "crim.h"
#include <iostream>

/*********************************************************************************
* Class for creating Chain Read-Out Controller Interfact Module objects for 
* use with the MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
**********************************************************************************/

/*! mask constants for the crim */
const unsigned short crim::TimingSetupRegisterModeMask = 0xF000;
unsigned short const crim::TimingSetupRegisterFrequencyMask = 0x0FFF;
unsigned short const crim::GateWidthRegisterMask = 0x007F;
unsigned short const crim::GateWidthRegisterEnableCNRSTMask = 0x8000;
unsigned short const crim::TCALBDelayRegisterMask = 0x03FF;
unsigned short const crim::InterruptMaskRegisterMask = 0x00FF;
unsigned short const crim::InterruptStatusRegisterMask = 0x00FF;
unsigned short const crim::ClearInterruptsRegisterMask = 0x0081;
unsigned short const crim::InterruptConfigRegisterIRQMask = 0x0007;
unsigned short const crim::InterruptConfigGlobalEnableMask = 0x0080;
unsigned short const crim::TriggerRegisterPulseMask = 0x0404;
unsigned short const crim::TCALBRegisterPulseMask = 0x0404;
unsigned short const crim::SGATERegisterStartMask = 0x0401;
unsigned short const crim::SGATERegisterStopMask = 0x0402;
unsigned short const crim::CNRSTRegisterPulseMask = 0x0202;
unsigned short const crim::CNRSTRegisterOneShotMask = 0x0808;
unsigned short const crim::ControlRegisterFETriggerMask = 0x1000;
unsigned short const crim::ControlRegisterCRCMask = 0x2000;
unsigned short const crim::ControlRegisterSendMask = 0x4000;
unsigned short const crim::ControlRegisterRetransmitMask = 0x8000;
unsigned short const crim::TimingCommandRegisterMask = 0x00FF;
unsigned short const crim::SequencerControlLatchResetMask = 0x0202;
unsigned short const crim::TimingViolationRegisterMask = 0x01FF;
unsigned short const crim::TimingViolationRegisterClearMask = 0x0101; // ?? 0x1001 in documentation
unsigned short const crim::MinosSGATELowerBitsMask = 0xFFFF;
unsigned short const crim::MinosSGATEUpperBitsMask = 0x0FFF;


crim::crim(unsigned int ca, int crimid, CVAddressModifier a, CVDataWidth w) 
{
/*! \fn
 * constructor takes the following arguments:
 * \param a:  The crim address 
 * \param b: The VME address modifier
 * \param c:  The VME data width
 */
	id = crimid;
	crimAddress = ca; //the crim address
	addressModifier = a; //the VME Address Modifier
	dataWidth = w;  //the VME Data Witdth
	crimRegisters statusRegister; //a temp for use in setting the register addresses
	irqLine = SGATEFall; //we want the interrupt to raise when the gate closes
	//NOTE:  both of these must "match" i.e. the IRQ level must be the same as
	//the configuration register level.  The BIT MASKS for these levels, however
	//are not the same!
	irqLevel = cvIRQ5; //interrupt level 5 for the CAEN interrupt handler
	interruptConfigValue = 5; //the interrupt level as stored in the interrupt configruation register
	resetInterrupts = 0x81; //the value to clear all pending interrupts

	//interrupt registers
	statusRegister = crimInterruptStatus;
	interruptStatusRegister = crimAddress+(unsigned int) statusRegister;
	statusRegister = crimInterruptConfig;
	interruptConfig = crimAddress+(unsigned int) statusRegister;
	statusRegister = crimClearInterrupts;
	interruptsClear = crimAddress+(unsigned int) statusRegister;
	statusRegister = crimInterruptMask;
	interruptAddress = crimAddress+(unsigned int) statusRegister;

	//timing registers
	statusRegister = crimTimingSetup;
	timingRegister = crimAddress+(unsigned int) statusRegister;
	statusRegister = SGATEWidth;
	sGateRegister = crimAddress+(unsigned int) statusRegister;
	statusRegister = TCALBDelay;
	tCalbRegister = crimAddress+(unsigned int) statusRegister;
	statusRegister = CNRSTPulse;
	cnrstRegister = crimAddress+(unsigned int) statusRegister;

	/* the control register */
	statusRegister = crimControl;
	controlRegisterAddress = crimAddress + (unsigned int)statusRegister;
	statusRegister = crimStatus;
	statusRegisterAddress = crimAddress + (unsigned int)statusRegister;
	statusRegister = crimClearStatus;
	clearStatusRegister = crimAddress + (unsigned int)statusRegister;

	//register value for control register (DAQ Mode control)
	controlRegister = ControlRegisterCRCMask | ControlRegisterSendMask 
		& ~ControlRegisterRetransmitMask; //set crc & send to true and retransmit to false
}


void crim::SetFrequency(crimTimingFrequencies a) 
{
/*! \fn 
 * Function to set the timing frequency on a CRIM
 *
 * \param a a timing frequency bitmask
 *
 */
	//set frequency suitable for internal
	//this is sent to the timing register
	timingSetup = ((unsigned short)a) & TimingSetupRegisterFrequencyMask;
}


void crim::SetTiming(unsigned short a) 
{
/*! \fn 
 * Function to set the timing input on a CRIM
 *
 * \param a a timing input bitmask
 *
 */
	//set frequency suitable for internal or external
	//this is sent to the timing register
	timingSetup |= a & TimingSetupRegisterModeMask;
}


void crim::SetGateWidth(unsigned short a) 
{
/*! \fn
 *
 * set gate with value, just an assignment
 * \param a the gate width value 
 */
	sGateWidth = a & GateWidthRegisterMask;
}


void crim::SetTcalbPulse(unsigned short a) 
{
/*! \fn
 *
 * set pulse delay, just an assignment
 * \param a the calibration pulse delay time 
 */
	tCalbPulse = a & TCALBDelayRegisterMask;
}


void crim::SetCRCEnable(bool a) 
{
/*! \fn
 *
 * this filps the crc enable bit(s) on the control register value
 *
 *  \param a status bit to decide how to set the bit
 */
	if (a) {
		controlRegister |= ControlRegisterCRCMask;
	} else {
		controlRegister &= ~ControlRegisterCRCMask;
	}
}


void crim::SetSendEnable(bool a) 
{
/*! \fn
 *
 * this filps the send enable bit(s) on the control register value
 *
 *  \param a status bit to decide how to set the bit
 */
	if (a) {
		controlRegister |= ControlRegisterSendMask;
	} else {
		controlRegister &= ~ControlRegisterSendMask;
	}
}


void crim::SetReTransmitEnable(bool a) 
{
/*! \fn
 *
 * this filps the transmit enable bit(s) on the control register value
 *
 *  \param a status bit to decide how to set th bit
 */
	if (a) {
		controlRegister |= ControlRegisterRetransmitMask;
	} else {
		controlRegister &= ~ControlRegisterRetransmitMask;
	}
}


void crim::SetSoftTrig(unsigned short a) 
{
}


void crim::SetSoftTcalb(unsigned short a) 
{
}


void crim::SetSoftSGate(unsigned short a) 
{
}


void crim::SetSoftCNRST(unsigned short a) 
{
/*! \fn set CNRST for one-shot mode
 *
 * \param a value to CNRST register
 *
 */
	//this is only set up for "one shot" mode at this time.
	//Of course, you are free to change this at any time.
	softCNRST = a & CNRSTRegisterOneShotMask;  
}


crimTimingFrequencies crim::GetFrequency() 
{
	unsigned short frequency = timingSetup & TimingSetupRegisterFrequencyMask;
	return (crimTimingFrequencies)frequency;
}


unsigned short crim::GetTiming() 
{
	unsigned short timing = (timingSetup & TimingSetupRegisterModeMask) >> 11;
	return timing;
}


unsigned short crim::GetSoftTrig() 
{
	return 1;
}


unsigned short crim::GetSoftTcalb() 
{
	return 1;
}


unsigned short crim::GetSoftSGate() 
{
	return 1;
}


void crim::SetupOneShot() 
{
/*! \fn
 * Set the register values (but does not send them) for one-shot trigger mode
 *
 */
	SetInterruptMask(); //set the interupt mask using that value
	SetFrequency(ZeroFreq); //we want the frequency bits set to zero for one-shot mode (when in internal timing) 
	SetTiming(0x4000);  //set timing to internal (mildly redundent with frequency set
	SetGateWidth(0x007F); //set gate width  127
	SetTcalbPulse(0x03FF);  //set the tcalb pulse delay 1023
	SetSoftCNRST(0x0808); //set the cnrst register value to trigger the single shot
}

#endif
