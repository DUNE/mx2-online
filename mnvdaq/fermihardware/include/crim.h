#ifndef crim_h
#define crim_h

/* system specific headers go here */
#include <fstream>

/* CAEN headers go here */
#include "CAENVMEtypes.h"

/* custom headers go here */
#include "MinervaDAQtypes.h"


/*********************************************************************************
* Class for creating Chain Read-Out Controller Interfact Module objects for 
* use with the MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
**********************************************************************************/

/*! \class crim
 *
 * \brief The class for CRIM objects.
 *
 * This class contains all of the data associated with a CRIM object.  This includes
 * the register addresses and interrupt information .
 *
 */

class crim {
	private:
		int id; /*!<an id number for a crim */
		unsigned int crimAddress;  /*!<the on-board address for the crim module being created */
		CVAddressModifier addressModifier; /*!<the address width */
		CVDataWidth dataWidth; /*!<the data transfer width */
		CVIRQLevels irqLevel; /*!<the interrupt priority level */
		crimInterrupts irqLine; /*!<the interrupt to be monitored */
		unsigned short interruptValue; /*!<the bitmask for the interrupt line */
		unsigned short interruptStatus; /*!<the status of the interrupts */
		unsigned short resetInterrupts; /*!<the value to be sent to the 
		clear interrupts register on the crim */
		unsigned short interruptConfigValue; /*!<the configuration value sent to the
		configuration register (must match the 
		IRQLevel for the CAEN interrupt handler:
		i.e. if this value is 5 (the default)
		the IRQLevel for the CAEN must be IRQ5. */

		/*!register value needed to control the behavior of the crim */
		unsigned short controlRegister; 

		/*! interrupt register addresses
		* interruptAddress:  the address of the Interrupt Mask Register, i.e. which line to monitor
		* interruptStatusRegister:  the address of the register which reports the interrupt status
		* interruptsClear: the address to which a "clear" is sent to acknowledge pending interrupts
		* interruptConfig:  the address to the register which sets the interrupt priority levels
		*/
		unsigned int interruptAddress, interruptStatusRegister, interruptsClear, interruptConfig;

		/*! timing & software register addresses */
		unsigned int timingRegister, SGATEWidthRegister, TCALBDelayRegister, softwareTriggerRegister, 
			softwareTCALBRegister, softwareSGATERegister, softwareCNRSTRegister;

		/*!control & status register addresses */
		unsigned int controlRegisterAddress;
		unsigned int statusRegisterAddress;
		unsigned int clearStatusRegister;

		/*! "external" data register addresses */
		unsigned int gateTimeWordLowAddress;
		unsigned int gateTimeWordHighAddress;

		/*! variables for holding information about the setup of the crim for use. */
		unsigned short timingSetup, gateWidthSetup, TCALBDelaySetup;
	
		/*! cosmic mode control registers. */
		unsigned int sequencerResetRegister;
	
		unsigned short crimStatusValue;

		/*!  these are the various masks that are used to set up  running conditions */
		static unsigned short const TimingSetupRegisterModeMask;
		static unsigned short const TimingSetupRegisterFrequencyMask;
		static unsigned short const GateWidthRegisterMask;
		static unsigned short const GateWidthRegisterEnableCNRSTMask;
		static unsigned short const TCALBDelayRegisterMask;
		static unsigned short const InterruptMaskRegisterMask;
		static unsigned short const InterruptStatusRegisterMask;
		static unsigned short const ClearInterruptsRegisterMask;
		static unsigned short const InterruptConfigRegisterIRQMask;
		static unsigned short const InterruptConfigGlobalEnableMask;
		static unsigned short const TriggerRegisterPulseMask;
		static unsigned short const TCALBRegisterPulseMask;
		static unsigned short const SGATERegisterStartMask;
		static unsigned short const SGATERegisterStopMask;
		static unsigned short const CNRSTRegisterPulseMask;
		static unsigned short const CNRSTRegisterOneShotMask;
		static unsigned short const ControlRegisterFETriggerMask;
		static unsigned short const ControlRegisterCRCMask;
		static unsigned short const ControlRegisterSendMask;
		static unsigned short const ControlRegisterRetransmitMask;
		static unsigned short const TimingCommandRegisterMask;
		static unsigned short const SequencerControlLatchResetMask; // Must write to re-enable ext. trigger
		static unsigned short const TimingViolationRegisterMask;
		static unsigned short const TimingViolationRegisterClearMask; // write to clear timing violations reg.
		static unsigned short const MinosSGATELowerBitsMask;
		static unsigned short const MinosSGATEUpperBitsMask;

		/*! execution values */
		static const unsigned short softTrigger, softTCALB, softSGATEstart, 
			softSGATEstop, softCNRST, softCNRSTseq;

	public:
		/*! The default constructor */
		crim() { };
		/*! The specialized constructor */
		crim(unsigned int, int, CVAddressModifier, CVDataWidth); // constructor
		/*! The default destructor */
		~crim() { }; //destructor


		/*! get & set functions for information about the crim */
		CVAddressModifier inline GetAddressModifier() {return addressModifier;};
		CVDataWidth inline GetDataWidth() {return dataWidth;};
		unsigned int inline GetAddress() {return crimAddress;}; 
		int inline GetCrimID() {return id;};
		unsigned int inline GetCrimAddress() {return crimAddress;};

		// setup the timing register - arguments are the timing mode and frequency
		void SetupTiming(crimTimingModes a, crimTimingFrequencies b) {
			timingSetup = ( a & TimingSetupRegisterModeMask ) | 
				(b & TimingSetupRegisterFrequencyMask);
#if DEBUG_CRIM
			printf("  CRIM timingSetup = 0x%04X\n",timingSetup);
			printf("       timingMode  = 0x%04X\n",a);
			printf("       frequency   = 0x%04X\n",b);
#endif
		}; 
		// setup gate width register - arguments are tcalb enable bit and gate width
		//  tcalb enable - a
		//  gate width   - b
		void SetupGateWidth(unsigned short a, unsigned short b) {
			gateWidthSetup = ((a & 0x1)<<15) | (b & GateWidthRegisterMask);
		};  
		// setup gate width register - arguments are tcalb enable bit, gate width, and sequencer control enable bit
		//  tcalb enable     - a
		//  gate width       - b
		//  sequencer enable - c 
		void SetupGateWidth(unsigned short a, unsigned short b, unsigned short c) {
			gateWidthSetup = ((a & 0x1)<<15) | ((c & 0x1)<<10) | (b & GateWidthRegisterMask);
		};  
		// set pluse delay - argument is the pulse delay
		void SetupTCALBPulse(unsigned short a) {
			TCALBDelaySetup = a & TCALBDelayRegisterMask;
		}; 

		// functions which return the timing/trigger info
		unsigned short GetGateWidthSetup() {return gateWidthSetup;};
		unsigned short GetTCALBPulse() {return TCALBDelaySetup;};
		unsigned short GetTimingSetup() {return timingSetup;};
		unsigned short GetGateWidth() {return (gateWidthSetup & GateWidthRegisterMask);};
		unsigned short GetGateTCALBEnable() {return ((gateWidthSetup & 0x8000)>>15);};
		unsigned short GetTiming() {return ((timingSetup & TimingSetupRegisterModeMask)>>12);}; 
		unsigned short GetSoftTrig() {return softTrigger;};
		unsigned short GetSoftTCALB() {return softTCALB;};
		unsigned short GetSoftSGATEStart() {return softSGATEstart;};
		unsigned short GetSoftSGATEStop() {return softSGATEstop;};
		unsigned short GetSoftCNRST() {return softCNRST;};
		unsigned short GetSoftCNRSTSeq() {return softCNRSTseq;};

		unsigned int GetTimingRegister() {return timingRegister;};
		unsigned int GetSGATEWidthRegister() {return SGATEWidthRegister;};
		unsigned int GetTCALBRegister() {return TCALBDelayRegister;};
		unsigned int GetSoftTriggerRegister() {return softwareTriggerRegister;};
		unsigned int GetSoftTCALBRegister() {return softwareTCALBRegister;};
		unsigned int GetSoftSGATERegister() {return softwareSGATERegister;};
		unsigned int GetSoftCNRSTRegister() {return softwareCNRSTRegister;};

		/*! interrupt stuff */
		void inline SetIRQLevel(CVIRQLevels a) {irqLevel = a;};  //sets the IRQ Level (CAEN)
		void inline SetIRQLine(crimInterrupts a) {irqLine = a;}; //sets the IRQ Level (CAEN)
		CVIRQLevels inline GetIRQLevel() {return irqLevel;}; //returns the irq level (CAEN)
		unsigned char inline GetIRQLine() { return (unsigned char)irqLine; };

		void inline SetInterruptMask() {
			interruptValue = ((unsigned short)irqLine & InterruptMaskRegisterMask);
		}; //sets the interrupt value bitmask

		void inline SetInterruptStatus(unsigned short a) {
			interruptStatus = a & InterruptStatusRegisterMask;
		}; //stores the interrupt status

		void inline SetInterruptConfigValue(unsigned short a) {
			interruptConfigValue = a;
		}; //interrupt level - must match the IRQ value!
		
		void inline SetInterruptGlobalEnable(bool a) {
			interruptConfigValue |= ((a << 7) & InterruptConfigGlobalEnableMask);
		}; //sets the global enable bit

		unsigned short inline GetInterruptMask() {
			return interruptValue;
		}; //returns the interrupt bitmask
		
		unsigned int inline GetInterruptMaskAddress() {
			return interruptAddress;
		}; //return the register address to set the interrupt bitmask
		
		unsigned short inline GetInterruptStatus() {
			return (interruptStatus & InterruptStatusRegisterMask);
		}; //returns the interrupt status

		unsigned short inline GetInterruptGlobalEnable() {
			return interruptConfigValue & InterruptConfigGlobalEnableMask;
		}; //returns the global enable status
		
		unsigned short inline GetInterruptConfig() {
			return interruptConfigValue;
		}; //returns the value of the interrupt level & enable bit
		
		unsigned int inline GetInterruptsConfigAddress() {
			return interruptConfig;
		}; //returns the interrupt config address

		unsigned int inline GetInterruptStatusAddress() {
			return interruptStatusRegister;
		}; // Return the interrupt status register address. 

		unsigned short inline GetClearInterrupts() {
			return resetInterrupts;
		}; //returns the reset interrupt bitmask

		unsigned int inline GetClearInterruptsAddress() {
			return interruptsClear;
		}; //returns the clear interrupts register address

		unsigned int inline GetGateTimeWordLowAddress() { 
			return gateTimeWordLowAddress;
		}; // returns the least significant 16 bits of the MINOS GATE time address
                unsigned int inline GetGateTimeWordHighAddress() {
			return gateTimeWordHighAddress;
		}; // returns the most significant 16 bits of the MINOS GATE time address

		unsigned int inline GetSequencerResetRegister() {
			return sequencerResetRegister;
		} // returns the sequencer reset register


		/*! control stuff */
		void SetCRCEnable(bool a);
		void SetSendEnable(bool a);
		void SetReTransmitEnable(bool a);
		unsigned short inline GetStatus() {return crimStatusValue;};
		unsigned short inline GetControlRegister() {return controlRegisterAddress;};
		long_m inline GetStatusRegisterAddress() {return statusRegisterAddress;}; 
		unsigned int inline GetClearRegisterAddress() {return clearStatusRegister;};
};

#endif
