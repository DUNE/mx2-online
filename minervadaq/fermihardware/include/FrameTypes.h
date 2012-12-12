#ifndef FrameTypes_h
#define FrameTypes_h
/*********************************************************************************
 * FPGA frame general types 
 * These enumerated lists are used to make remembering the
 * bit masks for various device settings easier.
 *
 * It also has the bitmasks for the various functions needed to
 * make up the FPGA frames 
 * 
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 ********************************************************************************/

/*! \file FrameTypes
 *
 * \brief A header file containing useful enumertions
 *
 *  The first byte of an outgoing frame contains:
 *  Bits 0-3:  Front-end address (1-15; 0 = all)
 *  Bits 4-6:  Broadcast command (0 = not a broadcast)
 *  Bit    7:  Bit indicating direction (0 for outgoing, 1 for response)
 */

/*! \enum Directions 
 * \brief The message handling direction.
 * */
typedef enum Directions { //typecast to unsigned char
	MasterToSlave = 0x00,
	SlaveToMaster = 0x80
};


/*! \enum Broadcasts 
 * \brief What type of message 
 */
typedef enum Broadcasts { //typecast to unsigned char
	None        = 0x00,
	LoadTimer   = 0x10,
	ResetTimer  = 0x20,
	OpenGate    = 0x30,
	SoftReset   = 0x40
};


/*!
 * The second byte of an outgoing message indicates the device (on the FEB) and function:
 * Bits 0-3:  Function
 * Bits 4-7:  Device
 */


/*! \enum Devices
 * \brief Which device is being addressed 
 *
 */
typedef enum Devices { //typecast to unsigned char
	NoDevices  = 0x00,
	TRiP  	   = 0x10,
	FPGA       = 0x20,
	RAM        = 0x30,
	Flash      = 0x40
};


/*! \enum FPGAFunctions 
 * \brief A read or write frame 
 *
 */
typedef enum FPGAFunctions { //typecast to unsigned char
	NoFPGA   = 0x00,
	Write    = 0x01,
	Read     = 0x02,
	DumpRead = 0x03
};


/*! \enum RAMFunctionsHit
 *
 * \brief Which hit to read off of the ADC's 
 *
 */
typedef enum RAMFunctionsHit { //typecast to unsigned char
	NoRAM        = 0x00,
	ReadHit0     = 0x01,
	ReadHit1     = 0x02,
	ReadHit2     = 0x03,
	ReadHit3     = 0x04,
	ReadHit4     = 0x05,
	ReadHit5     = 0x06,
	ReadHitDiscr = 0x07,
	ReadHit6     = 0x0E,
	ReadHit7     = 0x0F
};


/*! \enum RAMFunctionsChip
 *
 * \brief  Depricated - DO NOT USE!
 *
 */
typedef enum RAMFunctionsChip { //typecast to unsigned char
	NoChip       = 0x00,
	ReadChip0    = 0x08,
	ReadChip1    = 0x09,
	ReadChip2    = 0x0A,
	ReadChip3    = 0x0B,
	ReadChip4    = 0x0C,
	ReadChip5    = 0x0D,
	ReadDigital0 = 0x0E,
	ReadDigital1 = 0x0F
};


/*! \enum FlashFunctions
 *
 * \brief For writing firmware to flash memory 
 *
 */
typedef enum FlashFunctions { //typecast to unsigned char
	NoFlash  = 0x00,
	Command  = 0x01,
	SetReset = 0x02
};


/*! \enum ResponseWords
 *
 * \brief Useful for decoding returning frame headers 
 *
 */
typedef enum ResponseWords { //typecast to unsigned char
	ResponseLength0 = 0,
	ResponseLength1 = 1,
	FrameStatus0    = 2,  // New for CROC-E
	FrameStatus1	= 3,  // New for CROC-E
	FrameStart      = 4,
	DeviceStatus    = 5,
	FrameStatus     = 6,
	FrameID0        = 7,
	FrameID1        = 8,
	Timestamp0      = 9,
	Timestamp1      = 10,
	Timestamp2      = 11,
	Timestamp3      = 12,
	Data            = 13
};


/*! \enum HeaderWords
 *
 * \brief Useful for decoding FPGA frame headers
 *
 */
typedef enum HeaderWords { //typecast to unsigned char
	hwFrameStart     = 0,
	hwDeviceFunction = 1,
	hWord2           = 2,
	hwFrameID0       = 3,
	hwFrameID1       = 4,
	hWord5           = 5,
	hWord6           = 6,
	hWord7           = 7,
	hWord8           = 8
};


/*! \enum ResponseFlags
 *
 * \brief Bitmasks for decoding the status of a returned message
 *
 */
typedef enum ResponseFlags { //typecast to unsigned char
	// in Frame Start
	Direction = 0x80, //slave-to-master
	Broadcast = (0x10 | 0x30 | 0x20 | 0x40), //LoadTimer | OpenGate| ResetTimer | SoftReset
	// in Device Status
	DeviceOK   = 0x01,
	FunctionOK = 0x02,
	// in Frame Status
	CRCOK       = 0x01,
	EndHeader   = 0x02,
	MaxLen      = 0x04,
	SecondStart = 0x08,
	NAHeader    = 0x10
};


/*! \enum febAddress
 *
 * \brief  FPGA addresses 
 *
 * */
typedef enum febAddresses {
	febAll = 0,
	FE1    = 1,
	FE2    = 2,
	FE3    = 3,
	FE4    = 4,
	FE5    = 5,
	FE6    = 6,
	FE7    = 7,	
	FE8    = 8,
	FE9    = 9,
	FE10   =10,
	FE11   =11,
	FE12   =12,
	FE13   =13,
	FE14   =14,
	FE15   =15
};


#endif