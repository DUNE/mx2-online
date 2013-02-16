#ifndef CRIM_h
#define CRIM_h

/* system specific headers go here */
#include <fstream>
#include <sys/time.h>
#include <signal.h>   // for sig_atomic_t

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

    unsigned short irqLevel;  /*!<the interrupt priority level */
    CRIMInterrupts irqLine;   /*!<the interrupt to be monitored */

    unsigned short controlRegister; 

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

    void logRunningMode( const RunningModes& runningMode ) const;
    void CAENVMEIRQEnable() const; 

    static const unsigned long long timeOutSec;

  public:

    // SGATEFall is the correct interrupt for every mode but cosmic. IRQ5 is always(?) correct...
    // For Cosmics (TestBeam) use irqLine = Trigger;  
    explicit CRIM( unsigned int address, const Controller* controller, 
       CRIMInterrupts line=SGATEFall, unsigned short level=5 ); 
    ~CRIM() { }; 

    void Initialize( RunningModes runningMode );

    const unsigned int GetAddress() const;
    unsigned short GetStatus() const;

    void SetupTiming( CRIMTimingModes timingMode, CRIMTimingFrequencies frequency ) const; 
    void SetupGateWidth( unsigned short tcalbEnable, unsigned short gateWidth, unsigned short sequencerEnable ) const; 
    void SetupTCALBPulse( unsigned short pulseDelay ) const;
    void IRQEnable() const;
    void SetupInterruptMask() const;
    unsigned short GetInterruptStatus() const;
    void ClearPendingInterrupts( unsigned short interruptStatus ) const;
    void ResetGlobalIRQEnable() const;
    void ResetSequencerLatch() const;
    int WaitOnIRQ( sig_atomic_t const & continueFlag ) const;

    unsigned short GetInterruptMask() const; 

    /*! control stuff */
    void SetCRCEnable(bool a);
    void SetSendEnable(bool a);
    void SetReTransmitEnable(bool a);
    unsigned short inline GetControlRegister() {return controlRegisterAddress;};
    long_m inline GetStatusRegisterAddress() {return statusRegisterAddress;}; 
    unsigned int inline GetClearRegisterAddress() {return clearStatusRegister;};
};

#endif