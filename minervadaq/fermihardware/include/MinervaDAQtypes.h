#ifndef MinervaDAQtypes_h
#define MinervaDAQtypes_h

/*********************************************************************************
 * General types 
 * These enumerated lists are used to make remembering the
 * bit masks for various status & register settings easier.
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 ********************************************************************************/

#include <cmath>

/*! \file MinervaDAQTypes.h
 *
 * \brief More enumerations for decoding minerva data
 *
 */

/* A new, shiny "Minerva Long" for those pesky >32-bit integers on a 32-bit kernel 
   Elaine Schulte, June 4, 2009 
 */
#ifdef SYS_32
typedef unsigned long long long_m;
#else
typedef unsigned long long_m;
#endif 



//---------------
/* crim types */
//---------------

/*! \enum crimTimingModes
 *
 * \brief The register values for different timing modes 
 *
 */
typedef enum crimTimingModes { //cast this to unsigned short
	DAQ          = 0x1000,
	crimExternal = 0x2000,
	crimInternal = 0x4000,
	MTM          = 0x8000
};


/*! \enum crimTimingFrequencies
 *
 * \brief The register values for different frequencies. 
 *
 */
typedef enum crimTimingFrequencies { //cast this to unsigned short
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
};


/*! \enum crimRegisters
 *
 * \brief The register addresses on the CRIM  
 *
 */
typedef enum crimRegisters { //cast this to unsigned int
	crimMemory                 = 0x0000,
	crimInput                  = 0x2000,
	crimResetFIFO              = 0x2008,
	crimSendMessage            = 0x2010,
	crimStatus                 = 0x2020,
	crimClearStatus            = 0x2030,
	crimSendSynch              = 0x2040,
	crimDPMPointer             = 0x2050,
	crimDecodedCommand         = 0x2060,
	crimControl                = 0x2070,
	crimTimingSetup            = 0xC010,
	crimSGATEWidth             = 0xC020,
	crimTCALBDelay             = 0xC030,
	crimSoftwareTrigger        = 0xC040,
	crimSoftwareTCALB          = 0xC050,
	crimSoftwareSGATE          = 0xC060,
	crimSequencerControlLatch  = 0xC070, // Register for external trigger modes (cosmic - v5 firmware only) 
	crimSoftwareCNRST          = 0xC080,
	crimTimingOverlapViolation = 0xC090, // Readonly check for timing signal overlaps (obsolete)
	crimTestRegister           = 0xC0A0, // CG, Synch Test facility?
	crimGateTimeWordLow        = 0xC0B0, // MINOS SGATE least significant bits
	crimGateTimeWordHigh       = 0xC0C0, // MINOS SGATE most significant bits (total 28 meaningful bits)
	crimInterruptMask          = 0xF000,
	crimInterruptStatus        = 0xF010,
	crimClearInterrupts        = 0xF020,
	crimInterruptConfig        = 0xF040,
	crimInterruptVectors       = 0xF800  // 16 bytes
};


/*! \enum crimInterrupts
 *
 * \brief The interrupt bit masks   
 *
 */
typedef enum crimInterrupts { //typecast to unsigned char
	Trigger   = 0x01,
	SGATERise = 0x02,
	SGATEFall = 0x04,
	CNRST     = 0x08,
	TCALB     = 0x10
};


//---------------
/* croc types */
//---------------
typedef enum crocChannels{
	Ch1 = 1,
	Ch2 = 2,
	Ch3 = 3,
	Ch4 = 4
};


typedef enum crocClockModes { //typecast to unsigned int
	crocInternal = 0x0000,
	crocExternal = 0x8000
};


typedef enum crocTestPulseDelay { //typecast to unsigned int
	Disabled = 0x0000,
	Enabled  = 0x1000,
	Mask     = 0x03FF
};


typedef enum crocRegisters { //typecast to unsigned int
	crocMemory              = 0x0000,
	crocInput               = 0x2000,
	crocSendMessage         = 0x2010,
	crocStatus              = 0x2020,
	crocClearStatus         = 0x2030,
	crocLoopDelay           = 0x2040,
	crocDPMPointer          = 0x2050,
	crocTimingSetup         = 0xF000,
	crocResetAndTestMask    = 0xF010,
	crocChannelReset        = 0xF020,
	crocFastCommand         = 0xF030,
	crocTestPulse           = 0xF040,
	crocStartGate           = 0xF050,
	crocStopGate            = 0xF060
};


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

//---------------
/* croc types */
//---------------

static const int ecrocAddressShift = 24;

// All CROC-E channel registers may have a n * 0x400000 modifier, where n is the channel number (0-3).
typedef enum ecrocChannelRegisters { //typecast to unsigned int
	ecrocReceiveMemory             = 0x00000,
	ecrocSendMemory                = 0x22000,
	ecrocFramePointersMemory       = 0x24000,
	ecrocConfiguration             = 0x28002,
	ecrocCommand                   = 0x28004,
	ecrocEventCounter	       = 0x28008,
	ecrocFramesCounterAndLoopDelay = 0x28010,
	ecrocFrameStatus               = 0x28020,
	ecrocTxRxStatus                = 0x28040,
	ecrocReceiveMemoryPointer      = 0x28080
};

#endif
