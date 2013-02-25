#ifndef LVDSFrame_cpp
#define LVDSFrame_cpp

#include <iomanip>
#include "LVDSFrame.h"
#include "exit_codes.h"

/*********************************************************************************
 * Class for creating FPGA Frame header objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

/* const int LVDSFrame::MinHeaderLength=9; // renamed: FrameHeaderLengthOutgoing */

log4cpp::Category& lvdsLog = log4cpp::Category::getInstance(std::string("frames"));

//------------------------------------------
LVDSFrame::LVDSFrame() 
{ 
  FrameID[0] = 0x00; 
  FrameID[1] = 0x00; 
  outgoingMessage = NULL;
  receivedMessage = NULL;
  febNumber[0]        = 0;
  targetDevice[0]     = 0;
  deviceFunction[0]   = 0;
  broadcastCommand[0] = 0;
  messageDirection[0] = 0;
  lvdsLog.setPriority(log4cpp::Priority::DEBUG);
}

//-------------------------------------------------------
LVDSFrame::~LVDSFrame() 
{ 
  if (receivedMessage) delete [] receivedMessage; 
  if (outgoingMessage) delete [] outgoingMessage; 
}    

//------------------------------------------
void LVDSFrame::MakeDeviceFrameTransmit( Devices dev, Broadcasts b, Directions d, 
    unsigned int deviceFun, unsigned int febNum ) 
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
  deviceFunction[0]   = (unsigned char)deviceFun;
  febNumber[0]        = (unsigned char)febNum;

  MakeOutgoingHeader();
}

//------------------------------------------
void LVDSFrame::MakeOutgoingHeader() 
{
  /*! \fn********************************************************************************
   * a function which packs outgoing frame header data for transmitting information from
   * the data acquisition routines to the FPGA on the front end board (FEB) and
   * on to the requested device.
   *********************************************************************************/

  /* we've done all the conversion & stuff so we can make up the frame header now! */
  /* word 1: the broadcast direction, command, and feb number */
  frameHeader[0]  = (messageDirection[0] & 0x80 ); // The direction bit is in bit 7 of word 1
  frameHeader[0] |= (broadcastCommand[0] & 0xF0);  // The broadcast command is in bits 4-6
  frameHeader[0] |= (febNumber[0] & 0x0F);         // The feb number is bits 0-3

  /* word 2:  target device & its function */
  frameHeader[1]  = (targetDevice[0] & 0xF0);    // The target device is in bits 4-7
  frameHeader[1] |= (deviceFunction[0] & 0x0F);  // The function is in bits 0-3

  /* word 3:  reserved for response information */
  frameHeader[2] = 0x00; //initialize to null

  /* word 4 & 5:  frame ID (whatever that does) */
  frameHeader[3] = FrameID[0]; 
  frameHeader[4] = FrameID[1];

  /* words 5 - 8 are reserved for response information */
  frameHeader[5] = frameHeader[6] = frameHeader[7] = frameHeader[8] = 0x00; 
}

//------------------------------------------
void LVDSFrame::MakeMessage() 
{ 
  lvdsLog.debugStream() << "Please override LVDSFrame::MakeMessage()!"; 
}

//------------------------------------------
unsigned int LVDSFrame::GetOutgoingMessageLength() 
{ 
  return 0; 
}

//------------------------------------------
void LVDSFrame::DecodeRegisterValues() 
{ 
  lvdsLog.debugStream() << "Please override LVDSFrame::DecodeRegisterValues()!"; 
}

//------------------------------------------
bool LVDSFrame::CheckForErrors() 
{
  /*! \fn bool LVDSFrame::CheckForErrors()
   * Check incoming frame header data for errors.
   */
  bool error = false; 

  // There isn't really a good check we can make on message length here.
  
  unsigned short status = this->ReceivedMessageStatus();
  lvdsLog.debugStream() << "CheckForErrors Frame Status = 0x" << std::hex << status;
  if (0x1010 != status) {
    lvdsLog.fatalStream() << "CheckForErrors Frame Status = 0x" << std::hex << status;
    return true;
  }

  const unsigned int nflags = 8;
  ResponseWords words[nflags] = { FrameStart, DeviceStatus, DeviceStatus, FrameStatus, 
    FrameStatus, FrameStatus, FrameStatus, FrameStatus }; 
  ResponseFlags flags[nflags] = { Direction, DeviceOK, FunctionOK, CRCOK, 
    EndHeader, MaxLen, SecondStart, NAHeader }; 

  for (unsigned int i = 0; i < nflags; ++i) {
    lvdsLog.debugStream() << "Checking word : " << words[i] << "; and flag : " << flags[i];
    if (!receivedMessage[ words[i] ] & flags[i]) {
      error = true;
      lvdsLog.errorStream() << "HeaderError : " << words[i] 
        << " for FEB " << this->GetFEBNumber();
    }
  }

  lvdsLog.debugStream() << "Error Status = " << error;
  return error; 
}


//------------------------------------------
unsigned short LVDSFrame::ReceivedMessageLength()
{
  lvdsLog.debugStream() << "LVDSFrame::ReceivedMessageLength()";
  if (NULL == receivedMessage) {
    lvdsLog.errorStream() << "receivedMessage is NULL!";
    return 0;
  }
  lvdsLog.debugStream() << "Message Length = " << ( (receivedMessage[ResponseLength0]<<8) | receivedMessage[ResponseLength1] );
  return ( (receivedMessage[ResponseLength0]<<8) | receivedMessage[ResponseLength1] ); 
}

//------------------------------------------
unsigned short LVDSFrame::ReceivedMessageStatus()
{
  if (NULL == receivedMessage) return 0;
  return ( (receivedMessage[FrameStatus0]<<8) | receivedMessage[FrameStatus1] ); 
}


//------------------------------------------
void LVDSFrame::DecodeHeader() 
{
  /*! \fn 
   * extract device information from the FPGA header sent back from
   * the electronics by a read request.
   */
  lvdsLog.debugStream() << " Entering LVDSFrame::DecodeHeader...";
  ResponseWords word;

  word = FrameStart; 
  febNumber[0]        = (receivedMessage[word]&0x0F); 
  broadcastCommand[0] = (receivedMessage[word]&0xF0); 
  messageDirection[0] = (receivedMessage[word]&0x80); 
  word = DeviceStatus;
  deviceFunction[0]   = (receivedMessage[word]&0x0F); 
  targetDevice[0]     = (receivedMessage[word]&0xF0); 
  lvdsLog.debugStream() << "  message at framestart: " << (int)receivedMessage[word];
  lvdsLog.debugStream() << "  direction: " << (int)(receivedMessage[word]&0x80);
}

//------------------------------------------
void LVDSFrame::printReceivedMessageToLog()
{
  unsigned short buffersize = this->ReceivedMessageLength();
  lvdsLog.debugStream() << "Printing message buffer of size = " << buffersize;
  for (unsigned short i = 0; i < buffersize; i+=2 ) {
    int j = i + 1;
    lvdsLog.debugStream() 
      << std::setfill('0') << std::setw( 2 ) << std::hex << (int)receivedMessage[i] << " " 
      << std::setfill('0') << std::setw( 2 ) << std::hex << (int)receivedMessage[j] << " " 
      << "\t" 
      << std::setfill('0') << std::setw( 4 ) << std::dec << i << " " 
      << std::setfill('0') << std::setw( 4 ) << std::dec << j;

  }
}
#endif
