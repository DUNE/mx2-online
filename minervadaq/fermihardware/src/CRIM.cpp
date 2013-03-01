#ifndef CRIM_cpp
#define CRIM_cpp

#include <iostream>
#include <iomanip>
#include "CRIM.h"
#include "exit_codes.h"

/*********************************************************************************
 * Class for creating Chain Read-Out Controller Interfact Module objects for 
 * use with the MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

log4cpp::Category& CRIMLog = log4cpp::Category::getInstance(std::string("CRIM"));

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

const unsigned long long CRIM::timeOutSec = 3600;   // be careful shortening this w.r.t. multi-PC sync issues

//----------------------------------------
// NOTE: The IRQ level must be the same as the configuration register level.  
// The BIT MASKS for these levels, however are not the same!
CRIM::CRIM( unsigned int address, const Controller* controller, 
    CRIMInterrupts line, unsigned short level ) :
  VMECommunicator( address, controller ),
  irqLevel(level),
  irqLine(line)
{
  this->addressModifier = cvA24_U_DATA; 

  CRIMLog.setPriority(log4cpp::Priority::INFO); 
  CRIMLog.debugStream() << "Creating CRIM with address = 0x" << std::hex 
    << this->address << "; IRQ Line = 0x" << this->irqLine 
    << "; IRQ Level = 0x" << this->irqLevel;

  interruptStatusRegister = this->address + (unsigned int)CRIMInterruptStatus;
  interruptConfig         = this->address + (unsigned int)CRIMInterruptConfig;
  interruptsClear         = this->address + (unsigned int)CRIMClearInterrupts;
  interruptAddress        = this->address + (unsigned int)CRIMInterruptMask;
  timingRegister          = this->address + (unsigned int)CRIMTimingSetup;
  SGATEWidthRegister      = this->address + (unsigned int)CRIMSGATEWidth;
  TCALBDelayRegister      = this->address + (unsigned int)CRIMTCALBDelay;
  softwareTriggerRegister = this->address + (unsigned int)CRIMSoftwareTrigger;
  softwareTCALBRegister   = this->address + (unsigned int)CRIMSoftwareTCALB;
  softwareSGATERegister   = this->address + (unsigned int)CRIMSoftwareSGATE;
  softwareCNRSTRegister   = this->address + (unsigned int)CRIMSoftwareCNRST;
  controlRegisterAddress  = this->address + (unsigned int)CRIMControl;
  statusRegisterAddress   = this->address + (unsigned int)CRIMStatus;
  clearStatusRegister     = this->address + (unsigned int)CRIMClearStatus;
  gateTimeWordLowAddress  = this->address + (unsigned int)CRIMGateTimeWordLow;
  gateTimeWordHighAddress = this->address + (unsigned int)CRIMGateTimeWordHigh;
  sequencerResetRegister  = this->address + (unsigned int)CRIMSequencerControlLatch;

  // register value for control register (DAQ Mode control)
  // set crc & send to true and retransmit to false	
  controlRegister = ControlRegisterCRCMask | ControlRegisterSendMask 
    & ~ControlRegisterRetransmitMask; 
}

//----------------------------------------
void CRIM::Initialize( RunningModes runningMode )
{
  CRIMLog.infoStream() << "Initializing CRIM 0x" << std::hex << this->address;
  this->logRunningMode( runningMode );

  // The CRIM will ignore the SequencerEnable instruction in firmware before v9.
  unsigned short GateWidth         = 0x7F;     // GetWidth must never be zero!
  unsigned short TCALBDelay        = 0x3FF;    // Delay should also be non-zero.
  unsigned short TCALBEnable       = 0x1;      // Enable pulse delay.
  unsigned short SequencerEnable   = 0x1;      // Sequencer control (0 means always send gates, 1 for rearms).
  CRIMTimingFrequencies Frequency  = ZeroFreq; // Used to set ONE frequency bit!  ZeroFreq ~no Frequency.
  CRIMTimingModes       TimingMode = MTM;      // Default to MTM.

  switch (runningMode) {
    case OneShot:
      // "OneShot" is the casual name for CRIM internal timing with software gates.
      // We can use MTM mode though and prefer to when an MTM is available. This 
      // removes the need to switch clock modes for pure pedestal. We keep the name
      // "OneShot" for historical reasons no matter the clock mode.
#if NOMTMPEDESTAL 
      TimingMode   = crimInternal;
#endif
      break;
    case NuMIBeam:
      break;
    case PureLightInjection:
#if MTEST
      // Because no MTM is available at MTest, LI will use internal timing.
      TimingMode   = CRIMInternal;
      CRIMLog.infoStream() << "->Using MTest timing (CRIM Internal).";
#endif
      break;
    case MixedBeamPedestal:
    case MixedBeamLightInjection:
      break;
    case Cosmics:
    case MTBFBeamMuon:
    case MTBFBeamOnly:
      // Cosmics, Beam-Muon, & Beam-Only use CRIM internal timing with gates send at a set frequency.
      Frequency     = F2;
      TimingMode    = crimInternal;
      break;
    default:
      CRIMLog.fatalStream() << "Error in acquire_data::InitializeCrim()! No Running Mode defined!";
      exit(EXIT_CONFIG_ERROR);
  }
  CRIMLog.debugStream() << " GateWidth       = 0x" << std::hex << GateWidth;
  CRIMLog.debugStream() << " TCALBDelay      = 0x" << std::hex << TCALBDelay;
  CRIMLog.debugStream() << " TCALBEnable     = 0x" << std::hex << TCALBEnable;
  CRIMLog.debugStream() << " SequencerEnable = 0x" << std::hex << SequencerEnable;
  CRIMLog.debugStream() << " Frequency       = " << Frequency;
  CRIMLog.debugStream() << " Timing Mode     = " << TimingMode;

  this->SetupGateWidth( TCALBEnable, GateWidth, SequencerEnable );
  this->SetupTiming( TimingMode, Frequency );
  this->SetupTCALBPulse( TCALBDelay );
}

//----------------------------------------
void CRIM::logRunningMode( const RunningModes& runningMode ) const
{
  switch (runningMode) {
    case OneShot:
      CRIMLog.infoStream() << " Running Mode is OneShot.";
      break;
    case NuMIBeam:
      CRIMLog.infoStream() << " Running Mode is NuMI Beam.";
      break;
    case PureLightInjection:
      CRIMLog.infoStream() << " Running Mode is PureLightInjection.";
      break;
    case MixedBeamPedestal:
      CRIMLog.infoStream() << " Running Mode is MixedBeamPedestal.";
      break;
    case MixedBeamLightInjection:
      CRIMLog.infoStream() << " Running Mode is MixedBeamLightInjection.";
      break;
    case Cosmics:
      CRIMLog.infoStream() << " Running Mode is Cosmic.";
      break;
    case MTBFBeamMuon:
      CRIMLog.infoStream() << " Running Mode is MTBFBeamMuon.";
      break;
    case MTBFBeamOnly:
      CRIMLog.infoStream() << " Running Mode is MTBFBeamOnly.";
      break;
    default:
      CRIMLog.critStream() << "Error in ReadoutWorker::logRunningMode()! Undefined Running Mode!";
  }
}

//----------------------------------------
void CRIM::SetupTiming( CRIMTimingModes timingMode, CRIMTimingFrequencies frequency ) const
{
  unsigned short timingSetup = 
    ( timingMode & TimingSetupRegisterModeMask ) | 
    ( frequency  & TimingSetupRegisterFrequencyMask );

  CRIMLog.debugStream() << "CRIM timingSetup = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << timingSetup;
  CRIMLog.debugStream() << "      timingMode = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << timingMode;
  CRIMLog.debugStream() << "       frequency = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << frequency;

  unsigned char message[] = {0x0, 0x0};
  message[0] = timingSetup & 0xFF;
  message[1] = (timingSetup>>8) & 0xFF;
  int error = WriteCycle( 2, message, timingRegister, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Failure writing to CRIM Timing Register!");
} 

//----------------------------------------
void CRIM::SetupGateWidth( unsigned short tcalbEnable, 
    unsigned short gateWidth, unsigned short sequencerEnable ) const
{
  // sequencerEnable bit is ignored on CRIM firmwares earlier than v9
  unsigned short gateWidthSetup = 
    ((tcalbEnable & 0x1)<<15)            | 
    ((sequencerEnable & 0x1)<<10)        | 
    (gateWidth & GateWidthRegisterMask);

  CRIMLog.debugStream() << "CRIM gateWidthSetup = 0x"
    << std::setfill('0') << std::setw( 4 ) << std::hex << gateWidthSetup;
  CRIMLog.debugStream() << "       gateWidth = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << gateWidth;
  CRIMLog.debugStream() << " sequencer enable = " << sequencerEnable;
  CRIMLog.debugStream() << "     tcalb enable = " << tcalbEnable;

  unsigned char message[] = {0x0, 0x0};
  message[0] = gateWidthSetup & 0xFF;
  message[1] = (gateWidthSetup>>8) & 0xFF;
  int error = WriteCycle( 2, message, SGATEWidthRegister, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Failure writing to CRIM Gate Width Register!");
}

//----------------------------------------
void CRIM::SetupTCALBPulse( unsigned short pulseDelay ) const
{
  unsigned short TCALBDelaySetup = pulseDelay & TCALBDelayRegisterMask;

  CRIMLog.debugStream() << "CRIM TCALBDelaySetup = 0x"
    << std::setfill('0') << std::setw( 4 ) << std::hex << TCALBDelaySetup;

  unsigned char message[] = {0x0, 0x0};
  message[0] = TCALBDelaySetup & 0xFF;
  message[1] = (TCALBDelaySetup>>8) & 0xFF;
  int error = WriteCycle( 2, message, TCALBDelayRegister, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Failure writing to CRIM TCALB Pulse Delay Register!");
} 

//----------------------------------------
void CRIM::IRQEnable() const
{
  /*!\fn void CRIM::IRQEnable() const
   *
   * These are the steps to setting the IRQ:
   *  1) Select an IRQ LINE on which the system will wait for an assert.  
   *
   *  2) Set the Interrupt mask on the crim.
   *
   *  3) Check the interrupt status & clear any pending interrupts.  
   *
   *  4) Set the IRQ LEVEl which is asserted on the LINE.  We have set this to IRQ5, or 5 in the register
   *  when the CRIM is created.  (This also happens to be the power on default.)
   *
   *  5) Set the Global IRQ Enable bit.
   *
   *  6) Send this bitmask to the CRIM.
   *
   *  7) Enable the IRQ LINE on the CAEN controller to be the NOT of the IRQ LINE sent to the CRIM.
   */
  CRIMLog.debugStream() << "IRQEnable for CRIM 0x" << std::hex << this->address;
  CRIMLog.debugStream() << " IRQ Line  = " << (int)this->irqLine;
  CRIMLog.debugStream() << " IRQ Level = " << (int)this->irqLevel;

  this->SetupInterruptMask();
  unsigned short interruptStatus = this->GetInterruptStatus();
  this->ClearPendingInterrupts( interruptStatus );
  this->ResetGlobalIRQEnable();
  this->CAENVMEIRQEnable();
}

//----------------------------------------
void CRIM::SetupInterruptMask() const
{
  // Note that we use the irqLine instance variable.
  unsigned short mask = this->GetInterruptMask();
  CRIMLog.debugStream() << "InterruptMask = " << mask;
  unsigned char message[2] = {0,0};
  message[0] = mask & 0xFF;
  message[1] = (mask>>0x08) & 0xFF;
  int error = WriteCycle( 2, message, interruptAddress, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Error setting CRIM IRQ mask!");
}

//----------------------------------------
unsigned short CRIM::GetInterruptStatus() const
{
  unsigned char message[] = {0x0,0x0};
  int error = ReadCycle( message, interruptStatusRegister, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Error reading CRIM Interrupt Status Register!");
  unsigned short status = (message[1]<<8) | message[0];
  CRIMLog.debugStream() << "Interrupt Status = 0x" << std::hex << status;
  return status;
}

//----------------------------------------
void CRIM::ClearPendingInterrupts( unsigned short interruptStatus ) const
{
  if ( interruptStatus !=0 ) {
    unsigned short resetInterrupts = 0x81;  // clear all pending interrupts
    unsigned char message[] = {0x0,0x0};
    message[0] = resetInterrupts & 0xFF;
    message[1] = (resetInterrupts>>0x08) & 0xFF;
    CRIMLog.debugStream() << " Clearing pending interrupts with message: 0x"
      << std::setfill('0') << std::setw(2) << std::hex << (int)message[1]
      << std::setfill('0') << std::setw(2) << std::hex << (int)message[0];
    int error = WriteCycle( 2, message, interruptsClear, addressModifier, dataWidthReg );
    if( error ) exitIfError( error, "Error clearing pending CRIM Interrupts!");
  } else {
    CRIMLog.debugStream() << "No pending interrupts to clear.";
  }
}

//----------------------------------------
void CRIM::ResetGlobalIRQEnable() const
{
  CRIMLog.debugStream() << "ResetGlobalIRQEnable for CRIM 0x" << std::hex << this->address;
  CRIMLog.debugStream() << " Enable bit = 0x" << std::hex << (1 << 7);
  CRIMLog.debugStream() << " IRQ Level  = 0x" << std::hex << irqLevel;
  unsigned short interruptMessage = (1 << 7) | irqLevel;  // 1 << 7 sets the enable bit to true.
  CRIMLog.debugStream() << " interruptMessage = 0x" << std::hex << interruptMessage;
  unsigned char message[] = {0x0,0x0};
  message[0] = (interruptMessage) & 0xFF;
  message[1] = (interruptMessage >> 0x08) & 0xFF;
  CRIMLog.debugStream() << " Resetting Global IRQ Enable with message 0x" 
    << std::setfill('0') << std::setw(2) << std::hex << (int)message[1]
    << std::setfill('0') << std::setw(2) << std::hex << (int)message[0];
  int error = WriteCycle( 2, message, interruptConfig, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Error setting IRQ Global Enable Bit!");
}

//----------------------------------------
void CRIM::CAENVMEIRQEnable() const
{
  CRIMLog.debugStream() << "CAENVMEIRQEnable for mask 0x" << std::hex << ~this->GetInterruptMask();
  int error = CAENVME_IRQEnable(this->GetController()->GetHandle(),~this->GetInterruptMask());
  if( error ) exitIfError( error, "Error writing to CAEN VME IRQ Enable for CRIM!");
}

//----------------------------------------
unsigned int CRIM::GetAddress() const
{
  return this->address;
}

//----------------------------------------
unsigned short CRIM::GetInterruptMask() const
{
  return ((unsigned short)irqLine & InterruptMaskRegisterMask);
} 

//----------------------------------------
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

//----------------------------------------
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

//----------------------------------------
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

//----------------------------------------
unsigned short CRIM::GetStatus() const
{
  unsigned char dataBuffer[] = {0x0,0x0}; 
  int error = ReadCycle( dataBuffer, statusRegisterAddress, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Failure reading the CRIM Status Register!");
  unsigned short status = dataBuffer[1]<<8 | dataBuffer[0];
  return status;
}

//----------------------------------------
void CRIM::ResetSequencerLatch() const
{
  /*! \fn void CRIM::ResetSequencerLatch()
   *
   * This function resets the CRIM sequencer latch in cosmic mode to restart the seqeuncer in 
   * internal timing mode.  This only affects CRIMs with v5 firmware.
   */
  CRIMLog.debugStream() << "ResetSequencerLatch for CRIM 0x" << std::hex << this->address;
  unsigned char message[] = { 0x02, 0x02 };
  int error = WriteCycle( 2, message, sequencerResetRegister, addressModifier, dataWidthReg );
  if( error ) exitIfError( error, "Error resetting the sequencer latch!");
}

//---------------------------
int CRIM::WaitOnIRQ( sig_atomic_t const & continueFlag ) const
{
  /*! \fn void ReadoutWorker::WaitOnIRQ() 
   *
   * A function which waits on the interrupt handler to set an interrupt.  This function 
   * only checks the "master" CRIM.  The implicit assumption is that a trigger on any 
   * CRIM is a trigger on all CRIMs (this assumption is true by design). This function 
   * is "dumb" with respect to interrupts and only polls the interrupt status. See older
   * versions of the DAQ software for guesses on how to handle asserted interrupts.
   */
  int success = 0;
  CRIMLog.debugStream() << "Entering CRIM::WaitOnIRQ: IRQLevel = " << this->irqLevel;

  // Wait length vars... (don't want to spend forever waiting around).
  unsigned long long startTime, nowTime;
  struct timeval waitstart, waitnow;
  gettimeofday(&waitstart, NULL);
  startTime = (unsigned long long)(waitstart.tv_sec);
  // VME manip.
  unsigned short interruptStatus = 0;
  unsigned short iline = (unsigned short)this->irqLine;
  CRIMLog.debugStream() << "  Interrupt line = " << iline;

  while ( !( interruptStatus & iline ) ) {
    if ( !continueFlag ) {
      CRIMLog.debugStream() << "Caught exit signal.  Bailing on CRIM IRQ wait.";
      return 1;
    }
    interruptStatus = this->GetInterruptStatus();
    gettimeofday(&waitnow, NULL);
    nowTime = (unsigned long long)(waitnow.tv_sec);
    if ( (nowTime-startTime) > timeOutSec) { 
      CRIMLog.debugStream() << "Timing out. No interrupt after " << timeOutSec << " seconds.";
      success = 1;
      break; 
    } 
  }
  // Clear the interrupt after acknowledging it.
  this->ClearPendingInterrupts( interruptStatus );

  return success;
}

#endif
