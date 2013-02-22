#ifndef TRIPFrame_cpp
#define TRIPFrame_cpp

#include "TRIPFrame.h"
#include "exit_codes.h"
/*********************************************************************************
 * Class for creating Trip-t objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

log4cpp::Category& TRIPFrameLog = log4cpp::Category::getInstance(std::string("TRIPFrame"));

TRIPFrame::TRIPFrame(febAddresses a, TRiPFunctions f) : 
  LVDSFrame(),
  boardNumber(a),
  trip_function((unsigned char)f)
{
  /*! \fn
   * constructor takes the following arguments:
   * \param a: the FEB address to which this trip belongs
   * \param f: the Trip function (read or write)
   * \param maxHits: the maximum number of hits that can be serviced
   */
  TRIPFrameLog.setPriority(log4cpp::Priority::DEBUG);  // ERROR?

  TripTChipID[0] = 0x0A;              //the id number for the trip; they're all 10 for MINERvA
  TripTRead[0]   = 0x04;              //the read bit (1) is set
  TripTWrite[0]  = 0x01;              //the write bit (0) is set
  febNumber[0]   = (unsigned char) a; //feb number as a byte

  Devices dev      = TRiP;          // which device are we addressing
  Broadcasts broad = None;          // we don't broadcast to/from the TRIPFrame in MINERvA
  Directions dir   = MasterToSlave; // out-going is always master-to-slave
  MakeDeviceFrameTransmit(dev, broad, dir,(unsigned int)f, (unsigned int) febNumber[0]);   

  read = false; //the default position is that we are going to write information... uhhh...
  trip_values[0]  = (long_m)DefaultTripRegisterValues.tripRegIBP;
  trip_values[1]  = (long_m)DefaultTripRegisterValues.tripRegIBBNFOLL;
  trip_values[2]  = (long_m)DefaultTripRegisterValues.tripRegIFF;
  trip_values[3]  = (long_m)DefaultTripRegisterValues.tripRegIBPIFF1REF;
  trip_values[4]  = (long_m)DefaultTripRegisterValues.tripRegIBOPAMP;
  trip_values[5]  = (long_m)DefaultTripRegisterValues.tripRegIB_T;
  trip_values[6]  = (long_m)DefaultTripRegisterValues.tripRegIFFP2;
  trip_values[7]  = (long_m)DefaultTripRegisterValues.tripRegIBCOMP;
  trip_values[8]  = (long_m)DefaultTripRegisterValues.tripRegVREF;
  trip_values[9]  = (long_m)DefaultTripRegisterValues.tripRegVTH;
  trip_values[10] = (long_m)DefaultTripRegisterValues.tripRegPIPEDEL;
  trip_values[11] = (long_m)DefaultTripRegisterValues.tripRegGAIN;
  trip_values[12] = (long_m)DefaultTripRegisterValues.tripRegIRSEL;
  trip_values[13] = (long_m)DefaultTripRegisterValues.tripRegIWSEL;
  trip_values[14] = (long_m)0; 
}


void TRIPFrame::EncodeRegisterValues() 
{
  /*! \fn 
   *
   * OK, this is a little tricky.  It would seem that 
   * in order to provide the trip-t's with information,
   * we need to pack the bits of data into 4-bit chunks in 
   * 8-bit bytes (the smallest available unit).  This leads to 
   * a lot of words...Anyway, the 4-bits for each chunk of data 
   * contain the following information: \n
   *   bit 0:  Control bit  \n
   *   bit 1:  Clock bit \n
   *   bit 2:  Data Bit \n
   *   bit 3:  Reset \n
   *
   * Each piece of honest-to-goodness data seems to have two words attached
   * per bit, one with the clock bit "true" and the other with the clock 
   * bit "false".
   *
   * Also, the register values seem to be packed from least significant bit 
   * to most significant bit, while the register address is packed
   * most significant bit to least significant bit.
   *
   * I'm so confused.
   *
   * All information is packed up this way.  This is a little tedious,
   * but such is life, what can you do.
   *
   * That said here's what we're gonna do... \n
   *   0)  Make a temporary STL vector to build up the array \n
   *   1)  Build a function to put those 4 bits into a byte (PackBits) \n
   *   2)  Make a function to sort & set data bits (SortNSet) \n
   *   3)  Copy the vector to the buffer array. \n
   *       (this may be redundant, but I think being a little  \n
   *        parochial might not be too bad for this one) \n
   *        */

  //we need some flexibility in the packing array, so we'll use an STL list 
  std::vector<unsigned char> packTripData;  
  /* now we're ready to loop over the values & pack them into the register value array
   * this step is necessary because some of the registers hold multiple values. */
  long_m mask = 0xFF; //mask of 8 bits

  if (read) { //we don't need to fill the registers with anything if we're going to read out the data.
    for (int i=0;i<14;i++) {
      trip_registers[i]=0; //initialize the registers
    }
  } else { //bit-back the values set by people into trip-usable form
    for (int i=0; i<14;i++) {
      if ((i==10)||(i==11)||(i==12)||(i==13)) continue;
      trip_registers[i] = (trip_values[i] & mask);  //most of the rest
    }
    /* these two registers are combinations of 2 values, they need to be handled separately */
    trip_registers[10] = (trip_values[10] & 0x3F) | ((trip_values[11] & 0x0F) << 6); //gain & pipe delay
    trip_registers[11] = (trip_values[13] & 0x03) | ((trip_values[12] & 0x03) << 2); //drive currents
    trip_registers[12] = (long_m) 0; //unused register (by user)
#if SYS_32
    trip_registers[13] = ( trip_values[14] & 0x3FFFFFFFFULL); //inject value
#else
    trip_registers[13] = ( trip_values[14] & 0x3FFFFFFFF); //inject value - real mask is 0x1FFFFFFFE 
#endif
  }
#if DEBUG_FEB
  TRIPFrameLog.debugStream() << "In TRIPFrame::EncodeRegisterValues... PHYSICAL REGISTERS:";
  for (int i=0;i<14;i++) {
    if ( (i!=12) && (i!=13) ) {
      TRIPFrameLog.debugStream()<<"trip_register: "<<i+1<<" "<<(int)trip_registers[i];
    } else if (i==12) {
      TRIPFrameLog.debugStream()<<"trip_register: "<<i+1<<" "<<(int)trip_registers[i]<<" (unused)";			
    } else if (i==13) {
      TRIPFrameLog.debugStream()<<"trip_register: "<<i+1<<" "<<(int)trip_registers[i]<<" (inject)";			
    }
  }
#endif

  /* now load up the list with the words for each register value */
  for (int i=0;i<14;i++) {
    if (i==12) continue; //register 13 (when counting from 1) is not used
    if (i==13 && read) continue; //try a cheap and easy way of making sure we don't try to read the inj reg.
    long_m registerAddress = i+1; //we start counting at 0 (zero) but the registers start at 1 (one)
    PackBits(false, false, false, false, packTripData);
    PackBits(true, false, false, false, packTripData);
    SortNSet(false, (long_m) TripTChipID[0], 5, true, false, packTripData);
    SortNSet(false, registerAddress, 5, true, false, packTripData); //probably should tell the chips which register we'd like to set
    if (read) {  //flip the read & write bits
      SortNSet(false, (long_m) TripTRead[0], 3, true, false, packTripData);
    } else {
      SortNSet(false, (long_m) TripTWrite[0], 3, true, false, packTripData);
    }
    PackBits(true, true, false, false, packTripData);
    PackBits(true, false, false, false, packTripData);
    switch (i) {
      case 10:
        SortNSet(false, trip_registers[i], 10, true, true, packTripData);
        break;
      case 11:
        SortNSet(false, trip_registers[i], 4, true, true, packTripData);
        break;
      case 13:
        SortNSet(false, trip_registers[i], 34, true, true, packTripData);
        break;
      default:
        SortNSet(false, trip_registers[i], 8, true, true, packTripData);
        break;
    }
    PackBits(true, false, false, false, packTripData);
    PackBits(false, false, false, false, packTripData);
    PackBits(false, true, false, false, packTripData);
    PackBits(false, false, false, false, packTripData);
    PackBits(false, true, false, false, packTripData);
    PackBits(false, false, false, false, packTripData);
    PackBits(false, false, false, false, packTripData);
    /* check to make sure we have an odd number of bytes */
    if (((packTripData.size()) % 2) != 1 )
      PackBits(false, false, false, false, packTripData);
  }
  bufferSize = (int)packTripData.size(); //having packed the bits into the vector we now want to 
  //put them into the message buffer.  It made sense at the time

  buffer = new unsigned char [bufferSize];
  for (int i=0;i<bufferSize; i++ ) {
    buffer[i]=packTripData[i];
  }
}


void TRIPFrame::PackBits(bool control, bool clock, bool data, bool reset, std::vector<unsigned char> &l) 
{
  /*! \fn 
   * note we're setting one bit of a string of data bits into a for bits of an 8 bit bit string to 
   *  encode the entire bit string of the piece of data.  
   */

  unsigned char bitmask = 0x01; //mask off one bit
  unsigned char packMe = 0; //we need a temp to hold the bits

  packMe = ((unsigned char) control) & bitmask; //control goes in bit 0
  packMe |= (((unsigned char) clock) & bitmask) << 1; //clock goes in bit 1
  packMe |= (((unsigned char) data) & bitmask) << 2; //data bit goes in bit 2
  packMe |= (((unsigned char) reset) & bitmask) << 3; //reset goes in bit 3

  l.push_back(packMe);

  return;
}


void TRIPFrame::SortNSet(bool reset, long_m data, int bits, bool control, bool lowToHigh, 
    std::vector<unsigned char> &l) 
{
  /*! \fn
   * this sorts a multi-bit number into its bits, then packs them. 
   */

  if (lowToHigh) { 
    long_m bitmask = 0x01; //mask off first bit
    /* for the values of the register (not the address) we pack the bits from low to high */
    for (int i=0;i<bits;i++) { //loop over the number of bits in this data
      bool maskdata = ((data & bitmask) != 0);
      PackBits(control, true, maskdata, reset, l); 
      PackBits(control, false, maskdata, reset, l);
      bitmask <<= 1; //shift the mask to the next bit
    }
  } else {
    long_m bitmask = (0x01 << (bits-1)); //mask off first bit
    /* this goes the other way... */
    for (int i=0;i<bits;i++) { //loop over the number of bits in this data
      bool maskdata = ((data & bitmask) != 0);
      PackBits(control, true, maskdata, reset, l); 
      PackBits(control, false, maskdata,reset, l); 
      bitmask >>= 1; //shift the mask to the next bit
    }
  }
  return;
}


int TRIPFrame::DecodeRegisterValues(int messageLength) 
{
  /*! \fn 
   *  This function decodes an incoming message into the values of the
   *  particular settings on a trip.  It returns a success integer (0 for 
   *  success).
   *
   *  Input:
   *  \param messageLength:  the length of the incoming message as produred from the 
   *  \param dpm pointer register on the croc
   */
  int error = CheckForErrors(); //check the header of the frame for errors
  if (!error) { //if there are none, we're off to the races
    int startByte = 11; //remember that ALL incoming headers are 11 bytes long 
    int index = startByte;
    for (int j=0;j<14;j++) { // loop here is really over *physical* registers (1...12), note j+1's below..
      if ((j==12)||(j==13)) continue; // These regisers are either not used or not readable.
      // This initial piece is some kind of error checking? 
      // It takes up the first 31 bytes (yes bytes) after the data begins.
      if (message[index] != 0x00) ParseError(j+1, index);
      index++;
      if (message[index] != 0x01) ParseError(j+1, index);
      for (int k=0;k<14;k++) {
        index++;
        if (message[index] != 0x03) ParseError(j+1, index);
        index++;
        if (message[index] != 0x01) ParseError(j+1, index);
      }
      index++;
      if (message[index] != 0x03) ParseError(j+1, index);
      index++;
      // thus endith the header stuff; now for the actual data!
      switch (j) {
        case 10:
          GetRegisterValue(j,index, 10); //GAINPIPEDEL
          break;
        case 11:
          GetRegisterValue(j,index, 4); //IRSELIWSEL
          break;
        default:
          GetRegisterValue(j,index, 8); 
          break;
      }  
      // and then the tail stuff...
      if ((message[index] & 0x03) != 0x00) ParseError(j+1, index);
      index++;
      if ((message[index] & 0x03) != 0x02) ParseError(j+1, index);
      index++;
      if (message[index] != 0x00) ParseError(j+1, index);
      index++;
      if (message[index] != 0x02) ParseError(j+1, index);
      index++;
      if (message[index] != 0x00) ParseError(j+1, index);
      index++;
      if (message[index] != 0x00) ParseError(j+1, index);
      index++;
      if ((index%2) == 1) {
        if (message[index] != 0x00) ParseError(j+1, index);
        index++;
      }
      // Finished with the register...
    }
  } else {
    TRIPFrameLog.debugStream() << "Errors Found in Trip Message";
    return 1;
  }
  return 0;
}


void TRIPFrame::GetRegisterValue(int j, int &index, int bits) {
  /*! \fn
   *  This function extracts a given register value and puts it into the appropriate
   *  data member for this trip
   *
   *  Input:
   *  \param j:   the register being worked on (reasigned to registerIndex)
   *  \param index: a pointer to the array index in the message
   *  \param bits: the number of bits that need to be decoded/extracted
   */
  int registerIndex = j; //the register being extracted
  long_m value = 0; //a temp to "build up" the register's value
  unsigned char dataMask[1] = {0x01 << trip_function}; //the data mask bit for this trip function
  unsigned char sysMask[1] = {0x03}; //another data mask 

  for (int i=0;i<bits;i++) { //loop to extract the message given the number of bits to extract
    value <<=1;
    unsigned char byte[2];
    byte[0] = message[index];
    index++;
    byte[1] = message[index];
    if (((byte[0] & sysMask[0]) != 0x01) || 
        ((i < (bits-1)) && ((byte[1] & sysMask[0]) != 0x03)) ||
        ((i == (bits-1)) && ((byte[1] & sysMask[0])  != 0x01)) ||
        ((byte[0] & dataMask[0]) != (byte[1] & dataMask[0]))) ParseError(index-2);
    if ((byte[0] & dataMask[0]) != 0) value |= 0x01;
    index++;
  }

  switch (registerIndex) {
    case 10: //GAINPIPEDEL
      trip_values[10] = value & 0x3F;  // pipe delay
      trip_values[11] = (value >> 6) & 0x0F; // gain
      break;
    case 11: // IRSELIWSEL
      trip_values[12] = (value >> 2) & 0x03; // irsel
      trip_values[13] = value & 0x03; // iwsel
      break;
    default:
      trip_values[registerIndex] = value;
      break;
  }
}


void TRIPFrame::ParseError(int i, int j) 
{
  /*! \fn ********************************************************************************
   *  This function raises an error if the message being processed contains
   *  "bad" data.
   * 
   *  Inputs:
   *  \param i: register being worked on
   *  \param j: message array index
   */
  TRIPFrameLog.debugStream() << "Parse Error for register: " << i << " at index: " << j;
  exit(EXIT_FEB_UNSPECIFIED_ERROR);
}


void TRIPFrame::ParseError(int i) 
{
  /*! \fn
   *  This function raises an error if the message being processed contains
   *  "bad" data.
   *
   *  Inputs:
   *  \param i: message array index
   */
  TRIPFrameLog.debugStream() << "Parse Error at index: " << i << " while getting register value.";
  exit(EXIT_FEB_UNSPECIFIED_ERROR);
}


void TRIPFrame::MakeMessage() 
{
  /*! \fn
   * MakeMessage is the local implimentation of a virtual function of the same
   * name inherited from Frames.  This function bit-packs the data into an OUTGOING
   * message.
   */
  EncodeRegisterValues(); //sets the register values to these defaults
  int messageSize = MinHeaderLength+bufferSize;  //set the message size
  OutgoingMessageLength = messageSize;
  unsigned char localMessage[messageSize]; //local buffer copy for memory management issues
  outgoingMessage = new unsigned char [messageSize]; //the final outgoing message

  //load up the local copy
  for (int i=0;i<MinHeaderLength; i++) {
    localMessage[i]=frameHeader[i];
  }
  for (int i=MinHeaderLength;i<messageSize;i++) {
    localMessage[i] = buffer[i-MinHeaderLength];
  }

  //write this to the frame outgoing message
  for (int i=0;i<messageSize; i++) {  
    outgoingMessage[i]=localMessage[i];
  }
  delete [] buffer; //clean up the memory

}

#endif

