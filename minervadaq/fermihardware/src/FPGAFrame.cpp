#ifndef FPGAFrame_cpp
#define FPGAFrame_cpp

#include "FPGAFrame.h"
#include "exit_codes.h"
/*********************************************************************************
 * Class for creating Front-End Board (FPGAFrame) objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

// log4cpp category hierarchy.
log4cpp::Category& FPGAFrameLog = log4cpp::Category::getInstance(std::string("FPGAFrame"));

FPGAFrame::FPGAFrame( febAddresses a ) : Frames() 
{
  /*! \fn********************************************************************************
   * The log-free constructor takes the following arguments:
   * \param a: The address (number) of the FPGAFrame
   * \param reg:  The number of one byte registers in the FPGAFrame message body
   *       The message body is set up for FPGAFrame Firmware Versions 78+ (54 registers).  
   *       It will need to be adjusted for other firmware versions. ECS & GNP
   */
  boardNumber  = a;      
  febNumber[0] = (unsigned char) a; 
  FPGAFrameLog.setPriority(log4cpp::Priority::DEBUG);  

  // Make the header for this frame; frames default to read. 
  Devices dev = FPGA;           // the device type for the header
  Broadcasts b = None;          // broadcast type for header
  Directions d = MasterToSlave; // message direction for header
  FPGAFunctions f = Read;       // operation to be performed
  // Compose the transmission FPGA header
  MakeDeviceFrameTransmit(dev, b, d, f, (unsigned int)febNumber[0]);  

  // the header + information part of the message 
  OutgoingMessageLength = MinHeaderLength + FPGANumRegisters; //length of the outgoing message message

  // Set default frame values (DOES NOT WRITE TO HARDWARE OR WRITE A MESSAGE, just configure properties).
  this->SetFPGAFrameDefaultValues();

  FPGAFrameLog.debugStream() << "Created a new FPGAFrame! " << (int)febNumber[0];
  FPGAFrameLog.debugStream() << "  BoardNumber = " << boardNumber;
  FPGAFrameLog.debugStream() << "  Max hits    =  "<< ADCFramesMaxNumber;
}

// careful, this changes the OutgoingMessageLength and can break things down the line
void FPGAFrame::MakeShortMessage()
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
  OutgoingMessageLength = MinHeaderLength;     //length of the outgoing message message

  // Make a new out-going message buffer of suitable size.
  outgoingMessage = new unsigned char [OutgoingMessageLength];  

  // Eschew the local "non-dyamic" (for lack of a better description)
  // copy of the message buffer (dynamic).  May not work right?...
  // Put the message in the inherited out-going message bufer.
  for (int i=0;i<(OutgoingMessageLength);i++) { 
    outgoingMessage[i] = frameHeader[i];
  }
}

void FPGAFrame::MakeMessage() 
{
  /*! \fn ********************************************************************************
   * MakeMessage is the local implimentation of a virtual function of the same
   * name inherited from Frames.  This function bit-packs the data into an OUTGOING
   * message from values set using the get/set functions assigned to this class (see FPGAFrame.h).
   *
   * The packing for v90 firmware is described below. Header takes up First 11 bytes.  
   * Registers start at indx==11.  See docdb 4311 for a description of the bit-by-bit packing.
   * Note that we must clean up the outgoingMessages in the functions that call MakeMessage!
   ********************************************************************************
   */
  // Message must have an odd number of bytes!
  message = new unsigned char [FPGANumRegisters + (FPGANumRegisters+1)%2]; 

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
int FPGAFrame::DecodeRegisterValues(int buffersize) 
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

#if DEBUG_FPGAFrame
  FPGAFrameLog.debugStream() << "BoardNumber--Decode: " << boardNumber << " for buffer size = " << buffersize;
#endif
  if ( buffersize < (int)FPGAFrameMaxSize ) { 

    // The buffer is too short, so we need to stop execution, and notify the user!
    FPGAFrameLog.fatalStream() << "The FPGA buffer for FPGAFrame " << (int)febNumber[0]
      << " is too short!";
    FPGAFrameLog.fatalStream() << " Expected: " << FPGAFrameMaxSize;
    FPGAFrameLog.fatalStream() << " Had     : " << buffersize;
    exit(EXIT_FEB_UNSPECIFIED_ERROR);

  } else {

    /* have the frame check for status errors */
    int frameError = this->CheckForErrors();
#if DEBUG_FPGAFrame
    FPGAFrameLog.debugStream() << "\tFPGAFrame::DecodeRegisterValues CheckForErrors value = " << frameError;
#endif

    if (!frameError) {
      FPGAFrameLog.debugStream() <<  "No frame errors; parsing...";
      int startByte = 2 + 2 + MinHeaderLength; //this should be byte 13 for CROC-E

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
      FPGAFrameLog.fatalStream() << "The FPGA frame had errors!";
      exit(EXIT_FEB_UNSPECIFIED_ERROR); 
    }

  } 

#if DEBUG_FPGAFrame           
  FPGAFrameLog.debugStream() << "Decoded FPGA register values.";
#endif                  

  // This finishes the incoming message.
  return 0;
}


void FPGAFrame::SetFPGAFrameDefaultValues() 
{
  /*! \fn ********************************************************************************
   * Sets default (pre-defined) values for FPGAFrame information.  These are hard-coded
   * in this function.  No real reason not to hard-code the default values unless
   * the situation arises where different FPGAFrame's would indeed need to have different
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
#if DEBUG_FPGAFrame&&DEBUG_VERBOSE
  FPGAFrameLog.debugStream() << "Default FPGA register values set.";
  ShowValues();
#endif
}


void FPGAFrame::ShowValues() 
{
  /*! \fn **************************************************************************
   * Show the current values for the data members of an FPGAFrame.  
   *********************************************************************************/
  FPGAFrameLog.debugStream()<<"************** FPGAFrame Current Values *******************"; 
  FPGAFrameLog.debugStream()<<"Timer           : "<<Timer; 
  FPGAFrameLog.debugStream()<<"GateStart       : "<<GateStart;
  FPGAFrameLog.debugStream()<<"GateLength      : "<<GateLength; // in ~9.4 ns clock ticks
  FPGAFrameLog.debugStream()<<"TripPowerOff    : "<<(int)TripPowerOff[0];  
  for (int i=0;i<6;i++) {
    FPGAFrameLog.debugStream()<<"Inject Count    : "<<(int)InjectCount[i][0];
    FPGAFrameLog.debugStream()<<"Inject Enable   : "<<(int)InjectEnable[i][0];
  }
  FPGAFrameLog.debugStream()<<"Inject Range    : "<<(int)InjectRange[0];
  FPGAFrameLog.debugStream()<<"Inject Phase    : "<<(int)InjectPhase[0];
  FPGAFrameLog.debugStream()<<"Inject DACValue : "<<(int)InjectDACValue;
  FPGAFrameLog.debugStream()<<"Inject DACMode  : "<<(int)InjectDACMode[0];
  FPGAFrameLog.debugStream()<<"Inject DACDone  : "<<(int)InjectDACDone[0];
  FPGAFrameLog.debugStream()<<"Inject DACStart : "<<(int)InjectDACStart[0];
  FPGAFrameLog.debugStream()<<"HVEnabled       : "<<(int)HVEnabled[0];
  FPGAFrameLog.debugStream()<<"HVTarget        : "<<(int)HVTarget;
  FPGAFrameLog.debugStream()<<"HVActual        : "<<(int)HVActual;
  FPGAFrameLog.debugStream()<<"AfterPulse Delay: "<<(int)AfterPulseExtendedWidth[0];
  FPGAFrameLog.debugStream()<<"HVManual        : "<<(int)HVManual[0];
  FPGAFrameLog.debugStream()<<"statusRXLock    : "<<(int)statusRXLock[0];
  FPGAFrameLog.debugStream()<<"statusTXSyncLock: "<<(int)statusTXSyncLock[0];
  FPGAFrameLog.debugStream()<<"PhaseStart      : "<<(int)PhaseStart[0];
  FPGAFrameLog.debugStream()<<"PhaseIncrement  : "<<(int)PhaseIncrement[0];
  FPGAFrameLog.debugStream()<<"ExtTriggerFound : "<<(int)ExtTriggerFound[0]; 
  FPGAFrameLog.debugStream()<<"ExtTriggerRearm : "<<(int)ExtTriggerRearm[0]; 
  FPGAFrameLog.debugStream()<<"StatusSCMDUnkwn : "<<(int)statusSCMDUnknown[0];
  FPGAFrameLog.debugStream()<<"StatusFCMDUnkwn : "<<(int)statusFCMDUnknown[0];
  FPGAFrameLog.debugStream()<<"PhaseCount      : "<<(int)PhaseCount[0];
  FPGAFrameLog.debugStream()<<"DCM1Lock        : "<<(int)DCM1Lock[0];
  FPGAFrameLog.debugStream()<<"DCM2Lock        : "<<(int)DCM2Lock[0];
  FPGAFrameLog.debugStream()<<"DCM1NoClock     : "<<(int)DCM1NoClock[0];
  FPGAFrameLog.debugStream()<<"DCM2NoClock     : "<<(int)DCM2NoClock[0];
  FPGAFrameLog.debugStream()<<"DCM2PhaseDone   : "<<(int)DCM2PhaseDone[0];
  FPGAFrameLog.debugStream()<<"DCM2PhaseTotal  : "<<(int)DCM2PhaseTotal;
  FPGAFrameLog.debugStream()<<"TestPulse2Bit   : "<<(int)TestPulse2Bit[0];
  FPGAFrameLog.debugStream()<<"TestPulseCount  : "<<(int)TestPulseCount;
  FPGAFrameLog.debugStream()<<"BoardID         : "<<(int)boardID[0];
  FPGAFrameLog.debugStream()<<"FirmwareVersion : "<<(int)FirmwareVersion[0];
  FPGAFrameLog.debugStream()<<"PreviewEnable   : "<<(int)PreviewEnable[0];
  FPGAFrameLog.debugStream()<<"HVNumAve        : "<<(int)HVNumAve[0];
  FPGAFrameLog.debugStream()<<"HVPeriodAuto    : "<<(int)HVPeriodAuto;
  FPGAFrameLog.debugStream()<<"HVPeriodManual  : "<<(int)HVPeriodManual;
  FPGAFrameLog.debugStream()<<"HVPulseWidth    : "<<(int)HVPulseWidth[0];
  FPGAFrameLog.debugStream()<<"Temperature     : "<<(int)Temperature;
  FPGAFrameLog.debugStream()<<"TripXThresh     : "<<(int)TripXThresh[0];
  FPGAFrameLog.debugStream()<<"TripXCompEnc    : "<<(int)TripXCompEnc[0];
  for (int i=0; i<4; i++) {
    FPGAFrameLog.debugStream() << "DiscrimEnabledMask[ " << i << "]: 0x" << std::hex << DiscrimEnableMask[i];
  }
  FPGAFrameLog.debugStream()<<"GateTimeStamp   : "<<(unsigned int)GateTimeStamp; // only meaningful for 78+ firmware 
  FPGAFrameLog.debugStream()<<"************* End FPGAFrame Current Values ****************"; 
}

// All of the Set functions that take unsigned char* need to be overloaded to take
// char* in order to be setable from the Python GUI (convert int->char in Python).
// -> SlowControl does not use those functions!

#endif
