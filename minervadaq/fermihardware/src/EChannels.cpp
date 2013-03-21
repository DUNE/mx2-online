#ifndef EChannels_cpp
#define EChannels_cpp
/*! \file EChannels.cpp
*/

#include <iomanip>

#include "RegisterWords.h"
#include "EChannels.h"
#include "exit_codes.h"

log4cpp::Category& EChannelLog = log4cpp::Category::getInstance(std::string("EChannel"));

//----------------------------------------
/*!
  \param vmeAddress   The channel base address (already bit-shifted)
  \param number       The channel number (0-3)
  \param controller   Pointer to the VME 2718 Controller servicing this device.
  */
EChannels::EChannels( unsigned int vmeAddress, unsigned int number, 
    const Controller* controller ) : 
  VMECommunicator( vmeAddress, controller ),
  channelNumber(number)
{
  EChannelLog.setPriority(log4cpp::Priority::INFO);  

  this->commType = VMEModuleTypes::EChannels;
  channelDirectAddress             = this->address + VMEModuleTypes::EChannelOffset * (unsigned int)(channelNumber);
  receiveMemoryAddress             = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCReceiveMemory;
  sendMemoryAddress                = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCSendMemory;
  framePointersMemoryAddress       = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCFramePointersMemory;
  configurationAddress             = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCConfiguration;
  commandAddress                   = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCCommand;
  eventCounterAddress              = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCEventCounter;
  framesCounterAndLoopDelayAddress = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCFramesCounterAndLoopDelay;
  frameStatusAddress               = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCFrameStatus;
  txRxStatusAddress                = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCTxRxStatus;
  receiveMemoryPointerAddress      = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCReceiveMemoryPointer;
}

//----------------------------------------
EChannels::~EChannels() 
{
  for (std::vector<FrontEndBoard*>::iterator p=FrontEndBoardsVector.begin(); 
      p!=FrontEndBoardsVector.end(); 
      ++p) 
    delete (*p);
  FrontEndBoardsVector.clear();
}

//-----------------------------
//! Return the base address plus the channel offset. Identical to GetDirectAddress, but here for convenience.
unsigned int EChannels::GetAddress() const
{
  return this->channelDirectAddress;
}

//----------------------------------------
//! Return the base address plus the channel offset.
unsigned int EChannels::GetDirectAddress() const
{
  return this->channelDirectAddress;
}

//----------------------------------------
unsigned int EChannels::GetChannelNumber() const
{
  return channelNumber;
}

//----------------------------------------
//! Return the base address.
unsigned int EChannels::GetParentECROCAddress() const
{
  return this->address;
}

//----------------------------------------
unsigned int EChannels::GetParentCROCNumber() const
{
  return ( this->address >> VMEModuleTypes::ECROCAddressShift);
}

//----------------------------------------
int EChannels::DecodeStatusMessage( const unsigned short& status ) const
{
  int frameErrors = 0;
#ifndef GOFAST
  std::string statusBitsDecoded = "|";
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::ReceiveMemoryFrameDiscType) {
    statusBitsDecoded += "ReceiveMemoryFrameDiscType|";
  }
#endif
  if (status & VMEModuleTypes::ReceiveMemoryFrameHeaderError) {
#ifndef GOFAST
    statusBitsDecoded += "ReceiveMemoryFrameHeaderError|";
#endif
    frameErrors++;
  }
  if (status & VMEModuleTypes::ReceiveMemoryCRCError) {
#ifndef GOFAST
    statusBitsDecoded += "ReceiveMemoryCRCError|";
#endif
    frameErrors++;
  }
  if (status & VMEModuleTypes::ReceiveMemoryFrameTimeout) {
#ifndef GOFAST
    statusBitsDecoded += "ReceiveMemoryFrameTimeout|";
#endif
    frameErrors++;
  }
#ifndef GOFAST
  if (status & VMEModuleTypes::ReceiveMemoryFrameReceived) {
    statusBitsDecoded += "ReceiveMemoryFrameReceived|";
  }
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::ReceiveMemoryFrameCountFull) {
    statusBitsDecoded += "ReceiveMemoryFrameCountFull|";
  }
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::ReceiveMemoryEmpty) {
    statusBitsDecoded += "ReceiveMemoryEmpty|";
  }
#endif
  if (status & VMEModuleTypes::ReceiveMemoryFull) {
#ifndef GOFAST
    statusBitsDecoded += "ReceiveMemoryFull|";
#endif
    frameErrors++;
  }
#ifndef GOFAST
  if (status & VMEModuleTypes::SendMemoryUnusedBit0) {
    statusBitsDecoded += "SendMemoryUnusedBit0|";
  }
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::SendMemoryUnusedBit1) {
    statusBitsDecoded += "SendMemoryUnusedBit1|";
  }
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::SendMemoryRDFEDone) {
    statusBitsDecoded += "SendMemoryRDFEDone|";
  }
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::SendMemoryRDFEUpdating) {
    statusBitsDecoded += "SendMemoryRDFEUpdating|";
  }
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::SendMemoryFrameSent) {
    statusBitsDecoded += "SendMemoryFrameSent|";
  }
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::SendMemoryFrameSending) {
    statusBitsDecoded += "SendMemoryFrameSending|";
  }
#endif
#ifndef GOFAST
  if (status & VMEModuleTypes::SendMemoryEmpty) {
    statusBitsDecoded += "SendMemoryEmpty|";
  }
#endif
  if (status & VMEModuleTypes::SendMemoryFull) {
#ifndef GOFAST
    statusBitsDecoded += "SendMemoryFull|";
#endif
    frameErrors++;
  }
#ifndef GOFAST
  EChannelLog.debugStream() << "FrameStatus 0x" << std::hex << status << 
    " for ECROC " << std::dec << this->GetParentCROCNumber() << "; Channel " << 
    this->channelNumber << "; " << statusBitsDecoded;
#endif
  return frameErrors;
}

//----------------------------------------
//! We do not do FEB configuration here. We only check to see if the FEB exists.
void EChannels::SetupNFrontEndBoards( int nFEBs )
{
  EChannelLog.infoStream() << "SetupNFrontEndBoards for " << nFEBs << " FEBs...";
  if ( ( nFEBs < 0 ) || (nFEBs > 10) ) {
    EChannelLog.fatalStream() << "Cannot have less than 0 or more than 10 FEBs on a Channel!";
    exit(EXIT_CONFIG_ERROR);
  }
  for ( int i=1; i<=nFEBs; ++i ) {
    EChannelLog.infoStream() << "Setting up FEB " << i << " ...";
    FrontEndBoard *feb = 
      new FrontEndBoard( (FrameTypes::FEBAddresses)i, this->GetAddress(), this->GetCrateNumber() );
    if ( isAvailable( feb ) ) {
      FrontEndBoardsVector.push_back( feb );
    } else {
      EChannelLog.fatalStream() << "Requested FrontEndBoard with address " << i << " is not avialable!";
      exit(EXIT_CONFIG_ERROR);
    }
  }
  this->UpdateConfigurationForVal( (unsigned short)(0xF & nFEBs), (unsigned short)0xFFF0 );
}

//----------------------------------------
//! Only update the enable bit.
void EChannels::EnableSequencerReadout() const
{
  this->UpdateConfigurationForVal( (unsigned short)(0x8000), (unsigned short)(0x7FFF) );
}

//----------------------------------------
//! Only update the enable bit.
void EChannels::DisableSequencerReadout() const
{
  this->UpdateConfigurationForVal( (unsigned short)(0x0000), (unsigned short)(0x7FFF) );
}

//----------------------------------------
unsigned short EChannels::GetChannelConfiguration() const
{
  unsigned short configuration = 0;
  unsigned char receivedMessage[] = {0x0,0x0};

#ifndef GOFAST
  EChannelLog.debugStream() << "Read ReceiveMemoryPointer Address = 0x" << std::hex << configurationAddress;
#endif
  int error = ReadCycle( receivedMessage, configurationAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure reading the Channel Configuration!"); 
  configuration = receivedMessage[1]<<0x08 | receivedMessage[0];
#ifndef GOFAST
  EChannelLog.debugStream() << "Channel " << channelNumber << " Configuration = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << configuration;
#endif

  return configuration;
}

//----------------------------------------
//! Only update the enable bit.
void EChannels::UpdateConfigurationForVal( unsigned short val, unsigned short mask ) const
{
  // maintain state - we only want to update the val
  unsigned short configuration = this->GetChannelConfiguration();  
  configuration &= mask; 
  configuration |= val; 
  unsigned char config[] = {0x0,0x0};
  config[0] = configuration & 0xFF;
  config[1] = (configuration & 0xFF00)>>8;
  this->SetChannelConfiguration( config );
  unsigned short configurationCheck = this->GetChannelConfiguration();
  if( configuration != configurationCheck ) exit(EXIT_CONFIG_ERROR);
}

//----------------------------------------
void EChannels::SetChannelConfiguration( unsigned char* message ) const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "Channel " << channelNumber << " Target Configuration: 0x" 
    << std::setfill('0') << std::setw( 2 ) << std::hex << (int)message[1] << (int)message[0];
#endif
  int error = WriteCycle( 2, message, configurationAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure writing to Channel Configuration Register!"); 
}

//----------------------------------------
std::vector<FrontEndBoard*>* EChannels::GetFrontEndBoardVector() 
{
  return &FrontEndBoardsVector;
}

//----------------------------------------
//! Index should equal address - 1 (addr's go 1.., index goes 0..)
FrontEndBoard* EChannels::GetFrontEndBoardVector( int index ) 
{
  // We live fast and dangerous. If we're out of bounds, we crash.
  return FrontEndBoardsVector[index];
}

//----------------------------------------
unsigned int EChannels::GetNumFrontEndBoards() const
{
  return FrontEndBoardsVector.size();
}

//----------------------------------------
bool EChannels::isAvailable( FrontEndBoard* feb ) const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "isAvailable FrontEndBoard with class address = " << feb->GetBoardNumber();
#endif
  bool available = false;

  std::tr1::shared_ptr<FPGAFrame> frame = feb->GetFPGAFrame();
  unsigned short dataLength = this->ReadFPGAProgrammingRegistersToMemory( frame );
  unsigned char* dataBuffer = this->ReadMemory( dataLength ); 

  frame->SetReceivedMessage(dataBuffer);
  frame->DecodeRegisterValues();
#ifndef GOFAST
  EChannelLog.debugStream() << "Decoded FrontEndBoard address = " << (int)feb->GetBoardNumber();
#endif
  if( (int)feb->GetBoardNumber() == frame->GetFEBNumber() ) available = true;

#ifndef GOFAST
  EChannelLog.debugStream() << "FrontEndBoard " << feb->GetBoardNumber() << " isAvailable = " << available;
#endif
  return available;
}

//----------------------------------------
void EChannels::ClearAndResetStatusRegister() const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "Clear And Reset Command Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << commandAddress;
#endif
  int error = WriteCycle( 2,  RegisterWords::channelReset,  commandAddress, addressModifier, dataWidthReg ); 
  if( error ) exitIfError( error, "Failure clearing the status!");
}

//----------------------------------------
unsigned short EChannels::ReadFrameStatusRegister() const
{
  unsigned char receivedMessage[] = {0x0,0x0};
#ifndef GOFAST
  EChannelLog.debugStream() << "Frame Status Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << frameStatusAddress;
#endif

  int error = ReadCycle(receivedMessage, frameStatusAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure reading Frame Status!");

  unsigned short status = (receivedMessage[1] << 8) | receivedMessage[0];
#ifndef GOFAST
  EChannelLog.debugStream() << " Status = 0x" << std::hex << status;
#endif

  return status;
}

//----------------------------------------
unsigned short EChannels::ReadTxRxStatusRegister() const
{
  unsigned char receivedMessage[] = {0x0,0x0};
#ifndef GOFAST
  EChannelLog.debugStream() << "Tx/Rx Status Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << txRxStatusAddress;
#endif

  int error = ReadCycle(receivedMessage, txRxStatusAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure reading Tx/Rx Status!");

  unsigned short status = (receivedMessage[1] << 8) | receivedMessage[0];
#ifndef GOFAST
  EChannelLog.debugStream() << " Status = 0x" << std::hex << status;
#endif

  return status;
}


//----------------------------------------
void EChannels::SendMessage() const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "SendMessage Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex << commandAddress 
    << "; Message = 0x" << std::hex << (int)RegisterWords::sendMessage[1] << (int)RegisterWords::sendMessage[0];
#endif
  int error = WriteCycle( 2, RegisterWords::sendMessage, commandAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure writing to CROC Send Message Register!"); 
}

//----------------------------------------
unsigned short EChannels::WaitForMessageReceived() const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "WaitForMessageReceived...";
#endif
  unsigned short status = 0;
  do {
    status = this->ReadFrameStatusRegister();
  } while ( 
      !(status & VMEModuleTypes::SendMemoryFull)                
      && !(status & VMEModuleTypes::ReceiveMemoryFull)             
      && !(status & VMEModuleTypes::ReceiveMemoryFrameReceived)    
      && !(status & VMEModuleTypes::ReceiveMemoryFrameTimeout)     
      && !(status & VMEModuleTypes::ReceiveMemoryCRCError)         
      && !(status & VMEModuleTypes::ReceiveMemoryFrameHeaderError)
      );
  int error = DecodeStatusMessage(status);
  if (0 != error) return 0; // TODO: throw...
#ifndef GOFAST
  EChannelLog.debugStream() << " Decoded Status Error Level = " << error;
  EChannelLog.debugStream() << "Message was received with status = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << status;
#endif
  return status;
}

//----------------------------------------
unsigned short EChannels::WaitForSequencerReadoutCompletion() const
{
  unsigned short status = 0;
  do {
    status = this->ReadFrameStatusRegister();
  } while ( 0 == (status & VMEModuleTypes::SendMemoryRDFEDone) );  
  return status;
}

//----------------------------------------
unsigned short EChannels::ReadDPMPointer() const
{
  unsigned short receiveMemoryPointer = 0;
  unsigned char pointer[] = {0x0,0x0};

#ifndef GOFAST
  EChannelLog.debugStream() << "Read ReceiveMemoryPointer Address = 0x" 
    << std::hex << receiveMemoryPointerAddress;
#endif
  int error = ReadCycle( pointer, receiveMemoryPointerAddress, addressModifier, dataWidthReg ); 
  if( error ) exitIfError( error, "Failure reading the Receive Memory Pointer!"); 
  receiveMemoryPointer = pointer[1]<<0x08 | pointer[0];
#ifndef GOFAST
  EChannelLog.debugStream() << "Pointer Length = " << receiveMemoryPointer;
#endif

  return receiveMemoryPointer;
}

//----------------------------------------
unsigned short EChannels::ReadEventCounter() const
{
  unsigned short eventCounter = 0;
  unsigned char counter[] = {0x0,0x0};

#ifndef GOFAST
  EChannelLog.debugStream() << "Read EventCounter Address = 0x" << std::hex << eventCounterAddress;
#endif
  int error = ReadCycle( counter, eventCounterAddress, addressModifier, dataWidthReg ); 
  if( error ) exitIfError( error, "Failure reading the Event Counter!"); 
  eventCounter = counter[1]<<0x08 | counter[0];
#ifndef GOFAST
  EChannelLog.debugStream() << "Event Counter = " << eventCounter;
#endif

  return eventCounter;
}

//----------------------------------------
unsigned char* EChannels::ReadMemory( unsigned short dataLength ) const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "ReadMemory for buffer size = " << dataLength;
#endif
  unsigned char *dataBuffer = new unsigned char [dataLength];
  int error = ReadBLT( dataBuffer, dataLength, receiveMemoryAddress, bltAddressModifier, dataWidthSwapped );
  if( error ) exitIfError( error, "Error in BLT ReadCycle!");

  return dataBuffer;
}

//----------------------------------------
void EChannels::WriteMessageToMemory( unsigned char* message, int messageLength ) const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "Send Memory Address   = 0x" << std::hex << sendMemoryAddress;
  EChannelLog.debugStream() << "Message Length        = " << messageLength;
#endif
  int error = WriteCycle( messageLength, message, sendMemoryAddress, addressModifier, dataWidthSwappedReg );
  if( error ) exitIfError( error, "Failure writing to CROC FIFO!"); 
}

//----------------------------------------
void EChannels::WriteFrameRegistersToMemory( std::tr1::shared_ptr<LVDSFrame> frame ) const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "WriteFrameRegistersToMemory";
#endif
  frame->MakeMessage();
  this->WriteMessageToMemory( frame->GetOutgoingMessage(), frame->GetOutgoingMessageLength() );
}

//----------------------------------------
void EChannels::WriteFPGAProgrammingRegistersDumpReadToMemory( std::tr1::shared_ptr<FPGAFrame> frame ) const
{
  frame->MakeShortMessage();  
  this->WriteMessageToMemory( frame->GetOutgoingMessage(), frame->GetOutgoingMessageLength() );
}

//----------------------------------------
void EChannels::WriteTRIPRegistersReadFrameToMemory( std::tr1::shared_ptr<TRIPFrame> frame ) const
{
  frame->SetRead(true);
  this->WriteFrameRegistersToMemory( frame );
}

//----------------------------------------
unsigned short EChannels::ReadFPGAProgrammingRegistersToMemory( std::tr1::shared_ptr<FPGAFrame> frame ) const
{
  this->ClearAndResetStatusRegister();
  this->WriteFPGAProgrammingRegistersDumpReadToMemory( frame );
  this->SendMessage();
  this->WaitForMessageReceived();
  unsigned short dataLength = this->ReadDPMPointer();

  return dataLength;
}

//----------------------------------------
void EChannels::exitIfError( int error, const std::string& msg ) const
{
  if (error) {
    EChannelLog.fatalStream() << "Fatal error for Channel with address = 0x" 
      << std::hex << this->channelDirectAddress;
    EChannelLog.fatalStream() << " CROC Number = " << this->GetParentCROCNumber() 
      << "; Channel Number = " << channelNumber;
    EChannelLog.fatalStream() << msg;
    this->GetController()->ReportError(error);
    exit(error);
  }
}

#endif
