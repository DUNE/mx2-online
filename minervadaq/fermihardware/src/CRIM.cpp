#ifndef CRIM_cpp
#define CRIM_cpp

#include "CRIM.h"
#include <iostream>

/*********************************************************************************
* Class for creating Chain Read-Out Controller Interfact Module objects for 
* use with the MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
**********************************************************************************/

/*! mask constants for the CRIM */
unsigned short const CRIM::TimingSetupRegisterModeMask      = 0xF000;
unsigned short const CRIM::TimingSetupRegisterFrequencyMask = 0x0FFF;
unsigned short const CRIM::GateWidthRegisterMask            = 0x007F;
unsigned short const CRIM::GateWidthRegisterEnableCNRSTMask = 0x8000;
unsigned short const CRIM::TCALBDelayRegisterMask           = 0x03FF;
unsigned short const CRIM::InterruptMaskRegisterMask        = 0x00FF;
unsigned short const CRIM::InterruptStatusRegisterMask      = 0x00FF;
unsigned short const CRIM::ClearInterruptsRegisterMask      = 0x0081;
unsigned short const CRIM::InterruptConfigRegisterIRQMask   = 0x0007;
unsigned short const CRIM::InterruptConfigGlobalEnableMask  = 0x0080;
unsigned short const CRIM::TriggerRegisterPulseMask         = 0x0404;
unsigned short const CRIM::TCALBRegisterPulseMask           = 0x0404;
unsigned short const CRIM::SGATERegisterStartMask           = 0x0401;
unsigned short const CRIM::SGATERegisterStopMask            = 0x0402;
unsigned short const CRIM::CNRSTRegisterPulseMask           = 0x0202;
unsigned short const CRIM::CNRSTRegisterOneShotMask         = 0x0808;
unsigned short const CRIM::ControlRegisterFETriggerMask     = 0x1000;
unsigned short const CRIM::ControlRegisterCRCMask           = 0x2000;
unsigned short const CRIM::ControlRegisterSendMask          = 0x4000;
unsigned short const CRIM::ControlRegisterRetransmitMask    = 0x8000;
unsigned short const CRIM::TimingCommandRegisterMask        = 0x00FF;
unsigned short const CRIM::SequencerControlLatchResetMask   = 0x0202;
unsigned short const CRIM::TimingViolationRegisterMask      = 0x01FF;
unsigned short const CRIM::TimingViolationRegisterClearMask = 0x0101; 
unsigned short const CRIM::MinosSGATELowerBitsMask          = 0xFFFF;
unsigned short const CRIM::MinosSGATEUpperBitsMask          = 0x0FFF;

const unsigned short CRIM::softTrigger    = 0x0404;
const unsigned short CRIM::softTCALB      = 0x0404;
const unsigned short CRIM::softSGATEstart = 0x0401;
const unsigned short CRIM::softSGATEstop  = 0x0402;
const unsigned short CRIM::softCNRST      = 0x0202;
const unsigned short CRIM::softCNRSTseq   = 0x0808;


CRIM::CRIM(unsigned int ca, int CRIMid, CVAddressModifier a, CVDataWidth w) 
{
/*! \fn
 * constructor takes the following arguments:
 * \param a:  The CRIM address 
 * \param b: The VME address modifier
 * \param c:  The VME data width
 */
	id              = CRIMid; // internal tracking value
	CRIMAddress     = ca; // the CRIM address
	addressModifier = a;  // the VME Address Modifier
	dataWidth       = w;  // the VME Data Witdth
	irqLine = SGATEFall;  // default, but configurable
	// NOTE: The IRQ level must be the same as the configuration register level.  
	// The BIT MASKS for these levels, however are not the same!
	irqLevel             = cvIRQ5; // interrupt level 5 for the CAEN interrupt handler
	interruptConfigValue = 5;    // the interrupt level stored in the interrupt config register
	resetInterrupts      = 0x81; // the value to clear all pending interrupts

	CRIMRegisters statusRegister; // a temp for use in setting the register addresses

	// interrupt registers
	statusRegister          = CRIMInterruptStatus;
	interruptStatusRegister = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister          = CRIMInterruptConfig;
	interruptConfig         = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister          = CRIMClearInterrupts;
	interruptsClear         = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister          = CRIMInterruptMask;
	interruptAddress        = CRIMAddress + (unsigned int)statusRegister;

	// timing registers
	statusRegister      = CRIMTimingSetup;
	timingRegister      = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister      = CRIMSGATEWidth;
	SGATEWidthRegister  = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister      = CRIMTCALBDelay;
	TCALBDelayRegister  = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister          = CRIMSoftwareTrigger;
	softwareTriggerRegister = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister          = CRIMSoftwareTCALB;
	softwareTCALBRegister   = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister          = CRIMSoftwareSGATE;
	softwareSGATERegister   = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister          = CRIMSoftwareCNRST;
	softwareCNRSTRegister   = CRIMAddress + (unsigned int)statusRegister;

	// control registers
	statusRegister         = CRIMControl;
	controlRegisterAddress = CRIMAddress + (unsigned int)statusRegister;
	//
	statusRegister         = CRIMStatus;
	statusRegisterAddress  = CRIMAddress + (unsigned int)statusRegister;

	//
	statusRegister         = CRIMClearStatus;
	clearStatusRegister    = CRIMAddress + (unsigned int)statusRegister;

	// External data registers
	statusRegister          = CRIMGateTimeWordLow;
	gateTimeWordLowAddress  = CRIMAddress + (unsigned int)statusRegister;
	statusRegister          = CRIMGateTimeWordHigh;
	gateTimeWordHighAddress = CRIMAddress + (unsigned int)statusRegister;

	// Cosmic mode control (only meaningful for v5 CRIM firmware)
	statusRegister		= CRIMSequencerControlLatch;
	sequencerResetRegister  = CRIMAddress + (unsigned int)statusRegister;

	//register value for control register (DAQ Mode control)
	controlRegister = ControlRegisterCRCMask | ControlRegisterSendMask 
		& ~ControlRegisterRetransmitMask; //set crc & send to true and retransmit to false
}


void CRIM::SetCRCEnable(bool a) 
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


void CRIM::SetSendEnable(bool a) 
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


void CRIM::SetReTransmitEnable(bool a) 
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



#endif
