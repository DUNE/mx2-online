#ifndef LVDSFrames_cpp
#define LVDSFrames_cpp

#include <iomanip>
#include "LVDSFrames.h"
#include "exit_codes.h"

/*********************************************************************************
 * Class for creating FPGA Frame header objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

/* const int LVDSFrames::MinHeaderLength=9; // renamed: FrameHeaderLengthOutgoing */

log4cpp::Category& lvdsLog = log4cpp::Category::getInstance(std::string("frames"));

//------------------------------------------
LVDSFrames::LVDSFrames() 
{ 
  FrameID[0] = 0x00; 
  FrameID[1] = 0x00; 
  lvdsLog.setPriority(log4cpp::Priority::DEBUG);
  IncomingMessageLength = OutgoingMessageLength = 0;
}

//------------------------------------------
void LVDSFrames::MakeDeviceFrameTransmit( Devices dev, Broadcasts b, Directions d, 
    unsigned int f, unsigned int feb ) 
{
  /*! \fn********************************************************************************
   * a function which makes up an FPGA frame for transmitting information from
   * the data acquisition routines to the FPGA on the front end board (FEB) and
   * on to the requested device.
   *
   * Inputs:
   *
   * \param dev:  The device to which the message is destined
   * \param b: whether or not this is a broadcast request
   * \param d: the direction of the message:  either master-to-slave (true for transmit) or
   *    slave-to-master (receive)
   * \param f: the device function.  This is specific to the device (dev) receiving the message
   * \param feb: the number of the FEB to which this frame is destined
   *********************************************************************************/

  broadcastCommand[0] = (unsigned char)b;
  messageDirection[0] = (unsigned char)d;
  targetDevice[0]     = (unsigned char)dev; 
  deviceFunction[0]   = (unsigned char)f;
  febNumber[0]        = (unsigned char)feb;

  MakeOutgoingHeader();
}

//------------------------------------------
void LVDSFrames::MakeOutgoingHeader() 
{
  /*! \fn********************************************************************************
   * a function which packs outgoing frame header data for transmitting information from
   * the data acquisition routines to the FPGA on the front end board (FEB) and
   * on to the requested device.
   *********************************************************************************/

  /* we've done all the conversion & stuff so we can make up the frame header now! */
  /* word 1: the broadcast direction, command, and feb number */
  frameHeader[0] = (messageDirection[0] & 0x80 ); // The direction bit is in bit 7 of word 1
  frameHeader[0] |= (broadcastCommand[0] & 0xF0); // The broadcast command is in bits 4-6
  frameHeader[0] |= (febNumber[0] & 0x0F);        // The feb number is bits 0-3

  /* word 2:  target device & its function */
  frameHeader[1] = (targetDevice[0] & 0xF0);     // The target device is in bits 4-7
  frameHeader[1] |= (deviceFunction[0] & 0x0F);  // The function is in bits 0-3

  /* word 3:  reserved for response information */
  frameHeader[2] = 0x00; //initialize to null

  /* word 4 & 5:  frame ID (whatever that does) */
  frameHeader[3] = FrameID[0]; frameHeader[4] = FrameID[1];

  /* words 5 - 8 are reserved for response information */
  frameHeader[5] = frameHeader[6] = frameHeader[7] = frameHeader[8] = 0x00; 
}

//------------------------------------------
// Each class which inherits frames makes its own messages!
void LVDSFrames::MakeMessage() { std::cout << "Hello, world!" << std::endl; } 

//------------------------------------------
bool LVDSFrames::CheckForErrors() 
{
  /*! \fn bool LVDSFrames::CheckForErrors()
   * Check incoming frame header data for errors.
   */
  bool error = false; 

  unsigned char messageLength[2];
  ResponseWords word = ResponseLength0;
  messageLength[0] = message[word];
  word = ResponseLength1;
  messageLength[1] = message[word];
  lvdsLog.debugStream() << "CheckForErrors Message Length = " 
    << ( (messageLength[1]<<8) | messageLength[0] );

  const unsigned int nflags = 8;
  ResponseWords words[nflags] = { FrameStart, DeviceStatus, DeviceStatus, FrameStatus, 
    FrameStatus, FrameStatus, FrameStatus, FrameStatus }; 
  ResponseFlags flags[nflags] = { Direction, DeviceOK, FunctionOK, CRCOK, 
    EndHeader, MaxLen, SecondStart, NAHeader }; 

  for (unsigned int i = 0; i < nflags; ++i) {
    lvdsLog.debugStream() << "Checking word : " << words[i] << "; and flag : " << flags[i];
    if (!message[ words[i] ] & flags[i]) {
      error = true;
      lvdsLog.errorStream() << "HeaderError : " << words[i] 
        << " for FEB " << this->GetFEBNumber();
    }
  }

  return error; 
}

//------------------------------------------
void LVDSFrames::DecodeHeader() 
{
  /*! \fn 
   * extract device information from the FPGA header sent back from
   * the electronics by a read request.
   */
  lvdsLog.debugStream() << " Entering LVDSFrames::DecodeHeader...";
  ResponseWords word;

  word = FrameStart; 
  febNumber[0]        = (message[word]&0x0F); 
  broadcastCommand[0] = (message[word]&0xF0); 
  messageDirection[0] = (message[word]&0x80); 
  word = DeviceStatus;
  deviceFunction[0]   = (message[word]&0x0F); 
  targetDevice[0]     = (message[word]&0xF0); 
  lvdsLog.debugStream() << "  message at framestart: " << (int)message[word];
  lvdsLog.debugStream() << "  direction: " << (int)(message[word]&0x80);
}

//------------------------------------------
void LVDSFrames::printMessageBufferToLog( int buffersize )
{
  lvdsLog.debugStream() << "Printing message buffer of size = " << buffersize;
  if (buffersize > 0) 
    for (int i=0; i<buffersize; i+=2 ) {
      int j = i + 1;
      lvdsLog.debugStream() 
        << std::setfill('0') << std::setw( 2 ) << std::hex << (int)message[i] << " " 
        << std::setfill('0') << std::setw( 2 ) << std::hex << (int)message[j] << " " 
        << "\t" 
        << std::setfill('0') << std::setw( 4 ) << std::dec << i << " " 
        << std::setfill('0') << std::setw( 4 ) << std::dec << j;

    }
}
#endif
