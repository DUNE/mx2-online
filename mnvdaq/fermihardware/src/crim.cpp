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
unsigned short const crim::TimingSetupRegisterModeMask      = 0xF000;
unsigned short const crim::TimingSetupRegisterFrequencyMask = 0x0FFF;
unsigned short const crim::GateWidthRegisterMask            = 0x007F;
unsigned short const crim::GateWidthRegisterEnableCNRSTMask = 0x8000;
unsigned short const crim::TCALBDelayRegisterMask           = 0x03FF;
unsigned short const crim::InterruptMaskRegisterMask        = 0x00FF;
unsigned short const crim::InterruptStatusRegisterMask      = 0x00FF;
unsigned short const crim::ClearInterruptsRegisterMask      = 0x0081;
unsigned short const crim::InterruptConfigRegisterIRQMask   = 0x0007;
unsigned short const crim::InterruptConfigGlobalEnableMask  = 0x0080;
unsigned short const crim::TriggerRegisterPulseMask         = 0x0404;
unsigned short const crim::TCALBRegisterPulseMask           = 0x0404;
unsigned short const crim::SGATERegisterStartMask           = 0x0401;
unsigned short const crim::SGATERegisterStopMask            = 0x0402;
unsigned short const crim::CNRSTRegisterPulseMask           = 0x0202;
unsigned short const crim::CNRSTRegisterOneShotMask         = 0x0808;
unsigned short const crim::ControlRegisterFETriggerMask     = 0x1000;
unsigned short const crim::ControlRegisterCRCMask           = 0x2000;
unsigned short const crim::ControlRegisterSendMask          = 0x4000;
unsigned short const crim::ControlRegisterRetransmitMask    = 0x8000;
unsigned short const crim::TimingCommandRegisterMask        = 0x00FF;
unsigned short const crim::SequencerControlLatchResetMask   = 0x0202;
unsigned short const crim::TimingViolationRegisterMask      = 0x01FF;
unsigned short const crim::TimingViolationRegisterClearMask = 0x0101; 
unsigned short const crim::MinosSGATELowerBitsMask          = 0xFFFF;
unsigned short const crim::MinosSGATEUpperBitsMask          = 0x0FFF;

const unsigned short crim::softTrigger    = 0x0404;
const unsigned short crim::softTCALB      = 0x0404;
const unsigned short crim::softSGATEstart = 0x0401;
const unsigned short crim::softSGATEstop  = 0x0402;
const unsigned short crim::softCNRST      = 0x0202;
const unsigned short crim::softCNRSTseq   = 0x0808;


crim::crim(unsigned int ca, int crimid, CVAddressModifier a, CVDataWidth w) 
{
/*! \fn
 * constructor takes the following arguments:
 * \param a:  The crim address 
 * \param b: The VME address modifier
 * \param c:  The VME data width
 */
	id              = crimid; // internal tracking value
	crimAddress     = ca; // the crim address
	addressModifier = a;  // the VME Address Modifier
	dataWidth       = w;  // the VME Data Witdth
	irqLine = SGATEFall; // TODO - add irqLine configuration options.
	// NOTE: The IRQ level must be the same as the configuration register level.  
	// The BIT MASKS for these levels, however are not the same!
	irqLevel             = cvIRQ5; // interrupt level 5 for the CAEN interrupt handler
	interruptConfigValue = 5;    // the interrupt level stored in the interrupt config register
	resetInterrupts      = 0x81; // the value to clear all pending interrupts

	crimRegisters statusRegister; // a temp for use in setting the register addresses

	// interrupt registers
	statusRegister          = crimInterruptStatus;
	interruptStatusRegister = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister          = crimInterruptConfig;
	interruptConfig         = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister          = crimClearInterrupts;
	interruptsClear         = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister          = crimInterruptMask;
	interruptAddress        = crimAddress + (unsigned int)statusRegister;

	// timing registers
	statusRegister      = crimTimingSetup;
	timingRegister      = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister      = crimSGATEWidth;
	SGATEWidthRegister  = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister      = crimTCALBDelay;
	TCALBDelayRegister  = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister          = crimSoftwareTrigger;
	softwareTriggerRegister = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister          = crimSoftwareTCALB;
	softwareTCALBRegister   = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister          = crimSoftwareSGATE;
	softwareSGATERegister   = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister          = crimSoftwareCNRST;
	softwareCNRSTRegister   = crimAddress + (unsigned int)statusRegister;

	// control registers
	statusRegister         = crimControl;
	controlRegisterAddress = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister         = crimStatus;
	statusRegisterAddress  = crimAddress + (unsigned int)statusRegister;
	//
	statusRegister         = crimClearStatus;
	clearStatusRegister    = crimAddress + (unsigned int)statusRegister;

	//register value for control register (DAQ Mode control)
	controlRegister = ControlRegisterCRCMask | ControlRegisterSendMask 
		& ~ControlRegisterRetransmitMask; //set crc & send to true and retransmit to false
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


// TODO - This function is now basically obsolete?... Should probably remove it.
void crim::SetupOneShot() 
{
/*! \fn
 * Set the register values (but does not send them) for one-shot trigger mode
 */
	SetInterruptMask();     //set the interupt mask using that value
	SetupTiming(crimInternal, ZeroFreq);
	SetupGateWidth(0x0001, 0x007F); // enable tcalb, set gate width  127
	SetupTCALBPulse(0x03FF);  //set the tcalb pulse delay 1023
}

#endif
