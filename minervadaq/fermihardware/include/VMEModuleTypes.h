#ifndef VMEModuleTypes_h
#define VMEModuleTypes_h
/*! \file VMEModuleTypes.h
*/

#include <cmath>

/*!
  \brief Enumerations for decoding minerva data - focused on VME modules.
  \author Gabriel Perdue
  \author Elaine Schulte
  */

namespace VMEModuleTypes {

  /*! 
    \enum VMECommunicators
    \brief The different modules and devices we address by VME.

    CROC and Channels do not appear as classes in this version of the DAQ.
    */
  typedef enum {
    UnknownCommunicator,
    CRIM,
    CROC,
    Channels,
    ECROC,
    EChannels
  } VMECommunicatorType;

  //---------------
  /* crim types */
  //---------------

  // CRIM has 24-bit addressing. Addrr = 8 bits << 16 
  static const unsigned int CRIMAddressShift = 16;

  /*! 
    \enum CRIMTimingModes
    \brief The register values for different timing modes 
    */
  typedef enum { //cast this to unsigned short
    DAQ          = 0x1000,
    CRIMExternal = 0x2000,
    CRIMInternal = 0x4000,
    MTM          = 0x8000
  } CRIMTimingModes;


  /*! 
    \enum CRIMTimingFrequencies
    \brief The register values for different frequencies for gates in internal timing mode. 
    */
  typedef enum { //cast this to unsigned short
    // For internal timing mode - only one frequency bit may be set at a time!
    ZeroFreq = 0x0000, // Really "no" frequency - correct mode for OneShot, MTM running.
    F0       = 0x0001, // fastest, too fast for our FEB's
    F1       = 0x0002,
    F2       = 0x0004,
    F3       = 0x0008,
    F4       = 0x0010, // fastest our FEB's ran with in Wideband
    F5       = 0x0020,
    F6       = 0x0040,
    F7       = 0x0080,
    F8       = 0x0100,
    F9       = 0x0200,
    F10      = 0x0400,
    F11      = 0x0800 // slowest
  } CRIMTimingFrequencies;

  /*! 
    \enum CRIMRegisters
    \brief The register addresses on the CRIM  
    */
  typedef enum CRIMRegisters { //cast this to unsigned int
    CRIMMemory                 = 0x0000,
    CRIMInput                  = 0x2000,
    CRIMResetFIFO              = 0x2008,
    CRIMSendMessage            = 0x2010,
    CRIMStatus                 = 0x2020,
    CRIMClearStatus            = 0x2030,
    CRIMSendSynch              = 0x2040,
    CRIMDPMPointer             = 0x2050,
    CRIMDecodedCommand         = 0x2060,
    CRIMControl                = 0x2070,
    CRIMTimingSetup            = 0xC010,
    CRIMSGATEWidth             = 0xC020,
    CRIMTCALBDelay             = 0xC030,
    CRIMSoftwareTrigger        = 0xC040,
    CRIMSoftwareTCALB          = 0xC050,
    CRIMSoftwareSGATE          = 0xC060,
    CRIMSequencerControlLatch  = 0xC070, // Register for external trigger modes (cosmic - v5 firmware only) 
    CRIMSoftwareCNRST          = 0xC080,
    CRIMTimingOverlapViolation = 0xC090, // Readonly check for timing signal overlaps (obsolete)
    CRIMTestRegister           = 0xC0A0, // CG, Synch Test facility?
    CRIMGateTimeWordLow        = 0xC0B0, // MINOS SGATE least significant bits
    CRIMGateTimeWordHigh       = 0xC0C0, // MINOS SGATE most significant bits (total 28 meaningful bits)
    CRIMInterruptMask          = 0xF000,
    CRIMInterruptStatus        = 0xF010,
    CRIMClearInterrupts        = 0xF020,
    CRIMInterruptConfig        = 0xF040,
    CRIMInterruptVectors       = 0xF800  // 16 bytes
  };


  /*! 
    \enum CRIMInterrupts
    \brief The interrupt bit masks   
    */
  typedef enum  { //typecast to unsigned char
    Trigger   = 0x01,
    SGATERise = 0x02,
    SGATEFall = 0x04,
    CNRST     = 0x08,
    TCALB     = 0x10
  } CRIMInterrupts;


  //---------------
  /* status bits for croc & crim */
  //---------------
  typedef enum StatusBits { //typecast to unsigned short
    MessageSent            = 0x0001,
    MessageReceived        = 0x0002,
    CRCError               = 0x0004,
    TimeoutError           = 0x0008,
    FIFONotEmpty           = 0x0010,
    FIFOFull               = 0x0020,
    DPMFull                = 0x0040,
    UnusedBit1             = 0x0080,  // Irrelevant Note: "UnusedBit7" in WinDAQ
    RFPresent              = 0x0100,
    SerializerSynch        = 0x0200,
    DeserializerLock       = 0x0400,
    UnusedBit2             = 0x0800,  // Irrelevant Note: "UnusedBit11" in WinDAQ
    PLLLocked              = 0x1000,
    TestPulseReceived      = 0x2000,  // CRIM only  // CG for CROC it is PLL1lock
    ResetReceived          = 0x4000,  // CRIM only
    EncodedCommandReceived = 0x8000   // CRIM only
  };

  //-----------------
  /* Fast Commands */
  //-----------------

  // Need to clarify how these function differently from broadcasts - may affect naming conventions.
  // Most and least significant bit are always 1 for FastCommands.
  typedef enum FastCommands {     //typecast to unsigned char
    fcOpenGate     = 0xB1,  // 3 0 -> 1011 0001 -> X011 000X
    fcResetFPGA    = 0x8D,  // 0 C / 0 12, etc.
    fcResetTimer   = 0xC5,
    fcLoadTimer    = 0xC9,
    fcTriggerFound = 0x89,
    fcTriggerRearm = 0x85
  };	


  //---------------
  /* croce types */
  //---------------

  static const unsigned int ECROCAddressShift = 24;
  static const unsigned int EChannelOffset    = 0x40000;

  // These values are good for the ecroc as well.
  typedef enum ECROCClockModes { //typecast to unsigned int
    ECROCInternal = 0x0000,
    ECROCExternal = 0x8000
  };

  typedef enum ECROCTestPulseDelay { //typecast to unsigned int
    Disabled = 0x0000,
    Enabled  = 0x1000,
    Mask     = 0x01FF  // 1FF is mask for ecroc. ocroc was 3FF
  };

  // All CROC-E channel registers may have a n * 0x400000 modifier, where n is the channel number (0-3).
  typedef enum ECROCChannelRegisters { //typecast to unsigned int
    ECROCReceiveMemory             = 0x00000,
    ECROCSendMemory                = 0x22000,
    ECROCFramePointersMemory       = 0x24000,
    ECROCConfiguration             = 0x28002,
    ECROCCommand                   = 0x28004,
    ECROCEventCounter              = 0x28008,
    ECROCFramesCounterAndLoopDelay = 0x28010,
    ECROCFrameStatus               = 0x28020,
    ECROCTxRxStatus                = 0x28040,
    ECROCReceiveMemoryPointer      = 0x28080
  };

  typedef enum ECROCRegisters { //typecast to unsigned int
    ECROCTimingSetup               = 0xFF000,
    ECROCResetAndTestPulseMask     = 0xFF010,
    ECROCChannelReset              = 0xFF020,
    ECROCFastCommand               = 0xFF030,
    ECROCTestPulse                 = 0xFF040,
    ECROCRdfePulseDelay            = 0xFF050,
    ECROCRdfePulseCommand          = 0xFF060
  };

  typedef enum ECCROCChannelFrameStatusBits { //typecast to unsigned short
    ReceiveMemoryFrameDiscType    = 0x0001,
    ReceiveMemoryFrameHeaderError = 0x0002,
    ReceiveMemoryCRCError         = 0x0004,
    ReceiveMemoryFrameTimeout     = 0x0008,
    ReceiveMemoryFrameReceived    = 0x0010,
    ReceiveMemoryFrameCountFull   = 0x0020,
    ReceiveMemoryEmpty            = 0x0040,
    ReceiveMemoryFull             = 0x0080,  
    SendMemoryUnusedBit0          = 0x0100,
    SendMemoryUnusedBit1          = 0x0200,
    SendMemoryRDFEDone            = 0x0400,
    SendMemoryRDFEUpdating        = 0x0800,  
    SendMemoryFrameSent           = 0x1000,
    SendMemoryFrameSending        = 0x2000,  
    SendMemoryEmpty               = 0x4000,  
    SendMemoryFull                = 0x8000   
  };

}


#endif
