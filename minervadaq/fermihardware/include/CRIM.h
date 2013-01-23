#ifndef CRIM_h
#define CRIM_h

/* system specific headers go here */
#include <fstream>

/* CAEN headers go here */
#include "CAENVMEtypes.h"

/* custom headers go here */
#include "MinervaDAQtypes.h"
#include "ReadoutTypes.h"
#include "VMECommunicator.h"


/*********************************************************************************
 * Class for creating Chain Read-Out Controller Interfact Module objects for 
 * use with the MINERvA data acquisition system and associated software projects.
 *
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

/*! \class CRIM
 *
 * \brief The class for CRIM objects.
 *
 * This class contains all of the data associated with a CRIM object.  This includes
 * the register addresses and interrupt information .
 */

class CRIM : public VMECommunicator {

  private:
    /* We will always use the first CRIM in the vector of CRIMs held by the 
       DAQ worker classes as the master CRIM. */
    log4cpp::Appender* CRIMAppender;

    CVIRQLevels irqLevel;                /*!<the interrupt priority level */
    CRIMInterrupts irqLine;              /*!<the interrupt to be monitored */
    unsigned short interruptValue;       /*!<the bitmask for the interrupt line */
    unsigned short interruptStatus;      /*!<the status of the interrupts */
    unsigned short resetInterrupts;      /*!<the value to be sent to the clear interrupts register on the CRIM */
    unsigned short interruptConfigValue; /*!<the configuration value sent to the
                                           configuration register (must match the 
                                           IRQLevel for the CAEN interrupt handler:
                                           i.e. if this value is 5 (the default)
                                           the IRQLevel for the CAEN must be IRQ5. */

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

    /*! cosmic mode control registers. */
    unsigned int sequencerResetRegister;

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

    void logRunningMode( RunningModes runningMode );

  public:

    CRIM( unsigned int address, log4cpp::Appender* appender, Controller* controller ); 
    ~CRIM() { }; 

    void Initialize( RunningModes runningMode );

    unsigned int GetAddress();
    unsigned short GetStatus();

    void SetupTiming( CRIMTimingModes timingMode, CRIMTimingFrequencies frequency ); 
    void SetupGateWidth( unsigned short tcalbEnable, unsigned short gateWidth, unsigned short sequencerEnable ); 
    void SetupTCALBPulse( unsigned short pulseDelay );

    /*! interrupt stuff */
    void inline SetIRQLevel(CVIRQLevels a) {irqLevel = a;};  //sets the IRQ Level (CAEN)
    void inline SetIRQLine(CRIMInterrupts a) {irqLine = a;}; //sets the IRQ Level (CAEN)
    CVIRQLevels inline GetIRQLevel() {return irqLevel;}; //returns the irq level (CAEN)
    unsigned char inline GetIRQLine() { return (unsigned char)irqLine; };

    void inline SetInterruptMask() {
      interruptValue = ((unsigned short)irqLine & InterruptMaskRegisterMask);
    }; 

    void inline SetInterruptStatus(unsigned short a) {
      interruptStatus = a & InterruptStatusRegisterMask;
    }; 

    void inline SetInterruptConfigValue(unsigned short a) {
      interruptConfigValue = a;
    }; 

    void inline SetInterruptGlobalEnable(bool a) {
      interruptConfigValue |= ((a << 7) & InterruptConfigGlobalEnableMask);
    }; 

    unsigned short inline GetInterruptMask() {
      return interruptValue;
    }; 

    unsigned int inline GetInterruptMaskAddress() {
      return interruptAddress;
    }; 

    unsigned short inline GetInterruptStatus() {
      return (interruptStatus & InterruptStatusRegisterMask);
    }; 

    unsigned short inline GetInterruptGlobalEnable() {
      return interruptConfigValue & InterruptConfigGlobalEnableMask;
    }; 

    unsigned short inline GetInterruptConfig() {
      return interruptConfigValue;
    }; 

    unsigned int inline GetInterruptsConfigAddress() {
      return interruptConfig;
    }; 

    unsigned int inline GetInterruptStatusAddress() {
      return interruptStatusRegister;
    }; 

    unsigned short inline GetClearInterrupts() {
      return resetInterrupts;
    }; 

    unsigned int inline GetClearInterruptsAddress() {
      return interruptsClear;
    };

    unsigned int inline GetGateTimeWordLowAddress() { 
      return gateTimeWordLowAddress;
    }; 
    unsigned int inline GetGateTimeWordHighAddress() {
      return gateTimeWordHighAddress;
    }; 

    unsigned int inline GetSequencerResetRegister() {
      return sequencerResetRegister;
    } 


    /*! control stuff */
    void SetCRCEnable(bool a);
    void SetSendEnable(bool a);
    void SetReTransmitEnable(bool a);
    unsigned short inline GetControlRegister() {return controlRegisterAddress;};
    long_m inline GetStatusRegisterAddress() {return statusRegisterAddress;}; 
    unsigned int inline GetClearRegisterAddress() {return clearStatusRegister;};
};

#endif
