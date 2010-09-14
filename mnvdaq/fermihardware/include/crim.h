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
 * April 22, 2009
 *
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

    /*!timing register addresses (for internal mode) */
    unsigned int timingRegister, sGateRegister, tCalbRegister, cnrstRegister;

    /*!controll & status register addresses */
    unsigned int controlRegisterAddress;
    unsigned int statusRegisterAddress;
    unsigned int clearStatusRegister;

    /*!variables for holding information about the setup of the 
    *crim for use.  For the PMT Test Station we used the following setup:
    * 
    *timingSetup = 0x4000 (internal timing mode)
    *sGateWidth = 0x0010 
    *tCalbDelay =  0x0040 
    *CNRSTPulse = 0x08080
    *    
    *We raise an interrupt on IRQ3 when the gate is complete with priority 5
    */
    unsigned short timingSetup, sGateWidth, tCalbPulse,
      softTrigger, softTcalb, softSgate, softCNRST;

    unsigned short crimStatusValue;

    /*!  these are the various masks that are used to set up 
    * running conditions
    */
    static const unsigned short TimingSetupRegisterModeMask;
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

    /*! timing stuff */
    void SetTiming(unsigned short a); //set the timing register value
    void SetFrequency(crimTimingFrequencies a); //timing frequency (zero for one shot sequencer)
    void SetGateWidth(unsigned short a); //set gate width
    void SetTcalbPulse(unsigned short a);  //set pluse delay
    void SetSoftCNRST(unsigned short a); //trigger gate

    void SetSoftTrig(unsigned short a); //not yet instrumented
    void SetSoftTcalb(unsigned short a); //not yet instrumented
    void SetSoftSGate(unsigned short a); //not yet instrumented
    //functions which return the timing/trigger info
    crimTimingFrequencies GetFrequency();
    unsigned short inline GetGateWidth() {return sGateWidth;};
    unsigned short inline GetTcalbPulse() {return tCalbPulse;};
    unsigned short GetSoftTrig();
    unsigned short GetSoftTcalb();
    unsigned short GetSoftSGate();
    unsigned short inline GetSoftCNRST() {return softCNRST;};
    unsigned short GetTiming(); 
    unsigned short inline GetTimingSetup() {return timingSetup;};
    void SetupOneShot();
   
    unsigned int inline GetTimingRegister() {return timingRegister;};
    unsigned int inline GetGateRegister() {return sGateRegister;};
    unsigned int inline GetTCalbRegister() {return tCalbRegister;};
    unsigned int inline GetCNRSTRegister() {return cnrstRegister;};
    //unsigned int inline GetInterruptRegister() {return cnrstRegister;};
 
    /*! interrupt stuff */
    void inline SetIRQLevel(CVIRQLevels a) {irqLevel = a;}; //sets the IRQ Level (CAEN)
    void inline SetIRQLine(crimInterrupts a) {irqLine = a;}; //sets the IRQ Level (CAEN)

    void inline SetInterruptMask() {interruptValue = ((unsigned short)irqLine & InterruptMaskRegisterMask);}; //sets the interrupt value bitmask

    void inline SetInterruptStatus(unsigned short a) {interruptStatus = a & InterruptStatusRegisterMask;}; //stores the interrupt status

    void inline SetInterruptConfigValue(unsigned short a) {interruptConfigValue = a;}; //must match the IRQ vlaue
    void inline SetInterruptGlobalEnable(bool a) {interruptConfigValue |= ((a << 7) & InterruptConfigGlobalEnableMask);}; //sets the global enable bit

    unsigned short inline GetInterruptMask() {return interruptValue;}; //returns the interrupt bitmask
    unsigned int inline GetInterruptMaskAddress() {return interruptAddress;}; //return the register address to set the 
                                                                                //interrupt bitmask
    unsigned short inline GetInterruptStatus() {return (interruptStatus & InterruptStatusRegisterMask);}; //returns the interrupt status

    unsigned short inline GetInterruptGlobalEnable() {return interruptConfigValue & InterruptConfigGlobalEnableMask;}; //returns the global enable status
    unsigned short inline GetInterruptConfig() {return interruptConfigValue;}; //returns the value of the interrupt level & enable bit
    unsigned int inline GetInterruptsConfigAddress() {return interruptConfig;}; //returns the interrupt config address

    CVIRQLevels inline GetIRQLevel() {return irqLevel;}; //returns the irq level (CAEN)

    unsigned int inline GetInterruptStatusAddress() {return interruptStatusRegister;}; //return the interrupt status register address

    unsigned short inline GetClearInterrupts() {return resetInterrupts;}; //returns the reset interrupt bitmask
    unsigned int inline GetClearInterruptsAddress() {return interruptsClear;}; //returns the clear interrupts register address
                                                                                     
    /*! control stuff */
    void SetCRCEnable(bool a);
    void SetSendEnable(bool a);
    void SetReTransmitEnable(bool a);
    unsigned short inline GetStatus() {return crimStatusValue;};
    unsigned short inline GetControlRegister() {return controlRegisterAddress;};
    long_m inline GetStatusRegisterAddress() {return statusRegisterAddress;}; 
    unsigned int inline GetClearRegisterAddress() {return clearStatusRegister;};
    unsigned int inline GetCrimAddress() {return crimAddress;};
};

#endif
