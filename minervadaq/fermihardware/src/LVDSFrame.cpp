#ifndef LVDSFrame_cpp
#define LVDSFrame_cpp
/*! \file LVDSFrame.cpp
*/

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
  lvdsLog.setPriority(log4cpp::Priority::INFO);
}

//-------------------------------------------------------
LVDSFrame::~LVDSFrame() 
{ 
  lvdsLog.debugStream() << "LVDSFrame::~LVDSFrame()... LVDSFrame Destructor";
  if (receivedMessage) {
    delete [] receivedMessage;
  } 
  if (outgoingMessage) { 
    delete [] outgoingMessage;
  } 
}    

//------------------------------------------
//! Configure the ivars for building an outgoing header and build one.
/*!
  \param dev       The device to which the message is destined
  \param b         whether or not this is a broadcast request
  \param d         the direction of the message:  either master-to-slave (true for transmit) or
  slave-to-master (receive)
  \param deviceFun the device function.  This is specific to the device (dev) receiving the message
  \param febNum    the number of the FEB to which this frame is destined
  */
void LVDSFrame::MakeDeviceFrameTransmit( FrameTypes::Devices dev, 
    FrameTypes::Broadcasts b, FrameTypes::Directions d, 
    unsigned int deviceFun, unsigned int febNum ) 
{

  broadcastCommand[0] = (unsigned char)b;
  messageDirection[0] = (unsigned char)d;
  targetDevice[0]     = (unsigned char)dev; 
  deviceFunction[0]   = (unsigned char)deviceFun;
  febNumber[0]        = (unsigned char)febNum;

  MakeOutgoingHeader();
}

//------------------------------------------
//! Make the beginning of the outgoing header.
/*! 
  The base portion of the outgoing header is common to all frame types.
  */
void LVDSFrame::MakeOutgoingHeader() 
{
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
//! Check incoming frame header data for errors.
bool LVDSFrame::CheckForErrors() 
{
  using namespace FrameTypes;

  bool error = false; 

  // There isn't really a good check we can make on message length here.

  unsigned short status = this->ReceivedMessageStatus();
  lvdsLog.debugStream() << "CheckForErrors Frame Status = 0x" << std::hex << status;

  const unsigned int nflags = 8;
  ResponseBytes bytes[nflags] = { FrameStart, DeviceStatus, DeviceStatus, FrameStatus, 
    FrameStatus, FrameStatus, FrameStatus, FrameStatus }; 
  ResponseFlags flags[nflags] = { Direction, DeviceOK, FunctionOK, CRCOK, 
    EndHeader, MaxLen, SecondStart, NAHeader }; 

  for (unsigned int i = 0; i < nflags; ++i) {
    if (!receivedMessage[ bytes[i] ] & flags[i]) {
      error = true;
      lvdsLog.errorStream() << "HeaderError for byte: " << bytes[i] 
        << "; and flag : " << flags[i]
        << "; for FEB " << this->GetFEBNumber();
    }
  }

  lvdsLog.debugStream() << "Error Status = " << error;
  return error; 
}


//------------------------------------------
unsigned short LVDSFrame::ReceivedMessageLength() const
{
  using namespace FrameTypes;

  lvdsLog.debugStream() << "LVDSFrame::ReceivedMessageLength()";
  if (NULL == receivedMessage) {
    lvdsLog.errorStream() << "receivedMessage is NULL!";
    return 0;
  }

  lvdsLog.debugStream() << "Message Length = " << ( (receivedMessage[ResponseLength0]<<8) | receivedMessage[ResponseLength1] );
  return ( (receivedMessage[ResponseLength0]<<8) | receivedMessage[ResponseLength1] ); 
}

//------------------------------------------
unsigned short LVDSFrame::ReceivedMessageStatus() const
{
  if (NULL == receivedMessage) return 0;
  return ( (receivedMessage[FrameTypes::FrameStatus0]<<8) | 
      receivedMessage[FrameTypes::FrameStatus1] ); 
}


//------------------------------------------
//! Extract device information from the frame header sent back from the electronics.
void LVDSFrame::DecodeHeader() 
{
  using namespace FrameTypes;

  lvdsLog.debugStream() << " Entering LVDSFrame::DecodeHeader...";
  ResponseBytes byte; 

  byte = FrameStart; 
  febNumber[0]        = (receivedMessage[byte]&0x0F); 
  broadcastCommand[0] = (receivedMessage[byte]&0xF0); 
  messageDirection[0] = (receivedMessage[byte]&0x80); 
  byte = DeviceStatus;
  deviceFunction[0]   = (receivedMessage[byte]&0x0F); 
  targetDevice[0]     = (receivedMessage[byte]&0xF0); 
  lvdsLog.debugStream() << "  FEB Number            : " << (int)febNumber[0];
  lvdsLog.debugStream() << "  Device Function       : " << (int)deviceFunction[0];
  lvdsLog.debugStream() << "  message at framestart : " << (int)receivedMessage[byte];
  lvdsLog.debugStream() << "  direction             : " << (int)(receivedMessage[byte]&0x80);
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

//-----------------------------
std::ostream& operator<<(std::ostream& out, const LVDSFrame& s)
{
  using namespace FrameTypes;

  std::string device = "Uknown Device";
  switch (s.GetDeviceType()) {
    case (NoDevices) :
      device = "No Device";
      break;
    case (TRiP) :
      device = "TRiP";
      break;
    case (FPGA) :
      device = "FPGA";
      break;
    case (RAM) :
      device = "RAM";
      break;
    case (Flash) :
      device = "Flash";
      break;
    default :
      device = "Decoding Error?";
      break;
  }
  out << "FEB = " << s.GetFEBNumber() << "; Device = " << device 
    << "; Frame Length = " << s.ReceivedMessageLength()
    << "; Channel Status = 0x" << std::hex << s.ReceivedMessageStatus();
  return out;
}

#endif
