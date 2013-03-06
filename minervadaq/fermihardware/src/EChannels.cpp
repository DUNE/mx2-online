#ifndef EChannels_cpp
#define EChannels_cpp

#include <iomanip>

#include "RegisterWords.h"
#include "EChannels.h"
#include "exit_codes.h"

/*********************************************************************************
 * Class for creating CROC-E channel objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

log4cpp::Category& EChannelLog = log4cpp::Category::getInstance(std::string("EChannel"));

//----------------------------------------
EChannels::EChannels( unsigned int vmeAddress, unsigned int number, 
    const Controller* controller ) : 
  VMECommunicator( vmeAddress, controller ),
  channelNumber(number)
{
  /*! \fn 
   * constructor takes the following arguments:
   * \param vmeAddress  :  The channel base address (already bit-shifted)
   * \param number      :  The channel number (0-3)
   * \param *controller :  Pointer to the VME 2718 Controller servicing this device.
   */
  EChannelLog.setPriority(log4cpp::Priority::DEBUG);  

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
  for (std::vector<FrontEndBoard*>::iterator p=FrontEndBoardsVector.begin(); p!=FrontEndBoardsVector.end(); p++) delete (*p);
  FrontEndBoardsVector.clear();
}

//-----------------------------
unsigned int EChannels::GetAddress() const
{
  return this->channelDirectAddress;
}

//----------------------------------------
unsigned int EChannels::GetChannelNumber() const
{
  return channelNumber;
}

//----------------------------------------
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
unsigned int EChannels::GetDirectAddress() const
{
  return this->channelDirectAddress;
}

//----------------------------------------
int EChannels::DecodeStatusMessage( const unsigned short& status ) const
{
  int frameErrors = 0;
  std::string statusBitsDecoded = "|";
  if (status & VMEModuleTypes::ReceiveMemoryFrameDiscType) {
    statusBitsDecoded += "ReceiveMemoryFrameDiscType|";
  }
  if (status & VMEModuleTypes::ReceiveMemoryFrameHeaderError) {
    statusBitsDecoded += "ReceiveMemoryFrameHeaderError|";
    frameErrors++;
  }
  if (status & VMEModuleTypes::ReceiveMemoryCRCError) {
    statusBitsDecoded += "ReceiveMemoryCRCError|";
    frameErrors++;
  }
  if (status & VMEModuleTypes::ReceiveMemoryFrameTimeout) {
    statusBitsDecoded += "ReceiveMemoryFrameTimeout|";
    frameErrors++;
  }
  if (status & VMEModuleTypes::ReceiveMemoryFrameReceived) {
    statusBitsDecoded += "ReceiveMemoryFrameReceived|";
  }
  if (status & VMEModuleTypes::ReceiveMemoryFrameCountFull) {
    statusBitsDecoded += "ReceiveMemoryFrameCountFull|";
  }
  if (status & VMEModuleTypes::ReceiveMemoryEmpty) {
    statusBitsDecoded += "ReceiveMemoryEmpty|";
  }
  if (status & VMEModuleTypes::ReceiveMemoryFull) {
    statusBitsDecoded += "ReceiveMemoryFull|";
    frameErrors++;
  }
  if (status & VMEModuleTypes::SendMemoryUnusedBit0) {
    statusBitsDecoded += "SendMemoryUnusedBit0|";
  }
  if (status & VMEModuleTypes::SendMemoryUnusedBit1) {
    statusBitsDecoded += "SendMemoryUnusedBit1|";
  }
  if (status & VMEModuleTypes::SendMemoryRDFEDone) {
    statusBitsDecoded += "SendMemoryRDFEDone|";
  }
  if (status & VMEModuleTypes::SendMemoryRDFEUpdating) {
    statusBitsDecoded += "SendMemoryRDFEUpdating|";
  }
  if (status & VMEModuleTypes::SendMemoryFrameSent) {
    statusBitsDecoded += "SendMemoryFrameSent|";
  }
  if (status & VMEModuleTypes::SendMemoryFrameSending) {
    statusBitsDecoded += "SendMemoryFrameSending|";
  }
  if (status & VMEModuleTypes::SendMemoryEmpty) {
    statusBitsDecoded += "SendMemoryEmpty|";
  }
  if (status & VMEModuleTypes::SendMemoryFull) {
    statusBitsDecoded += "SendMemoryFull|";
    frameErrors++;
  }
  EChannelLog.debugStream() << "FrameStatus 0x" << std::hex << status << 
    " for ECROC " << std::dec << this->GetParentCROCNumber() << "; Channel " << 
    this->channelNumber << "; " << statusBitsDecoded;
  return frameErrors;
}

//----------------------------------------
void EChannels::SetupNFrontEndBoards( int nFEBs )
{
  EChannelLog.debugStream() << "SetupNFrontEndBoards for " << nFEBs << " FEBs...";
  if ( ( nFEBs < 0 ) || (nFEBs > 10) ) {
    EChannelLog.fatalStream() << "Cannot have less than 0 or more than 10 FEBs on a Channel!";
    exit(EXIT_CONFIG_ERROR);
  }
  for ( int i=1; i<=nFEBs; ++i ) {
    EChannelLog.infoStream() << "Setting up FEB " << i << " ...";
    FrontEndBoard *feb = new FrontEndBoard( (FrameTypes::febAddresses)i );
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
void EChannels::EnableSequencerReadout() const
{
  this->UpdateConfigurationForVal( (unsigned short)(0x8000), (unsigned short)(0x7FFF) );
}

//----------------------------------------
void EChannels::DisableSequencerReadout() const
{
  this->UpdateConfigurationForVal( (unsigned short)(0x0000), (unsigned short)(0x7FFF) );
}

//----------------------------------------
unsigned short EChannels::GetChannelConfiguration() const
{
  unsigned short configuration = 0;
  unsigned char receivedMessage[] = {0x0,0x0};

  EChannelLog.debugStream() << "Read ReceiveMemoryPointer Address = 0x" << std::hex << configurationAddress;
  int error = ReadCycle( receivedMessage, configurationAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure reading the Channel Configuration!"); 
  configuration = receivedMessage[1]<<0x08 | receivedMessage[0];
  EChannelLog.debugStream() << "Channel " << channelNumber << " Configuration = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << configuration;

  return configuration;
}

//----------------------------------------
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
  // message length should always be two or there could be problems!
  EChannelLog.debugStream() << "Channel " << channelNumber << " Target Configuration: 0x" 
    << std::setfill('0') << std::setw( 2 ) << std::hex << (int)message[1] << (int)message[0];
  int error = WriteCycle( 2, message, configurationAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure writing to Channel Configuration Register!"); 
}

//----------------------------------------
std::vector<FrontEndBoard*>* EChannels::GetFrontEndBoardVector() 
{
  return &FrontEndBoardsVector;
}

//----------------------------------------
FrontEndBoard* EChannels::GetFrontEndBoardVector( int index /* should always equal FrontEndBoard address - 1 (vect:0..., addr:1...) */ ) 
{
  // TODO: add check for null here? or too slow? (i.e., live fast and dangerouss)
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
  EChannelLog.debugStream() << "isAvailable FrontEndBoard with class address = " << feb->GetBoardNumber();
  bool available = false;

  std::tr1::shared_ptr<FPGAFrame> frame = feb->GetFPGAFrame();
  unsigned short dataLength = this->ReadFPGAProgrammingRegistersToMemory( frame );
  EChannelLog.debugStream() << "isAvailable read data length = " << dataLength;
  unsigned char* dataBuffer = this->ReadMemory( dataLength ); 
  EChannelLog.debugStream() << "isAvailable read dataBuffer.";

  frame->SetReceivedMessage(dataBuffer);
  EChannelLog.debugStream() << "isAvailable set frame received message.";
  frame->DecodeRegisterValues();
  EChannelLog.debugStream() << "Decoded FrontEndBoard address = " << (int)feb->GetBoardNumber();
  if( (int)feb->GetBoardNumber() == frame->GetFEBNumber() ) available = true;

  EChannelLog.debugStream() << "FrontEndBoard " << feb->GetBoardNumber() << " isAvailable = " << available;
  return available;
}

//----------------------------------------
void EChannels::ClearAndResetStatusRegister() const
{
  EChannelLog.debugStream() << "Clear And Reset Command Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << commandAddress;
  int error = WriteCycle( 2,  RegisterWords::channelReset,  commandAddress, addressModifier, dataWidthReg ); 
  if( error ) exitIfError( error, "Failure clearing the status!");
}

//----------------------------------------
unsigned short EChannels::ReadFrameStatusRegister() const
{
  unsigned char receivedMessage[] = {0x0,0x0};
  EChannelLog.debugStream() << "Frame Status Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << frameStatusAddress;

  int error = ReadCycle(receivedMessage, frameStatusAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure reading Frame Status!");

  unsigned short status = (receivedMessage[1] << 8) | receivedMessage[0];
  EChannelLog.debugStream() << " Status = 0x" << std::hex << status;

  return status;
}

//----------------------------------------
unsigned short EChannels::ReadTxRxStatusRegister() const
{
  unsigned char receivedMessage[] = {0x0,0x0};
  EChannelLog.debugStream() << "Tx/Rx Status Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << txRxStatusAddress;

  int error = ReadCycle(receivedMessage, txRxStatusAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure reading Tx/Rx Status!");

  unsigned short status = (receivedMessage[1] << 8) | receivedMessage[0];
  EChannelLog.debugStream() << " Status = 0x" << std::hex << status;

  return status;
}


//----------------------------------------
void EChannels::SendMessage() const
{
  //#ifndef GOFAST
  //#endif
  EChannelLog.debugStream() << "SendMessage Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex << commandAddress 
    << "; Message = 0x" << std::hex << (int)RegisterWords::sendMessage[1] << (int)RegisterWords::sendMessage[0];
  int error = WriteCycle( 2, RegisterWords::sendMessage, commandAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure writing to CROC Send Message Register!"); 
}

//----------------------------------------
unsigned short EChannels::WaitForMessageReceived() const
{
  EChannelLog.debugStream() << "WaitForMessageReceived...";
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
  EChannelLog.debugStream() << " Decoded Status Error Level = " << error;
  EChannelLog.debugStream() << "Message was received with status = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << status;
  return status;
}

//----------------------------------------
unsigned short EChannels::WaitForSequencerReadoutCompletion() const
{
  unsigned short status = 0;
  do {
    status = this->ReadFrameStatusRegister();
  } while ( 0 == (status & VMEModuleTypes::SendMemoryRDFEDone /*0x0400*/ ) );  
  return status;
}

//----------------------------------------
unsigned short EChannels::ReadDPMPointer() const
{
  unsigned short receiveMemoryPointer = 0;
  unsigned char pointer[] = {0x0,0x0};

  EChannelLog.debugStream() << "Read ReceiveMemoryPointer Address = 0x" << std::hex << receiveMemoryPointerAddress;
  int error = ReadCycle( pointer, receiveMemoryPointerAddress, addressModifier, dataWidthReg ); 
  if( error ) exitIfError( error, "Failure reading the Receive Memory Pointer!"); 
  receiveMemoryPointer = pointer[1]<<0x08 | pointer[0];
  EChannelLog.debugStream() << "Pointer Length = " << receiveMemoryPointer;

  return receiveMemoryPointer;
}

//----------------------------------------
unsigned short EChannels::ReadEventCounter() const
{
  unsigned short eventCounter = 0;
  unsigned char counter[] = {0x0,0x0};

  EChannelLog.debugStream() << "Read EventCounter Address = 0x" << std::hex << eventCounterAddress;
  int error = ReadCycle( counter, eventCounterAddress, addressModifier, dataWidthReg ); 
  if( error ) exitIfError( error, "Failure reading the Event Counter!"); 
  eventCounter = counter[1]<<0x08 | counter[0];
  EChannelLog.debugStream() << "Event Counter = " << eventCounter;

  return eventCounter;
}

//----------------------------------------
unsigned char* EChannels::ReadMemory( unsigned short dataLength ) const
{
  // -> possible shenanigans! -> 
  /* if (dataLength%2) {dataLength -= 1;} else {dataLength -= 2;} //must be even  //TODO: should this be in ReadDPMPointer? */
  EChannelLog.debugStream() << "ReadMemory for buffer size = " << dataLength;
  unsigned char *dataBuffer = new unsigned char [dataLength];

  int error = ReadBLT( dataBuffer, dataLength, receiveMemoryAddress, bltAddressModifier, dataWidthSwapped );
  if( error ) exitIfError( error, "Error in BLT ReadCycle!");

  return dataBuffer;
}

//----------------------------------------
void EChannels::WriteMessageToMemory( unsigned char* message, int messageLength ) const
{
  EChannelLog.debugStream() << "Send Memory Address   = 0x" << std::hex << sendMemoryAddress;
  EChannelLog.debugStream() << "Message Length        = " << messageLength;
  int error = WriteCycle( messageLength, message, sendMemoryAddress, addressModifier, dataWidthSwappedReg );
  if( error ) exitIfError( error, "Failure writing to CROC FIFO!"); 
}

//----------------------------------------
void EChannels::WriteFrameRegistersToMemory( std::tr1::shared_ptr<LVDSFrame> frame ) const
{
  EChannelLog.debugStream() << "WriteFrameRegistersToMemory";
  frame->MakeMessage();
  this->WriteMessageToMemory( frame->GetOutgoingMessage(), frame->GetOutgoingMessageLength() );
}

//----------------------------------------
void EChannels::WriteFPGAProgrammingRegistersDumpReadToMemory( std::tr1::shared_ptr<FPGAFrame> frame ) const
{
  // Note: this function does not send the message! It only writes the message to the CROC memory.
  frame->MakeShortMessage();  // Use the "DumpRead" option.
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
  // Note: this function does not retrieve the data from memory! It only loads it and reads the pointer.
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
    EChannelLog.fatalStream() << "Fatal error for Channel with address = 0x" << std::hex << this->channelDirectAddress;
    EChannelLog.fatalStream() << " CROC Number = " << this->GetParentCROCNumber() << "; Channel Number = " << channelNumber;
    EChannelLog.fatalStream() << msg;
    this->GetController()->ReportError(error);
    exit(error);
  }
}

#endif
