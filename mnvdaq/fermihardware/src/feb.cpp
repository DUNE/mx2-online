#ifndef feb_cpp
#define feb_cpp

#include "feb.h"
/*********************************************************************************
* Class for creating Front-End Board (FEB) objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
**********************************************************************************/

// log4cpp category hierarchy.
log4cpp::Category& febLog = log4cpp::Category::getInstance(std::string("feb"));

feb::feb(int mh, bool init, febAddresses a, int reg, log4cpp::Appender* appender) : Frames(appender) 
{
/*! \fn********************************************************************************
 * The log-free constructor takes the following arguments:
 * \param mh: maximum number of hits per tdc
 * \param init: the FEB is initialized (i.e. an FEB is available)
 * \param a: The address (number) of the feb
 * \param reg:  The number of one byte registers in the FEB message body
 *       The message body is set up for FEB Firmware Versions 78+ (54 registers).  
 *       It will need to be adjusted for other firmware versions. ECS & GNP
 */
	maxHits      = mh;     // Maximum number of hits
	initialized  = false;  // Frames are not initialized by default
	boardNumber  = a;      // feb address (also called board number)
	febNumber[0] = (unsigned char) a; // put the feb number into it's character.
	NRegisters   = reg;      // # of one byte registers in the data frame
	febAppender  = appender; // log4cpp appender
	if (febAppender!=0) febLog.setPriority(log4cpp::Priority::ERROR);
	
	// Make the header for this frame; frames default to read. 
	Devices dev = FPGA;     //the device type for the header
	Broadcasts b = None;    //broadcast type for header
	Directions d = MasterToSlave; //message direction for header
	FPGAFunctions f = Read;      //operation to be performed
	// Compose the transmission FPGA header
	MakeDeviceFrameTransmit(dev, b, d, f, (unsigned int)febNumber[0]);  

	// the header + information part of the message 
	OutgoingMessageLength = MinHeaderLength + NRegisters; //length of the outgoing message message
	TrueIncomingMessageLength = 
		2 + MinHeaderLength + NRegisters + (NRegisters + 1) % 2; //the length of the incoming message
	// Note above: incoming messages are ALWAYS 2 bytes LARGER than outgoing messages!

	// Instantiate objects for the trip chips on the board - loop over possible trips.
	for (int i=0;i<6;i++) { 
		TRiPFunctions chipFunction;
		// Assign the trip function to make up the trip object.
		switch (i) {  
			case 0:
				chipFunction = tTR0;
				break;
			case 1:
				chipFunction = tTR1;
				break;
			case 2:
				chipFunction = tTR2;
				break;
			case 3:
				chipFunction = tTR3;
				break;
			case 4:
				chipFunction = tTR4;
				break;
			case 5:
				chipFunction = tTR5;
				break;
			default: 
				std::cout << "Invalid TriP ChipID at instantiation!" << std::endl;
				if (febAppender!=0) { febLog.fatalStream() << "Invalid TriP ChipID at instantiation!"; }
				exit(1);
		}
		tripChips[i] = new trips(boardNumber,chipFunction,maxHits); 
	}

	// Instantiate a discriminator.  
	hits_n_timing = new disc(a); 
	
	// Instantiate objects for the ADC's
	// We read the RAMFunctions in "reverse" order:
	//  0               for 1 Hit (any firmware) - this *assumes* a PIPEDEL of 1!  This is a user responsibility! 
	//  4,3,2,1,0       for 5 Hit firmware (PIPEDEL 9).
	//  5,4,3,2,1,0     for 6 Hit firmware (PIPEDEL 11).
	//  7,6,5,4,3,2,1,0 for 8 Hit firmware (PIPEDEL 15).
	if (maxHits == 1) {
		adcHits[0] = new adc( a, (RAMFunctionsHit)ReadHit0 ); 
	} else if (maxHits == 5) {
		adcHits[0] = new adc( a, (RAMFunctionsHit)ReadHit4 );
		adcHits[1] = new adc( a, (RAMFunctionsHit)ReadHit3 );
		adcHits[2] = new adc( a, (RAMFunctionsHit)ReadHit2 );
		adcHits[3] = new adc( a, (RAMFunctionsHit)ReadHit1 );
		adcHits[4] = new adc( a, (RAMFunctionsHit)ReadHit0 );
	} else if (maxHits == 6) {
		adcHits[0] = new adc( a, (RAMFunctionsHit)ReadHit5 );
		adcHits[1] = new adc( a, (RAMFunctionsHit)ReadHit4 );
		adcHits[2] = new adc( a, (RAMFunctionsHit)ReadHit3 );
		adcHits[3] = new adc( a, (RAMFunctionsHit)ReadHit2 );
		adcHits[4] = new adc( a, (RAMFunctionsHit)ReadHit1 );
		adcHits[5] = new adc( a, (RAMFunctionsHit)ReadHit0 );
	} else if (maxHits == 8) {
		adcHits[0] = new adc( a, (RAMFunctionsHit)ReadHit7 );
		adcHits[1] = new adc( a, (RAMFunctionsHit)ReadHit6 );
		adcHits[2] = new adc( a, (RAMFunctionsHit)ReadHit5 );
		adcHits[3] = new adc( a, (RAMFunctionsHit)ReadHit4 );
		adcHits[4] = new adc( a, (RAMFunctionsHit)ReadHit3 );
		adcHits[5] = new adc( a, (RAMFunctionsHit)ReadHit2 );
		adcHits[6] = new adc( a, (RAMFunctionsHit)ReadHit1 );
		adcHits[7] = new adc( a, (RAMFunctionsHit)ReadHit0 );
	} else {
		std::cout << "Invalid number of maximum hits!  Only 1, 5, 6, or 8 are accepted right now!" << std::endl;
		if (febAppender!=0) febLog.fatalStream() << 
			"Invalid number of maximum hits!  Only 1, 5, 6, or 8 are accepted right now!";
		exit(-1);		
	}
	if (febAppender!=0) {
		febLog.infoStream() << "Created a new FEB! " << (int)febNumber[0];
		febLog.infoStream() << "  BoardNumber = " << boardNumber;
		febLog.infoStream() << "  Max hits    =  "<< maxHits;
	}
}


void feb::MakeShortMessage()
{
/*! \fn ********************************************************************|
 * MakeShortMessage uses FPGA Dump Read instead of the regular Read.        |
 ***************************************************************************|
 */
	// Update the header for this frame (frames default to read). 
	Devices dev     = FPGA;          //the device type for the header
	Broadcasts b    = None;          //broadcast type for header
	Directions d    = MasterToSlave; //message direction for header
	FPGAFunctions f = DumpRead;      //operation to be performed
	// Compose the transmission FPGA header
	MakeDeviceFrameTransmit(dev, b, d, f, (unsigned int)febNumber[0]);  

	// the header + information part of the message 
	OutgoingMessageLength = MinHeaderLength;              //length of the outgoing message message

	// Make a new out-going message buffer of suitable size.
	outgoingMessage = new unsigned char [OutgoingMessageLength];  
												
	// Eschew the local "non-dyamic" (for lack of a better description)
	// copy of the message buffer (dynamic).  May not work right?...
	// Put the message in the inherited out-going message bufer.
	for (int i=0;i<(OutgoingMessageLength);i++) { 
		outgoingMessage[i] = frameHeader[i];
	}
}

void feb::MakeMessage() 
{
/*! \fn ********************************************************************************
 * MakeMessage is the local implimentation of a virtual function of the same
 * name inherited from Frames.  This function bit-packs the data into an OUTGOING
 * message from values set using the get/set functions assigned to this class (see feb.h).
 *
 * The packing for v90 firmware is described below. Header takes up First 11 bytes.  
 * Registers start at indx==11.  See docdb 4311 for a description of the bit-by-bit packing.
 * Note that we must clean up the outgoingMessages in the functions that call MakeMessage!
 ********************************************************************************
 */
	// Message must have an odd number of bytes!
	message = new unsigned char [NRegisters + (NRegisters+1)%2]; 

	/* message word 0 - 3:  The timer information, 32 bits for the timer */
	message[0] = (Timer & 0xFF); //mask off bits 0-7
	message[1] = (Timer >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7 and mask off
	message[2] = (Timer >> 0x10) & 0xFF; //shift bits 16-23 to bits 0-7 and mask off
	message[3] = (Timer >> 0x18) & 0xFF; //shift bits 24-31 to bits 0-7 and mask off

	/* message word 4 - 5:  The gate start value, 16 bits */
	message[4] = (GateStart & 0xFF); //mask off bits 0-7
	message[5] = (GateStart >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7 and mask off 

	/* message word 6 - 7:  The gate length value, 16 bits */
	message[6] = (GateLength & 0xFF); //mask off bits 0-7
	message[7] = (GateLength >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7 and mask off

	/* message word 8 - 9, bit 0: DCM2 phase total, 9 bits */
	message[8] = (DCM2PhaseTotal & 0xFF); //mask off bits 0-7
	message[9] = (DCM2PhaseTotal >> 0x08) & 0x01; //shift bits 8-15 to bits 0-7 and mask off bit 0

	/* message word 9, bit 1: DCM2 phase done, 1 bit */
	message[9] |= (DCM2PhaseDone[0] & 0x01) << 0x01; //mask off bit 0 & shift left to bit 1

	/* message word 9, bit 2: DCM1 no clock, 1 bit */
	message[9] |= (DCM1NoClock[0] & 0x01) << 0x02; //mask off bit 0 & shift left to bit 2

	/* message word 9, bit 3: DCM2 no clock, 1 bit */
	message[9] |= (DCM2NoClock[0] & 0x01) << 0x03; //mask off bit 0 & shift left to bit 3

	/* message word 9, bit 4: DCM1 lock, 1 bit */
	message[9] |= (DCM1Lock[0] & 0x01) << 0x04; //mask off bit 0 & shift left to bit 4

	/* message word 9, bit 5: DCM1 lock, 1 bit */
	message[9] |= (DCM2Lock[0] & 0x01) << 0x05; //mask off bit 0 & shift left to bit 5

	/* message word 9, bit 6 - 7: Test Pules 2 Bit, 2 bits */
	message[9] |= (TestPulse2Bit[0] & 0x03) << 0x06; //mask off bit 0 & shift left to bit 6

	/* message word 10: Phase count, 8 bits */
	message[10] = PhaseCount[0];

	/* message word 11, bit 0: Ext. Trigger Found is readonly. */
	message[11] = (ExtTriggerFound[0] & 0x01); //mask off bit 0

	/* message word 11, bit 1: Ext. Trigger Rearm is readonly. */
	message[11] |= (ExtTriggerRearm[0] & 0x01) << 0x01; //mask off bit 0 and shift left to bit 1

	/* message word 11, bit 2: statusSCMDUnknown, 1 bit */
	message[11] |= (statusSCMDUnknown[0] & 0x01) << 0x02; //mask off bit 0 and shift left to bit 2

	/* message word 11, bit 3: statusFCMDUnknown, 1 bit */
	message[11] |= (statusFCMDUnknown[0] & 0x01) << 0x03; //mask off bit 1 and shift left to bit 3

	/* message word 11, bit 4: Phase increment, 1 bits */
	message[11] |= (PhaseIncrement[0] & 0x01) << 0x04; //mask off bit 0 and shift left to bit 4

	/* message word 11, bit 5: Phase start, 1 bits */
	message[11] |= (PhaseStart[0] & 0x01) << 0x05; //mask off bit 0 and shift left to bit 5

	/* message word 11, bit 6: statusRXLock, 1 bits */
	message[11] |= (statusRXLock[0] & 0x01) << 0x06; //mask off bit 0 and shift left to bit 6

	/* message word 11, bit 7: statusTXSyncLock, 1 bits */
	message[11] |= (statusTXSyncLock[0] & 0x01) << 0x07; //mask off bit 0 and shift left to bit 7

	/* message word 12 - 15: test pulse count */
	message[12] = (TestPulseCount & 0xFF); //mask off bits 0-7
	message[13] = (TestPulseCount >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7 & mask off
	message[14] = (TestPulseCount >> 0x10) & 0xFF; //shift bits 15-23 to bits 0-7 & mask off
	message[15] = (TestPulseCount >> 0x18) & 0xFF; //shift bits 24-31 to bits 0-7 & mask off

	/* message word 16 - 21 (bits 0-1): 
		The Injector counts 6 at 7 bits each, and the 8th bit of each word  is the enable status */
	for (int i=16;i<22;i++ ) {
		message[i] = InjectCount[(i-16)][0] & 0x7F; //mask off bits 0-6 (InjectCount)
		message[i] |= (InjectEnable[(i-16)][0] & 0x01) << 0x07; //mask off bit 0 (InjectEnable) and shift to bit 7
	}

	/* message word 22, bits 0-5:  trip power off, 1 bit for each trip 
	*     message word 22, bit 6: HV manual
	*     message word 22, bit 7: HV enabled */
	message[22] = TripPowerOff[0] & 0x3F; //mask off bits 0-5;
	message[22] |= (HVManual[0] & 0x01) << 0x06; //mask off bits 0, shift left 6
	message[22] |= (HVEnabled[0] & 0x01) << 0x07; //mask off bits 0, shift left 7

	/* message word 23-24: HV target value, 16 bits */
	message[23] = (HVTarget & 0xFF); //mask off bits 0-7
	message[24] = (HVTarget >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7. 
						//and mask off bits 0-7
	/* message word 25-26: HV actual value, 16 bits */
	message[25] = (HVActual & 0xFF); //mask off bits 0-7
	message[26] = (HVActual >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7. 
						//and mask off bits 0-7
	/* message word 27: AfterPulseExtendedWidth, 4 bits */
	//message[27] = (HVControl[0] & 0xFF); //mask off bits 0-7, HV Control is irrelevant for this (all firmwares).
	message[27] = (AfterPulseExtendedWidth[0] & 0x0F); //mask off bits 0-3, set 4-7 to zero (unused bits).

	/* message word 28-29, bits 0-3: Inject DAC value, 12 bits */
	message[28] = (InjectDACValue & 0xFF); //mask off bits 0-7
	message[29] = (InjectDACValue & 0x0F00) >> 8; //shift bits 8-11 to bits 0-3
							//and mask off bits 0-3
	/* message word 29, bits 4-7: InjectDACMode, 2 bits; InjectDACDone, 1 bit, 
	*     InjectDACStart, 1 bit */
	message[29] |= (InjectDACMode[0] & 0x03) << 0x04; //mask off bits 0-1 & shift left 4 bits
							// to bits 4-5
	message[29] |= (InjectDACDone[0] & 0x01) << 0x06; //mask off bits 0 & shift left 6 bits
							// to bit 6
	message[29] |= (InjectDACStart[0] & 0x01) << 0x07; //mask off bits 0 & shift left 7 bits
							// to bit 7
	/* message word 30: Inject range (bits 0-3), Inject phase (bits 4-7) */
	message[30] = (InjectRange[0] & 0x0F); //mask off bits 0-3
	message[30] |= (InjectPhase[0] & 0x0F) << 0x04; //mask off bits 0-3 and
							//shift left 4 bits to 4-7
	/* message word 31: BoardID (bits 0-3), HVNumAve (bits 4-6), and PreviewEnable (bit 7) */
	message[31] = (boardID[0] & 0x0F); //mask off bits 0-3
	message[31] |= (HVNumAve[0] & 0x07) << 0x04; //mask off bits 0-2 and shift left 4 bits to 4-6
	message[31] |= (PreviewEnable[0] & 0x01) << 0x07; //mask bit 1 and shift left 7 bits.

	/* message word 32:  Firmware version */
	message[32] = (FirmwareVersion[0] & 0xFF); //the firmware version is 8 bits

	/* message word 33 - 34: HV period manual, 16 bits */
	message[33] = (HVPeriodManual & 0xFF); //mask off bits 0-7
	message[34] = (HVPeriodManual >> 0x08) & 0xFF;  //shift bits 8-15 to bits 0-7
							//and mask off ibt 0-7
	/* message word 35 - 36: HV period auto, 16 bits */
	message[35] = (HVPeriodAuto & 0xFF); //mask off bits 0-7
	message[36] = (HVPeriodAuto >> 0x08) & 0xFF;  //shift bits 8-15 to bits 0-7
						//and mask off ibt 0-7
	/* message word 37: HV pulse width, 8 bits */
	message[37] = (HVPulseWidth[0] & 0xFF); //mask off bits 0-7

	/* message word 38 - 39: Temperature, 16 bits */
	message[38] = (Temperature & 0xFF); //mask off bits 0-7
	message[39] = (Temperature >> 0x08) & 0xFF;  //shift bits 8-15 to bits 0-7
						//and mask off ibt 0-7
	/* message word 40: TripX Thresh , 8 bits */
	message[40] = (TripXThresh[0] & 0xFF); //mask off bits 0-7

	/* message word 41: TripXCompEnc, 6 (+2 spare) bits */
	message[41] = (TripXCompEnc[0] & 0x3F); //mask off bits 0-5

	/* message word 42-43 Discriminator Enable Mask Trip 0, 16 bits */
	message[42] = (DiscrimEnableMask[0] & 0xFF); //mask off bits 0-7
	message[43] = (DiscrimEnableMask[0] >> 0x08); // shift right 8 bits and mask is redundant here

	/* message word 44-45 Discriminator Enable Mask Trip 1, 16 bits */
	message[44] = (DiscrimEnableMask[1] & 0xFF); //mask off bits 0-7
	message[45] = (DiscrimEnableMask[1] >> 0x08); // shift right 8 bits and mask is redundant here

	/* message word 46-47 Discriminator Enable Mask Trip 2, 16 bits */
	message[46] = (DiscrimEnableMask[2] & 0xFF); //mask off bits 0-7
	message[47] = (DiscrimEnableMask[2] >> 0x08); // shift right 8 bits and mask is redundant here

	/* message word 48-49 Discriminator Enable Mask Trip 3, 16 bits */
	message[48] = (DiscrimEnableMask[3] & 0xFF); //mask off bits 0-7
	message[49] = (DiscrimEnableMask[3] >> 0x08); // shift right 8 bits and mask is redundant here

	/* message word 50-53 Gate Time Stamp, 32 bits */
	message[50] = (GateTimeStamp & 0xFF); //mask off bits 0-7
	message[51] = (GateTimeStamp >> 0x08) & 0xFF; // shift right 8 bits and mask 
	message[52] = (GateTimeStamp >> 0x10) & 0xFF; // shift right 16 bits and mask 
	message[53] = (GateTimeStamp >> 0x18) & 0xFF; // shift right 24 bits and mask 

	// Make a new out-going message buffer of suitable size.
	outgoingMessage = new unsigned char [OutgoingMessageLength];  
												
	// Create a local "non-dyamic" (for lack of a better description)
	// copy of the message buffer (dynamic) for use in working around
	// a potential memory leak problems.  While mildly redundant, it 
	// doesn't really cause any speed issues either and it helps 
	// ensure that memory is cleaned up properly.
	unsigned char localMessage[OutgoingMessageLength]; 

	// Write the message to the localMessage buffer.
	for (int i=0;i<(OutgoingMessageLength);i++) { 
		if (i<MinHeaderLength) {
			localMessage[i]=frameHeader[i];
		} else {
			localMessage[i]=message[i-MinHeaderLength];
		}
	}
	// Put the message in the inherited out-going message bufer.
	for (int i=0;i<(OutgoingMessageLength);i++) { 
		outgoingMessage[i]=localMessage[i];
	}
	// Clean up memory.
	delete [] message; 
	// This finishes the outgoing message.
}


// TODO - ? Maybe... it isn't consistent that the FPGA frame function does not print the 
// register values while the discr and adc frame decode functions do... 
int feb::DecodeRegisterValues(int buffersize) 
{
/*! \fn********************************************************************************
 *  DecodeMessage takes the incoming message and unpacks the bits into the
 *  variables which hold the data.
 * The packing is described below.
 * inputs:
 *
 * \param buffersize:  the size of the total message, extracted from the dpm pointer 
 * register on the croc
 *********************************************************************************/

#if DEBUG_FEB
	std::cout << "BoardNumber--Decode: " << boardNumber << std::endl;
#endif
	// Check for errors
	if ((buffersize < TrueIncomingMessageLength)&&(initialized)) { 
		// The buffer is too short, so we need to stop execution, and notify the user!
		std::cout << "The FPGA buffer for FEB " << (int)febNumber[0]
			<< " is too short!" << std::endl;
		std::cout << " Expected: " << TrueIncomingMessageLength << std::endl;
		std::cout << " Had     : " << buffersize << std::endl;
		if (febAppender!=0) {
			febLog.critStream() << "The FPGA buffer for FEB " << (int)febNumber[0]
				<< " is too short!";
			febLog.critStream() << " Expected: " << TrueIncomingMessageLength;
			febLog.critStream() << " Had     : " << buffersize;
		}
		exit(1);
	} else if ((!initialized)&&(buffersize<TrueIncomingMessageLength)) {
		std::cout<<"FEB: "<<(int) febNumber[0]<<" is not available on this channel."<<std::endl;
		initialized = false;
	} else if ((!initialized)&&(buffersize==TrueIncomingMessageLength)) {
#if DEBUG_FEB 
		// Need a better mechanism for this...
		std::cout<<"FEB: "<<(int)febNumber[0]<<" is available on this channel."<<std::endl;
#endif
		initialized = true;
	}

	if (initialized) {
		/* have the frame check for status errors */
		int frameError = this->CheckForErrors();
#if DEBUG_VERBOSE
		std::cout << "\tfeb::DecodeRegisterValues CheckForErrors value = " << frameError << std::endl;
#endif

		if (!frameError) {
			int startByte = 2 + MinHeaderLength; //this should be byte 11
		
			/* message word 0 - 3:  The timer information, 32 bits for the timer */
			Timer = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			Timer |= (message[startByte] & 0xFF) << 0x08; //mask off and shift to bits 8-15 
			startByte++;
			Timer |= (message[startByte] & 0xFF) << 0x10; //mask off and shift to bits 16-23
			startByte++;
			Timer |= (message[startByte] & 0xFF) << 0x18; //mask off and shift to bits 24-31 

			/* message word 4 - 5:  The gate start value, 16 bits */
			startByte++;
			GateStart = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			GateStart |= (message[startByte] & 0xFF) << 0x08; //maks of and shift to bits 8-15  

			/* message word 6 - 7:  The gate length value, 16 bits */
			startByte++;
			GateLength = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			GateLength |= (message[startByte] & 0xFF) << 0x08; //mask of and shift to bits 8-15

			/* message word 8 - 9, bit 0: DCM2 phase total, 9 bits */
			startByte++;
			DCM2PhaseTotal = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			DCM2PhaseTotal |= (message[startByte] & 0x01) << 0x08; //mask of and shift to bits 8-15 

			/* message word 9, bit 1: DCM2 phase done, 1 bit */
			DCM2PhaseDone[0] = (message[startByte] & 0x02); //mask off bit 1

			/* message word 9, bit 2: DCM1 no clock, 1 bit */
			DCM1NoClock[0] = (message[startByte] & 0x04) >> 0x02; //mask off bit 2

			/* message word 9, bit 3: DCM2 no clock, 1 bit */
			DCM2NoClock[0] = (message[startByte] & 0x08) >> 0x03; //mask off bit 3

			/* message word 9, bit 4: DCM1 lock, 1 bit */
			DCM1Lock[0] = (message[startByte] & 0x10) >> 0x04; //mask off bit 4 

			/* message word 9, bit 5: DCM1 lock, 1 bit */
			DCM2Lock[0] = (message[startByte] & 0x20) >> 0x05; //mask off bit 5

			/* message word 9, bit 6 - 7: Test Pules 2 Bit, 2 bits */
			TestPulse2Bit[0] = (message[startByte] & 0xC0) >> 0x06; //mask off bit 6 & 7 

			/* message word 10: Phase count, 8 bits */
			startByte++;
			PhaseCount[0]= message[startByte];

			/* message word 11, bit 0: Ext. Trigger Found, 1 bit */
			startByte++;
			ExtTriggerFound[0] = (message[startByte] & 0x01); //mask off bit 0

			/* message word 11, bit 1: Ext. Trigger Rearm, 1 bit */
			ExtTriggerRearm[0] = (message[startByte] & 0x02) >> 0x01; //mask off bit 1

			/* message word 11, bit 2: statusSCMDUnknown, 1 bit */
			statusSCMDUnknown[0] = (message[startByte] & 0x04) >> 0x02; //mask off bits 1

			/* message word 11, bit 3: statusFCMDUnknown, 1 bit */
			statusFCMDUnknown[0] = (message[startByte] & 0x08) >> 0x03; //mask off bits 3

			/* message word 11, bit 4: Phase increment, 1 bits */
			PhaseIncrement[0] = (message[startByte]  & 0x10) >> 0x04; //mask off bit 4 

			/* message word 11, bit 5: Phase start, 1 bits */
			PhaseStart[0] = (message[startByte] & 0x20) >> 0x05; //mask off bit 5

			/* message word 11, bit 6: statusRXLock, 1 bits */
			statusRXLock[0] = (message[startByte] & 0x40) >> 0x06; //mask off bit 6

			/* message word 11, bit 7: statusTXSyncLock, 1 bits */
			statusTXSyncLock[0] = (message[startByte] & 0x80) >> 0x07; //mask off bit 7

			/* message word 12 - 15: test pules count */
			startByte++;
			TestPulseCount = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			TestPulseCount |= (message[startByte] & 0xFF) << 0x08; //mask off and shift to bits 8-15
			startByte++;
			TestPulseCount |= (message[startByte] & 0xFF) << 0x10; //mask off and shift to bits 15-23
			startByte++;
			TestPulseCount |= (message[startByte] & 0xFF) << 0x18; //mask off and shift to bits 24-31

			/* message word 16 - 21 (bits 0-1): 
				The Injector counts 6 at 7 bits each, and the 8th bit of each word is the enable status */
			int tmp=0;
			int tmp1=startByte+1; int tmp2 = startByte+6; //we need to sort out the injector bits
			for (int i=tmp1;i<=tmp2;i++ ) {
				InjectCount[tmp][0] = (message[i] & 0x7F); //mask off bits 0-6 (InjectCount)
				InjectEnable[tmp][0] = (message[i] & 0x80) >> 0x07;  //mask off bit 7 (InjectEnable)
				tmp++;
				startByte = i;
			}

			/* message word 22, bits 0-5:  trip power off, 1 bit for each trip 
			*     message word 22, bit 6: HV manual
			*     message word 22, bit 7: HV enabled*/
			startByte++;
			TripPowerOff[0] = (message[startByte] & 0x3F); //mask off bits 0-5;
			HVManual[0] = (message[startByte] & 0x40) >> 0x06; //mask off bits 6
			HVEnabled[0] = (message[startByte] & 0x80) >> 0x07; //mask off bits 7

			/* message word 23-24: HV target value, 16 bits */
			startByte++;
			HVTarget = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			HVTarget |= (message[startByte] & 0xFF) << 0x08; //mask & shift bits to 8-15  

			/* message word 25-26: HV actual value, 16 bits */
			startByte++;
			HVActual = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			HVActual |= (message[startByte] & 0xFF) << 0x08; //mask & shift bits to 8-15. 

			/* message word 27: HV control value, 8 bits */
			startByte++;
			HVControl[0] = 0; // Depricated in v90+, irrelevant in previous.
			AfterPulseExtendedWidth[0] = (message[startByte] & 0x0F); //mask off bits 0-3

			/* message word 28-29, bits 0-3: Inject DAC value, 12 bits */
			startByte++;
			InjectDACValue = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			InjectDACValue |= (message[startByte] & 0x0F) << 0x08; //shift bits 8-11 to bits 0-3
										//and mask off bits 0-3

			/* message word 29, bits 4-7: InjectDACMode, 2 bits; InjectDACDone, 1 bit, 
			*     InjectDACStart, 1 bit */
			InjectDACMode[0]  = (message[startByte] & 0x30) >> 0x04; //mask off bits 4 & 5 
			InjectDACDone[0]  = (message[startByte] & 0x40) >> 0x06; //mask off bits 6 
			InjectDACStart[0] = (message[startByte] & 0x80) >> 0x07; //mask off bits 7 

			/* message word 30: Inject range (bits 0-3), Inject phase (bits 4-7) */
			startByte++;
			InjectRange[0] = (message[startByte] & 0x0F); //mask off bits 0-3
			InjectPhase[0] = (message[startByte] & 0xF0) >> 0x04; //mask off bits 4-7 

			/* message word 31: BoardID (bits 0-3), HVNumAve (bits 4-6), and PreviewEnable (bit 7) */
			startByte++;
			boardID[0]       = (message[startByte] & 0x0F); //mask off bits 0-3
			HVNumAve[0]      = (message[startByte] & 0x70) >> 0x04; //mask off bits 4-6 & shift
			PreviewEnable[0] = (message[startByte] & 0x80) >> 0x07; //mask off bit 7 & shift

			/* message word 32:  Firmware version */
			startByte++;
			FirmwareVersion[0] = (message[startByte] & 0xFF); //the firmware version is 8 bits

			/* message word 33 - 34: HV period manual, 16 bits */
			startByte++;
			HVPeriodManual = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			HVPeriodManual |= (message[startByte] & 0xFF) << 0x08;  //shift bits to 8-15

			/* message word 35 - 36: HV period auto, 16 bits */
			startByte++;
			HVPeriodAuto = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			HVPeriodAuto |= (message[startByte] & 0xFF) << 0x08;  //shift bits to 8-15 

			/* message word 37: HV pulse width, 8 bits */
			startByte++;
			HVPulseWidth[0] = (message[startByte] & 0xFF); //mask off bits 0-7

			/* message word 38 - 39: Temperature, 16 bits */
			startByte++;
			Temperature = (message[startByte] & 0xFF); //mask off bits 0-7
			startByte++;
			Temperature |= (message[startByte] & 0xFF) << 0x08;  //shift bits 8-15 to bits 0-7
										//and mask off ibt 0-7

			/* message word 40: TripXThresh , 8 bits */
			startByte++;
			TripXThresh[0] = (message[startByte] & 0xFF); //mask off bits 0-7

			/* message word 41: whatever this is...TripXCompEnc, 6 bits */
			startByte++;
			TripXCompEnc[0] = (message[startByte] & 0x3F); //mask off bits 0-5

			/* message word 42-43 Discriminator Enable Mask Trip 0, 16 bits */
			/* message word 44-45 Discriminator Enable Mask Trip 1, 16 bits */
			/* message word 46-47 Discriminator Enable Mask Trip 2, 16 bits */
			/* message word 48-49 Discriminator Enable Mask Trip 3, 16 bits */
			for (int i=0; i<4; i++) {
				startByte++;
				DiscrimEnableMask[i] = (message[startByte] & 0xFF);
				startByte++;
				DiscrimEnableMask[i] |= (message[startByte] & 0xFF) << 0x08;                        
			}
		
			/* message word 50-53 Gate Time Stamp, 32 bits */
			startByte++;
			GateTimeStamp = (message[startByte] & 0xFF);                        
			startByte++;
			GateTimeStamp |= (message[startByte] & 0xFF) << 0x08;                        
			startByte++;
			GateTimeStamp |= (message[startByte] & 0xFF) << 0x10;                        
			startByte++;
			GateTimeStamp |= (message[startByte] & 0xFF) << 0x18;                        
		
		} else { // frame error check
			std::cout << "The FPGA frame had errors!" << std::endl;
			if (febAppender!=0) febLog.fatalStream() << "The FPGA frame had errors!";
			exit(1); 
		}

	} // end if initialized

#if DEBUG_FEB           
	std::cout << "Decoded FPGA register values:" << std::endl;
	ShowValues();   
#endif                  

	// This finishes the incoming message.
	return 0;
}


void feb::SetFEBDefaultValues() 
{
/*! \fn ********************************************************************************
 * Sets default (pre-defined) values for feb information.  These are hard-coded
 * in this function.  No real reason not to hard-code the default values unless
 * the situation arises where different FEB's would indeed need to have different
 * default values.  Then this would need to be changed.  There are a number of 
 * readonly registers initialized anyway (not all are marked with comments!).
 *********************************************************************************/
	Timer           = 12;
	GateStart       = 43300; // (65535 - 43300 ticks ) * 9.4 ns/tick ~ 209 us delay before gate open
	GateLength      = 1702;  // 1702 clock ticks * ~9.4 ns/tick ~ 15.999 us
	TripPowerOff[0] = 0x0;   // all on! // 0x3F; // all off
	for (int i=0;i<6;i++) {
		InjectCount[i][0]  = 0;
		InjectEnable[i][0] = 0;
	}
	InjectRange[0]    = 0;
	InjectPhase[0]    = 0;
	InjectDACValue    = 0;
	InjectDACMode[0]  = 0;
	InjectDACDone[0]  = 0;
	InjectDACStart[0] = 0;
	HVEnabled[0]      = 0;
	HVTarget          = 32768; // ~550 Volts?
	HVActual          = 0;
	HVControl[0]      = 0; // not used anymore in v90+ firmware...
	AfterPulseExtendedWidth[0] = 0;
	HVManual[0]          = 0;
	statusRXLock[0]      = 0; //actually readonly
	statusTXSyncLock[0]  = 0; //actually readonly
	PhaseStart[0]        = 0;
	PhaseIncrement[0]    = 0;
	ExtTriggerFound[0]   = 0; 
	ExtTriggerRearm[0]   = 0; 
	statusSCMDUnknown[0] = 0; //actually readonly
	statusFCMDUnknown[0] = 0; //actually readonly
	PhaseCount[0]        = 0;
	DCM1Lock[0]          = 0;
	DCM2Lock[0]          = 0;
	DCM1NoClock[0]       = 0;
	DCM2NoClock[0]       = 0;
	DCM2PhaseDone[0]     = 0;
	DCM2PhaseTotal       = 0;
	TestPulse2Bit[0]     = 0;
	TestPulseCount       = 0;
	boardID[0]           = 15; // readonly
	FirmwareVersion[0]   = 0;  // readonly
	HVNumAve[0]          = 0;
	PreviewEnable[0]     = 0;
	HVPeriodAuto         = 0;  // readonly
	HVPeriodManual       = 0;
	HVPulseWidth[0]      = 0;
	Temperature          = 0;  // readonly
	TripXThresh[0]       = 0;
	TripXCompEnc[0]      = 0;
	for (int i=0; i<4; i++) {DiscrimEnableMask[i]=0xFFFF;} // default to discr. enabled
	GateTimeStamp = 0; // readonly
#if DEBUG_FEB&&DEBUG_VERBOSE
	std::cout << "Default FPGA register values set." << std::endl;
	ShowValues();
#endif
}


void feb::ShowValues() 
{
/*! \fn **************************************************************************
 * Show the current values for the data members of an FEB.  
 *********************************************************************************/
	std::cout<<"************** FEB Current Values *******************"<<std::endl; 
	std::cout<<"Timer           : "<<Timer<<std::endl; 
	std::cout<<"GateStart       : "<<GateStart<<std::endl;
	std::cout<<"GateLength      : "<<GateLength<<std::endl; // in ~9.4 ns clock ticks
	std::cout<<"TripPowerOff    : "<<(int)TripPowerOff[0]<<std::endl;  
	for (int i=0;i<6;i++) {
		std::cout<<"Inject Count    : "<<(int)InjectCount[i][0]<<std::endl;;
		std::cout<<"Inject Enable   : "<<(int)InjectEnable[i][0]<<std::endl;
	}
	std::cout<<"Inject Range    : "<<(int)InjectRange[0]<<std::endl;;
	std::cout<<"Inject Phase    : "<<(int)InjectPhase[0]<<std::endl;;
	std::cout<<"Inject DACValue : "<<(int)InjectDACValue<<std::endl;;
	std::cout<<"Inject DACMode  : "<<(int)InjectDACMode[0]<<std::endl;;
	std::cout<<"Inject DACDone  : "<<(int)InjectDACDone[0]<<std::endl;;
	std::cout<<"Inject DACStart : "<<(int)InjectDACStart[0]<<std::endl;;
	std::cout<<"HVEnabled       : "<<(int)HVEnabled[0]<<std::endl;;
	std::cout<<"HVTarget        : "<<(int)HVTarget<<std::endl;;
	std::cout<<"HVActual        : "<<(int)HVActual<<std::endl;
	std::cout<<"AfterPulse Delay: "<<(int)AfterPulseExtendedWidth[0]<<std::endl;
	std::cout<<"HVManual        : "<<(int)HVManual[0]<<std::endl;
	std::cout<<"statusRXLock    : "<<(int)statusRXLock[0]<<std::endl;
	std::cout<<"statusTXSyncLock: "<<(int)statusTXSyncLock[0]<<std::endl;
	std::cout<<"PhaseStart      : "<<(int)PhaseStart[0]<<std::endl;
	std::cout<<"PhaseIncrement  : "<<(int)PhaseIncrement[0]<<std::endl;
	std::cout<<"ExtTriggerFound : "<<(int)ExtTriggerFound[0]<<std::endl; 
	std::cout<<"ExtTriggerRearm : "<<(int)ExtTriggerRearm[0]<<std::endl; 
	std::cout<<"StatusSCMDUnkwn : "<<(int)statusSCMDUnknown[0]<<std::endl;
	std::cout<<"StatusFCMDUnkwn : "<<(int)statusFCMDUnknown[0]<<std::endl;
	std::cout<<"PhaseCount      : "<<(int)PhaseCount[0]<<std::endl;
	std::cout<<"DCM1Lock        : "<<(int)DCM1Lock[0]<<std::endl;
	std::cout<<"DCM2Lock        : "<<(int)DCM2Lock[0]<<std::endl;
	std::cout<<"DCM1NoClock     : "<<(int)DCM1NoClock[0]<<std::endl;
	std::cout<<"DCM2NoClock     : "<<(int)DCM2NoClock[0]<<std::endl;
	std::cout<<"DCM2PhaseDone   : "<<(int)DCM2PhaseDone[0]<<std::endl;
	std::cout<<"DCM2PhaseTotal  : "<<(int)DCM2PhaseTotal<<std::endl;
	std::cout<<"TestPulse2Bit   : "<<(int)TestPulse2Bit[0]<<std::endl;
	std::cout<<"TestPulseCount  : "<<(int)TestPulseCount<<std::endl;
	std::cout<<"BoardID         : "<<(int)boardID[0]<<std::endl;
	std::cout<<"FirmwareVersion : "<<(int)FirmwareVersion[0]<<std::endl;
	std::cout<<"PreviewEnable   : "<<(int)PreviewEnable[0]<<std::endl;
	std::cout<<"HVNumAve        : "<<(int)HVNumAve[0]<<std::endl;
	std::cout<<"HVPeriodAuto    : "<<(int)HVPeriodAuto<<std::endl;
	std::cout<<"HVPeriodManual  : "<<(int)HVPeriodManual<<std::endl;
	std::cout<<"HVPulseWidth    : "<<(int)HVPulseWidth[0]<<std::endl;
	std::cout<<"Temperature     : "<<(int)Temperature<<std::endl;
	std::cout<<"TripXThresh     : "<<(int)TripXThresh[0]<<std::endl;
	std::cout<<"TripXCompEnc    : "<<(int)TripXCompEnc[0]<<std::endl;
	for (int i=0; i<4; i++) {
		printf("DiscrimEnabledMask[%d]: 0x%04X\n",i,DiscrimEnableMask[i]);
	}
	std::cout<<"GateTimeStamp   : "<<(unsigned int)GateTimeStamp<<std::endl; // only meaningful for 78+ firmware 
	std::cout<<"************* End FEB Current Values ****************"<<std::endl; 
}

// All of the Set functions that take unsigned char* need to be overloaded to take
// char* in order to be setable from the Python GUI (convert int->char in Python).

void feb::SetTripPowerOff(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetTripPowerOff(c);
}

void feb::SetInjectCount(char *a, int i)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetInjectCount(c,i);
}

void feb::SetInjectEnable(char *a, int i)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetInjectEnable(c,i);
}

void feb::SetInjectRange(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetInjectRange(c);
}

void feb::SetInjectPhase(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetInjectPhase(c);
}

void feb::SetInjectDACMode(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetInjectDACMode(c);
}

void feb::SetInjectDACStart(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetInjectDACStart(c);
}

void feb::SetHVEnabled(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetHVEnabled(c);
}

void feb::SetHVManual(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetHVManual(c);
}

void feb::SetPhaseStart(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetPhaseStart(c);
}

void feb::SetPhaseIncrement(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetPhaseIncrement(c);
}

void feb::SetPhaseCount(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetPhaseCount(c);
}

void feb::SetHVNumAve(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetHVNumAve(c);
}

void feb::SetHVPulseWidth(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetHVPulseWidth(c);
}

void feb::SetTripXThresh(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetTripXThresh(c);
}

void feb::SetExtTriggerRearm(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetExtTriggerRearm(c);
}

void feb::SetAfterPulseExtendedWidth(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetAfterPulseExtendedWidth(c);
}

void feb::SetPreviewEnable(char *a)
{
	unsigned char * c = reinterpret_cast<unsigned char *>(a);
	feb::SetPreviewEnable(c);
}
#endif
