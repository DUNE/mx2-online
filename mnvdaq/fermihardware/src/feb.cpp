#ifndef feb_cpp
#define feb_cpp
 
#include "feb.h"
/*********************************************************************************
 * Class for creating Front-End Board (FEB) objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * April 22, 2009
 *
 **********************************************************************************/

 feb::feb(int mh, bool init, febAddresses a,int reg, std::ofstream &log_file):NRegisters(reg),Frames(log_file) {
//feb::feb(int mh, bool init, febAddresses a,int reg):NRegisters(reg) {
  /*! \fn********************************************************************************
 * constructor takes the following arguments:
 * \param mh: maximum number of hits per tdc
 * \param init: the FEB is initialized (i.e. an FEB is available)
 * \param a: The address (number) of the feb
 * \param reg:  The number of one byte registers in the FEB message body
 *       The message body is set up for FEB Firmware Versions 65 (42 registers) & 78-80 (54 registers).  
 *       It will need to be adjusted for other firmware versions. ECS & GNP
 *********************************************************************************/
  maxHits = mh; //maximum number of hits
  initialized = false;  //frames are not initialized by default
  boardNumber = a;  //feb address (also called board number)
  febNumber[0] = (unsigned char) a; //put the feb number into it's character.

  /* make up the header for this frame, frames default to read */
  Devices dev = FPGA; //the device type for the header
  Broadcasts b = None; //broadcast type for header
  Directions d = MasterToSlave; //message direction for header
  FPGAFunctions f = Read; //operation to be performed; options are read and write
  
  MakeDeviceFrameTransmit(dev, b, d, f, (unsigned int)febNumber[0]);  //make up the transmission FPGA header
  
  /* the header + information part of the message */
  OutgoingMessageLength = MinHeaderLength + NRegisters; //length of the outgoing message message
  TrueIncomingMessageLength = 2 + MinHeaderLength + NRegisters + (NRegisters + 1) % 2; //the length of the incoming message
  std::cout<<"Outgoing: "<<OutgoingMessageLength<<std::endl;
  std::cout<<"Incoming: "<<TrueIncomingMessageLength<<std::endl;
  /* note above: incoming messages are ALWAYS 2 bytes LARGER than outgoing messages */

  /* make up the frames for each of the trip chips on the board.
 *  We'll initialize them in the appropriate step.
 *  Each FEB has 6 and only 6 Trip-t's unless the engineering physically changes.
 *  There is NO NEED to make this dynamic, EVER!!  Even if the engineering physically changes! */

  for (int i=0;i<6;i++) { //loop over possible trips
    TRiPFunctions chipFunction;
    switch (i) {  //assign the trip function to make up the trip object
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
        std::cout<<"Just Don't Go There!"<<std::endl;
        exit(1);
    }
     tripChips[i] = new trips(boardNumber,chipFunction,maxHits,log_file); //make up the trip object
    //tripChips[i] = new trips(boardNumber,chipFunction,maxHits); //make up the trip object
  }
   hits_n_timing = new disc(a,log_file); //doesn't really do anything just yet
  //hits_n_timing = new disc(a); //doesn't really do anything just yet
  for (int i=0;i<maxHits;i++) { //we're going to make up maxHits worth of outgoing frames
    RAMFunctionsHit nhit;
    switch ((i+1)) {
      case (ReadHit0):
        nhit = ReadHit0;
        break;
      case (ReadHit1):
        nhit = ReadHit1;
        break;
      case (ReadHit2):
        nhit = ReadHit2;
        break;
      case (ReadHit3):
        nhit = ReadHit3;
        break;
      case (ReadHit4):
        nhit = ReadHit4;
        break;
      case (ReadHit5):
        nhit = ReadHit5;
        break;
    }
    #if DEBUG_FEB
      std::cout<<"Max hits: "<<maxHits<<std::endl;
    #endif
     adcHits[i] = new adc(a,nhit,log_file); //log this object
    //adcHits[i] = new adc(a,nhit); //log this object
  }
  #if DEBUG_FEB  
    std::cout<<"Created a new FEB! "<<(int) febNumber[0]<<std::endl;
    std::cout<<"BoardNumber "<<boardNumber<<std::endl;
  #endif
}

void feb::MakeMessage() {
  /*! \fn ********************************************************************************
 * MakeMessage is the local implimentation of a virtual function of the same
 * name inherited from Frames.  This function bit-packs the data into an OUTGOING
 * message from values set using the get/set functions assigned to this class (see feb.h).
 *
 * The packing is described below.
 ********************************************************************************

  now we'll pack the information into the message 
     the following scheme describes the numbers of bits assigned
     to each value: \n

    Timer,          // 32 bits \n
    GateStart,      // 16 bits \n
    GateLength,     // 16 bits \n
    TripPowerOff,   //  6 bits \n
    InjectCount0,   //  7 bits \n
    InjectCount1,   //  7 bits \n
    InjectCount2,   //  7 bits \n
    InjectCount3,   //  7 bits \n
    InjectCount4,   //  7 bits \n
    InjectCount5,   //  7 bits \n
    InjectEnable,   //  6 bits, one for each trip \n
    InjectRange,    //  4 bits \n
    InjectPhase,    //  4 bits \n
    InjectDACValue, // 12 bits \n
    InjectDACMode,  //  2 bits \n
    InjectDACStart, //  1 bit \n
    InjectDACDone,  //  1 bit, readonly \n
    HVEnabled,      //  1 bit \n
    HVTarget,       // 16 bits \n
    HVActual,       // 16 bits, readonly \n
    HVControl,      //  8 bits, readonly \n
    HVManual,       //  1 bit \n
    VXOOff,         //  1 bit \n
    VXOMuxXilinx,   //  1 bit \n
    PhaseStart,     //  1 bit \n
    PhaseIncrement, //  1 bit \n
    ExtTriggFound,      //  1 bit, readonly --> v78+; \n 
    ExtTriggRearm,      //  1 bit           --> v78+; \n
    PhaseSpare,     //  2 bits ignored in v78+ \n
    PhaseCount,     //  8 bits \n
    DCM1Lock,       //  1 bit, readonly \n
    DCM2Lock,       //  1 bit, readonly \n
    DCM1NoClock,    //  1 bit, readonly \n
    DCM2NoClock,    //  1 bit, readonly \n
    DCM2PhaseDone,  //  1 bit, readonly \n
    DCM2PhaseTotal, //  9 bits, readonly \n
    TestPulse2Bit,  //  2 bits, readonly \n
    TestPulseCount, // 32 bits, readonly \n
    BoardID,        //  4 bits, readonly in production version \n
    FirmwareVersion,//  4 bits, readonly \n
    HVNumAvg,       //  4 bits \n
    HVPeriodManual, // 16 bits \n
    HVPeriodAuto,   // 16 bits, readonly \n
    HVPulseWidth,   //  8 bits, readonly(?) - seems possible to write to it --> Definitely writeable! \n
                    // HVPulseWidth sets the power provided to the CCW -> do *not* go to 100!!! \n
    Temperature,    // 16 bits, readonly \n
    CosmicTrig,     //  8 bits \n
    TripXCompEnc,   //  8 bits \n
    ------------------------------ Version 65 firmware ends here. \n
    DiscrimEnableMaskTrip0,     // 16 bits, 1 enables the discim. for a pixel, 0 disables \n
    DiscrimEnableMaskTrip1,     // 16 bits, 1 enables the discim. for a pixel, 0 disables \n
    DiscrimEnableMaskTrip2,     // 16 bits, 1 enables the discim. for a pixel, 0 disables \n
    DiscrimEnableMaskTrip3,     // 16 bits, 1 enables the discim. for a pixel, 0 disables \n
    // Note no masks for trips 4 & 5 -> they are low gain and so don't have discriminators. \n
    GateTimeStamp,      // 32 bits, readonly \n
    ------------------------------ Version 78-80 firmware ends here. \n
    ------------------------------ Future Firmware Versions *MAY* also be compatible.  Check carefully! \n
    These are packed into the "message" variable */
 
    message = new unsigned char [NRegisters + (NRegisters+1)%2]; //message must have an odd number of bytes
    std::cout<<"NRegisters + (NRegisters+1)%2: "<<(NRegisters + (NRegisters+1)%2)<<std::endl;

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

    /* message word 11, bits 2 - 3: Phase spare, 2 bits */
    message[11] |= (PhaseSpare[0] & 0x03) << 0x02; //mask off bits 0-1 and shift left to bit 2

    /* message word 11, bit 4: Phase increment, 1 bits */
    message[11] |= (PhaseIncrement[0] & 0x01) << 0x04; //mask off bit 0 and shift left to bit 4

    /* message word 11, bit 5: Phase start, 1 bits */
    message[11] |= (PhaseStart[0] & 0x01) << 0x05; //mask off bit 0 and shift left to bit 5

    /* message word 11, bit 6: VXOMuxXilinx, 1 bits */
    message[11] |= (VXOMuxXilinx[0] & 0x01) << 0x06; //mask off bit 0 and shift left to bit 6

    /* message word 11, bit 7: VXOOff, 1 bits */
    message[11] |= (VXOOff[0] & 0x01) << 0x07; //mask off bit 0 and shift left to bit 7

    /* message word 12 - 15: test pulse count */
    message[12] = (TestPulseCount & 0xFF); //mask off bits 0-7
    message[13] = (TestPulseCount >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7 & mask off
    message[14] = (TestPulseCount >> 0x10) & 0xFF; //shift bits 15-23 to bits 0-7 & mask off
    message[15] = (TestPulseCount >> 0x18) & 0xFF; //shift bits 24-31 to bits 0-7 & mask off
  
    /* message word 16 - 21 (bits 0-1): The Injector counts 6 at 7 bits each, and the 8th bit of each word 
       is the enable status */
    for (int i=16;i<22;i++ ) {
      message[i] = InjectCount[(i-16)][0] & 0x7F; //mask off bits 0-6 (InjectCount)
      message[i] |= (InjectEnable[(i-16)][0] & 0x01) << 0x07;  //mask off bit 0 (InjectEnable)
                                                        //and shift to bit 7
    }

    /* message word 22, bits 0-5:  trip power off, 1 bit for each trip 
 *     message word 22, bit 6: HV manual
 *     message word 22, bit 7: HV enabled*/
    message[22] = TripPowerOff[0] & 0x3F; //mask off bits 0-5;
    message[22] |= (HVManual[0] & 0x01) << 0x06; //mask off bits 0, shift left 6
    message[22] |= (HVEnabled[0] & 0x01) << 0x07; //mask off bits 0, shift left 7
  
    /* message word 23-24: HV target value, 16 bits */
    message[23] = (HVTarget & 0xFF); //mask off bits 0-7
    message[24] = (HVTarget >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7. 
                                           //and mask off bits 0-7
                                           
    #if DEBUG_FEB
      std::cout<<(int) HVEnabled[0]<<" "<<HVTarget<<std::endl;
    #endif
    /* message word 25-26: HV actual value, 16 bits */
    message[25] = (HVActual & 0xFF); //mask off bits 0-7
    message[26] = (HVActual >> 0x08) & 0xFF; //shift bits 8-15 to bits 0-7. 
                                           //and mask off bits 0-7

    /* message word 27: HV control value, 8 bits */
    message[27] = (HVControl[0] & 0xFF); //mask off bits 0-7
 
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

    /* message word 31: BoardID (bits 0-3) and HVNumAve (bits 4-7) */
    message[31] = (boardID[0] & 0x0F); //mask off bits 0-3
    message[31] |= (HVNumAve[0] & 0x0F) << 0x04; //mask off bits 0-3 and
                                               //shift left 4 bits to 4-7

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
                                                  
    /* message word 40: cosmics trigger , 8 bits */
    message[40] = (CosmicTrig[0] & 0xFF); //mask off bits 0-7

    /* message word 41: whatever this is...TripXCompEnc, 8 bits */
    message[41] = (TripXCompEnc[0] & 0xFF); //mask off bits 0-7

//    if (NRegisters==54) { // Firmware versions 78-84
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
//    }

    outgoingMessage = new unsigned char [OutgoingMessageLength];  //make up the out-going message buffer
                                                 //of suitable size
    unsigned char localMessage[OutgoingMessageLength]; //a local "non-dyamic" (for lack of a better description)
                                                 //copy of the message buffer (dynamic) for use in working around
                                                 //a potential memory leak problems.
                                                 //While mildly redundant, it doesn't really cause any speed issues either
                                                 //and it ensures that memory is cleaned up properly.
    for (int i=0;i<(OutgoingMessageLength);i++) { //write message to localMessage buffer
      if (i<MinHeaderLength) {
        localMessage[i]=frameHeader[i];
      } else {
        localMessage[i]=message[i-MinHeaderLength];
      }
    }
    for (int i=0;i<(OutgoingMessageLength);i++) { //put the message in the inherited out-going message bufer
        outgoingMessage[i]=localMessage[i];
    }
    delete [] message; //clean up memory

/* this finishes off an outgoing message */
}

void feb::DecodeRegisterValues(int buffersize) {
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
    std::cout<<"BoardNumber--Decode: "<<boardNumber<<std::endl;
  #endif
  if ((buffersize < TrueIncomingMessageLength)&&(initialized)) { //check for errors
    /* the buffer is too short, so we need to stop execution, and notify the user */
    std::cout<<"The FPGA buffer for this FEB "<<(int)febNumber[0]
        <<" is too short"<<std::endl;
    std::cout<<"Expected: "<<TrueIncomingMessageLength<<std::endl;
    std::cout<<"Had: "<<buffersize<<std::endl;
    exit(1);
  } else if ((!initialized)&&(buffersize<TrueIncomingMessageLength)) {
    std::cout<<"FEB: "<<(int) febNumber[0]<<" is not available on this channel."<<std::endl;
    initialized = false;
  } else if ((!initialized)&&(buffersize==TrueIncomingMessageLength)) {
    std::cout<<"FEB: "<<(int)febNumber[0]<<" is available on this channel."<<std::endl;
    initialized = true;
  }

  if (initialized) {
    /* have the frame check for status errors */
    int frameError = this->CheckForErrors();
  
    if (!frameError) {
      int startByte = 2 + MinHeaderLength; //this should be byte 11
    /* now we'll unpack the information into the message 
       the following scheme describes the numbers of bits assigned
       to each value:

      Timer,          // 32 bits
      GateStart,      // 16 bits
      GateLength,     // 16 bits
      TripPowerOff,   //  6 bits
      InjectCount0,   //  7 bits
      InjectCount1,   //  7 bits
      InjectCount2,   //  7 bits
      InjectCount3,   //  7 bits
      InjectCount4,   //  7 bits
      InjectCount5,   //  7 bits
      InjectEnable,   //  6 bits, one for each trip
      InjectRange,    //  4 bits
      InjectPhase,    //  4 bits
      InjectDACValue, // 12 bits
      InjectDACMode,  //  2 bits
      InjectDACStart, //  1 bit
      InjectDACDone,  //  1 bit, readonly
      HVEnabled,      //  1 bit
      HVTarget,       // 16 bits
      HVActual,       // 16 bits, readonly
      HVControl,      //  8 bits, readonly
      HVManual,       //  1 bit
      VXOOff,         //  1 bit
      VXOMuxXilinx,   //  1 bit
      PhaseStart,     //  1 bit
      PhaseIncrement, //  1 bit
      ExtTriggFound,  //  1 bit -> Only meaningful in v78+ Firmware
      ExtTriggRearm,  //  1 bit -> Only meaningful in v78+ Firmware
      PhaseSpare,     //  2 bits
      PhaseCount,     //  8 bits
      DCM1Lock,       //  1 bit, readonly
      DCM2Lock,       //  1 bit, readonly
      DCM1NoClock,    //  1 bit, readonly
      DCM2NoClock,    //  1 bit, readonly
      DCM2PhaseDone,  //  1 bit, readonly
      DCM2PhaseTotal, //  9 bits, readonly
      TestPulse2Bit,  //  2 bits, readonly
      TestPulseCount, // 32 bits, readonly
      boardID,        //  4 bits, readonly in production version
      FirmwareVersion,//  4 bits, readonly
      HVNumAvg,       //  4 bits
      HVPeriodManual, // 16 bits
      HVPeriodAuto,   // 16 bits, readonly
      HVPulseWidth,   //  8 bits, readonly(?) - seems possible to write to it
      Temperature,     //  16 bits, readonly
      CosmicTrig,      // 8 bits
      TripXCompEnc     // 8 bits
      DiscriminatorEnableMaskTrip0 // 16 bits -> Only meaningful in v78+ Firmware
      DiscriminatorEnableMaskTrip1 // 16 bits -> Only meaningful in v78+ Firmware
      DiscriminatorEnableMaskTrip2 // 16 bits -> Only meaningful in v78+ Firmware
      DiscriminatorEnableMaskTrip3 // 16 bits -> Only meaningful in v78+ Firmware
      Gate Time Stamp // 32 bits -> Only meaningful in v78+ Firmware
        
      These are packed into the "message" variable */

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

    /* message word 11, bits 2 - 3: Phase spare, 2 bits */
    PhaseSpare[0] = (message[startByte] & 0x0C) >> 0x02; //mask off bits 2-3

    /* message word 11, bit 4: Phase increment, 1 bits */
    PhaseIncrement[0] = (message[startByte]  & 0x10) >> 0x04; //mask off bit 4 

    /* message word 11, bit 5: Phase start, 1 bits */
    PhaseStart[0] = (message[startByte] & 0x20) >> 0x05; //mask off bit 5

    /* message word 11, bit 6: VXOMuxXilinx, 1 bits */
    VXOMuxXilinx[0] = (message[startByte] & 0x40) >> 0x06; //mask off bit 6

    /* message word 11, bit 7: VXOOff, 1 bits */
    VXOOff[0] = (message[startByte] & 0x80) >> 0x07; //mask off bit 7

    /* message word 12 - 15: test pules count */
    startByte++;
    TestPulseCount = (message[startByte] & 0xFF); //mask off bits 0-7
    startByte++;
    TestPulseCount |= (message[startByte] & 0xFF) << 0x08; //mask off and shift to bits 8-15
    startByte++;
    TestPulseCount |= (message[startByte] & 0xFF) << 0x10; //mask off and shift to bits 15-23
    startByte++;
    TestPulseCount |= (message[startByte] & 0xFF) << 0x18; //mask off and shift to bits 24-31

    /* message word 16 - 21 (bits 0-1): The Injector counts 6 at 7 bits each, and the 8th bit of each word 
       is the enable status --- fix this first thing in the morning... */
    int tmp=0;
    int tmp1=startByte+1; int tmp2 = startByte+6; //we need to sort out the 
                                    //injector bits
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
    HVControl[0] = (message[startByte] & 0xFF); //mask off bits 0-7
 
    /* message word 28-29, bits 0-3: Inject DAC value, 12 bits */
    startByte++;
    InjectDACValue = (message[startByte] & 0xFF); //mask off bits 0-7
    startByte++;
    InjectDACValue |= (message[startByte] & 0x0F) << 0x08; //shift bits 8-11 to bits 0-3
                                                 //and mask off bits 0-3
    /* message word 29, bits 4-7: InjectDACMode, 2 bits; InjectDACDone, 1 bit, 
 *     InjectDACStart, 1 bit */
    InjectDACMode[0] = (message[startByte] & 0x30) >> 0x04; //mask off bits 4 & 5 
    InjectDACDone[0] = (message[startByte] & 0x40) >> 0x06; //mask off bits 6 
    InjectDACStart[0] = (message[startByte] & 0x80) >> 0x07; //mask off bits 7 

    /* message word 30: Inject range (bits 0-3), Inject phase (bits 4-7) */
    startByte++;
    InjectRange[0] = (message[startByte] & 0x0F); //mask off bits 0-3
    InjectPhase[0] = (message[startByte] & 0xF0) >> 0x04; //mask off bits 4-7 

    /* message word 31: BoardID (bits 0-3) and HVNumAve (bits 4-7) */
    startByte++;
    boardID[0] = (message[startByte] & 0x0F); //mask off bits 0-3
    HVNumAve[0] = (message[startByte] & 0xF0) >> 0x04; //mask off bits 4-7 and

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
                                                  
    /* message word 40: cosmics trigger , 8 bits */
    startByte++;
    CosmicTrig[0] = (message[startByte] & 0xFF); //mask off bits 0-7

    /* message word 41: whatever this is...TripXCompEnc, 8 bits */
    startByte++;
    TripXCompEnc[0] = (message[startByte] & 0xFF); //mask off bits 0-7

    if (NRegisters==54) { // Firmware versions 78-80
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
    } // endif NRegisters==54
        } else { // frame error check
      std::cout<<"The frame had errors."<<std::endl;
      exit(1); //force an exit
    }
        
  }

/* this finishes off an incoming message */
}

void feb::SetFEBDefaultValues() {
  /*! \fn ********************************************************************************
 * Sets default (pre-defined) values for feb information.  These are hard-coded
 * in this function.  No real reason not to hard-code the default values unless
 * the situation arises where different FEB's would indeed need to have different
 * default values.  Then this would need to be changed.
 *********************************************************************************/
  Timer = 12;
  GateStart = 65488;
  GateLength = 1024; // 1024 clock ticks * ~9.4 ns/tick ~ 9.6 us
  TripPowerOff[0] = 0x3F; // all off
  for (int i=0;i<6;i++) {
    InjectCount[i][0] = 0;
    InjectEnable[i][0] = 0;
  }
  InjectRange[0] = 0;
  InjectPhase[0] = 0;
  InjectDACValue = 0;
  InjectDACMode[0] = 0;
  InjectDACDone[0] = 0;
  InjectDACStart[0] = 0;
  HVEnabled[0] = 0;
  HVTarget = 32768;
  HVActual = 0;
  HVControl[0] = 0;
  HVManual[0] = 0;
  VXOOff[0] = 0;
  VXOMuxXilinx[0] = 1;
  PhaseStart[0] = 0;
  PhaseIncrement[0] = 0;
  ExtTriggerFound[0] = 0; // only meaningful for 78+ firmware 
  ExtTriggerRearm[0] = 0; // only meaningful for 78+ firmware 
  PhaseSpare[0] = 0;
  PhaseCount[0] = 0;
  DCM1Lock[0] = 0;
  DCM2Lock[0] = 0;
  DCM1NoClock[0] = 0;
  DCM2NoClock[0] = 0;
  DCM2PhaseDone[0] = 0;
  DCM2PhaseTotal = 0;
  TestPulse2Bit[0] = 0;
  TestPulseCount = 0;
  boardID[0] = 15;
  FirmwareVersion[0] = 0;
  HVNumAve[0] = 0;
  HVPeriodAuto = 0;
  HVPeriodManual = 0;
  HVPulseWidth[0] = 0;
  Temperature = 0;
  CosmicTrig[0] = 0;
  TripXCompEnc[0] = 0;
  for (int i=0; i<4; i++) {DiscrimEnableMask[i]=0xFFFF;} // default to discr. enabled, only meaningful for 78+ firmware
  GateTimeStamp = 0; // readonly, only meaningful for 78+ firmware 
#if DEBUG_FEB
  std::cout<<"Default FPGA register values set."<<std::endl;
  ShowValues();
#endif
}

void feb::ShowValues() {
  /*! \fn ********************************************************************************
 * Show the current values for the data members of an FEB.  Yeah, it's not the ideal
 * way to do it, but it does the job.
 *********************************************************************************/
  std::cout<<"***************************FEB Current Values*************************************"<<std::endl; 
  std::cout<<"Timer: "<<Timer<<std::endl; 
  std::cout<<"GateStart: "<<GateStart<<std::endl;
  std::cout<<"GateLength: "<<GateLength<<std::endl; // in ~9.4 ns clock ticks
  std::cout<<"TripPowerOff: "<<(int)TripPowerOff[0]<<std::endl;  
  for (int i=0;i<6;i++) {
    std::cout<<"Inject Count: "<<(int)InjectCount[i][0]<<std::endl;;
    std::cout<<"Inject Enable: "<<(int)InjectEnable[i][0]<<std::endl;
  }
  std::cout<<"Inject Range: "<<(int)InjectRange[0]<<std::endl;;
  std::cout<<"Inject Phase: "<<(int)InjectPhase[0]<<std::endl;;
  std::cout<<"Inject DACValue: "<<(int)InjectDACValue<<std::endl;;
  std::cout<<"Inject DACMode: "<<(int)InjectDACMode[0]<<std::endl;;
  std::cout<<"Inject DACDone: "<<(int)InjectDACDone[0]<<std::endl;;
  std::cout<<"Inject DACStart: "<<(int)InjectDACStart[0]<<std::endl;;
  std::cout<<"HVEnabled: "<<(int)HVEnabled[0]<<std::endl;;
  std::cout<<"HVTarget: "<<(int)HVTarget<<std::endl;;
  std::cout<<"HVActual: "<<(int)HVActual<<std::endl;
  std::cout<<"HVControl: "<<(int)HVControl[0]<<std::endl;
  std::cout<<"HVManual: "<<(int)HVManual[0]<<std::endl;
  std::cout<<"VXOOff: "<<(int)VXOOff[0]<<std::endl;
  std::cout<<"VXOMuxXilinx: "<<(int)VXOMuxXilinx[0]<<std::endl;
  std::cout<<"PhaseStart: "<<(int)PhaseStart[0]<<std::endl;
  std::cout<<"PhaseIncrement: "<<(int)PhaseIncrement[0]<<std::endl;
  std::cout<<"ExtTriggerFound: "<<(int)ExtTriggerFound[0]<<std::endl; // only meaningful for 78+ firmware 
  std::cout<<"ExtTriggerRearm: "<<(int)ExtTriggerRearm[0]<<std::endl; // only meaningful for 78+ firmware 
  std::cout<<"PhaseSpare: "<<(int)PhaseSpare[0]<<std::endl;
  std::cout<<"PhaseCount: "<<(int)PhaseCount[0]<<std::endl;
  std::cout<<"DCM1Lock: "<<(int)DCM1Lock[0]<<std::endl;
  std::cout<<"DCM2Lock: "<<(int)DCM2Lock[0]<<std::endl;
  std::cout<<"DCM1NoClock: "<<(int)DCM1NoClock[0]<<std::endl;
  std::cout<<"DCM2NoClock: "<<(int)DCM2NoClock[0]<<std::endl;
  std::cout<<"DCM2PhaseDone: "<<(int)DCM2PhaseDone[0]<<std::endl;
  std::cout<<"DCM2PhaseTotal: "<<(int)DCM2PhaseTotal<<std::endl;
  std::cout<<"TestPulse2Bit: "<<(int)TestPulse2Bit[0]<<std::endl;
  std::cout<<"TestPulseCount: "<<(int)TestPulseCount<<std::endl;
  std::cout<<"BoardID: "<<(int)boardID[0]<<std::endl;
  std::cout<<"FirmwareVersion: "<<(int)FirmwareVersion[0]<<std::endl;
  std::cout<<"HVNumAve: "<<(int)HVNumAve[0]<<std::endl;
  std::cout<<"HVPeriodAuto: "<<(int)HVPeriodAuto<<std::endl;
  std::cout<<"HVPeriodManual: "<<(int)HVPeriodManual<<std::endl;
  std::cout<<"HVPulseWidth: "<<(int)HVPulseWidth[0]<<std::endl;
  std::cout<<"Temperature: "<<(int)Temperature<<std::endl;
  std::cout<<"CosmicTrig: "<<(int)CosmicTrig[0]<<std::endl;
  std::cout<<"TripXCompEnc: "<<(int)TripXCompEnc[0]<<std::endl;
    for (int i=0; i<4; i++) {
        // definitely easiest to parse in hex...
        // only meaningful for 78+ firmware 
        std::cout<<"DiscrimEnableMask["<<i<<"]: "<<(int)DiscrimEnableMask[i]<<std::endl;        
    }
    std::cout<<"GateTimeStamp: "<<(unsigned int)GateTimeStamp<<std::endl; // only meaningful for 78+ firmware 
  std::cout<<"***************************End FEB Current Values*************************************"<<std::endl; 
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
void feb::SetInjectDACDone(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetInjectDACDone(c);
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
void feb::SetHVControl(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetHVControl(c);
}
void feb::SetHVManual(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetHVManual(c);
}
void feb::SetVXOOff(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetVXOOff(c);
}
void feb::SetVXOMuxXilinx(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetVXOMuxXilinx(c);
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
void feb::SetPhaseSpare(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetPhaseSpare(c);
}
void feb::SetPhaseCount(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetPhaseCount(c);
}
void feb::SetDCM1Lock(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetDCM1Lock(c);
}
void feb::SetDCM2Lock(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetDCM2Lock(c);
}
void feb::SetDCM1NoClock(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetDCM1NoClock(c);
}
void feb::SetDCM2NoClock(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetDCM2NoClock(c);
}
void feb::SetDCM2PhaseDone(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetDCM2PhaseDone(c);
}
void feb::SetTestPulse2Bit(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetTestPulse2Bit(c);
}
void feb::SetBoardID(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetBoardID(c);
}
void feb::SetFirmwareVersion(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetFirmwareVersion(c);
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
void feb::SetCosmicTrig(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetCosmicTrig(c);
}
void feb::SetTripXCompEnc(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetTripXCompEnc(c);
}
void feb::SetExtTriggerFound(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetExtTriggerFound(c);
}
void feb::SetExtTriggerRearm(char *a)
{
   unsigned char * c = reinterpret_cast<unsigned char *>(a);
   feb::SetExtTriggerRearm(c);
}

#endif
