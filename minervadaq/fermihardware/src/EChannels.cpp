#ifndef EChannels_cpp
#define EChannels_cpp
/*! \file EChannels.cpp
*/
/*
11/19/2014 Geoff Savage

Modified EChannels::DecodeStatusMessage() so the SequencerError bit (0x0200)
in the frame status word now triggers an error.
*/

#include <iomanip>

#include "EChannels.h"
#include "EChannelsConfigRegParser.h"
#include "FrontEndBoard.h"
#include "RegisterWords.h"
#include "exit_codes.h"

log4cpp::Category& EChannelLog = log4cpp::Category::getInstance(std::string("EChannel"));

const short int EChannels::eventCounterMask  = 0x3FFF;
const short int EChannels::eventCounterBits  = 0;  
const short int EChannels::receiveMemoryMask = 0x8000; 
const short int EChannels::receiveMemoryBits = 15; 

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
#ifdef GOFAST
  EChannelLog.setPriority(log4cpp::Priority::INFO);
#else
  EChannelLog.setPriority(log4cpp::Priority::DEBUG);
#endif

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
  headerDataAddress                = channelDirectAddress + (unsigned int)VMEModuleTypes::ECROCHeaderData;
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
std::pair<int,std::string> EChannels::DecodeStatusMessage( const unsigned short& status ) const
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
  if (status & VMEModuleTypes::SequencerError) {
    statusBitsDecoded += "SequencerError|";
    frameErrors++;
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
#ifndef GOFAST
  EChannelLog.debugStream() << "FrameStatus 0x" << std::hex << status << 
    " for ECROC " << std::dec << this->GetParentCROCNumber() << "; Channel " << 
    this->channelNumber << "; " << statusBitsDecoded;
#endif
  std::pair<int,std::string> retval( frameErrors, statusBitsDecoded );
  return retval;
}
//----------------------------------------
std::pair<int,std::string> EChannels::DecodeTxRxMessage( const unsigned short& status ) const
{
  int frameErrors = 0;
  std::string statusBitsDecoded = "|";

  if (status & VMEModuleTypes::TXUnused) {
    statusBitsDecoded += "TXUnused|";
  }
  if (status & VMEModuleTypes::TXRstTpInCmdFound) {
    statusBitsDecoded += "TXRstTpInCmdFound|";
  }
  if (status & VMEModuleTypes::TXRstTpInCmdTimeout) {
    statusBitsDecoded += "TXRstTpInCmdTimeout|";
  }
  if (status & VMEModuleTypes::RXRstTpOutCmdSent) {
    statusBitsDecoded += "RXRstTpOutCmdSent|";
  }
  if (status & VMEModuleTypes::RXEncInRFOK) {
    statusBitsDecoded += "RXEncInRFOK|";
  }
  if (status & VMEModuleTypes::RXEncInCmdMatch) {
    statusBitsDecoded += "RXEncInCmdMatch|";
  }
  if (status & VMEModuleTypes::RXEncInCmdFound) {
    statusBitsDecoded += "RXEncInCmdFound|";
  }
  if (status & VMEModuleTypes::RXEncInCmdTimeout) {
    statusBitsDecoded += "RXEncInCmdTimeout|";
  }
  if (status & VMEModuleTypes::TXEncOutCmdSent) {
    statusBitsDecoded += "TXEncOutCmdSent|";
  }
  if (status & VMEModuleTypes::TXSync2) {
    statusBitsDecoded += "TXSync2|";
  }
  if (status & VMEModuleTypes::TXLockStable) {
    statusBitsDecoded += "TXLockStable|";
  }
  if (status & VMEModuleTypes::TXLockError) {
    statusBitsDecoded += "TXLockError|";
    frameErrors++;
  }
  if (status & VMEModuleTypes::TXSync1) {
    statusBitsDecoded += "TXSync1|";
  }
  if (status & VMEModuleTypes::RXLockStable) {
    statusBitsDecoded += "RXLockStable|";
  }
  if (status & VMEModuleTypes::RXLockError) {
    statusBitsDecoded += "RXLockError|";
    frameErrors++;
  }
  if (status & VMEModuleTypes::RXLockMSB) {
    statusBitsDecoded += "RXLockMSB|";
  }
#ifndef GOFAST
  EChannelLog.debugStream() << "TxRxStatus 0x" << std::hex << status << 
    " for ECROC " << std::dec << this->GetParentCROCNumber() << "; Channel " << 
    this->channelNumber << "; " << statusBitsDecoded;
#endif
  std::pair<int,std::string> retval( frameErrors, statusBitsDecoded );
  return retval;
}

//----------------------------------------
//! We do not do FEB configuration here. We only check to see if the FEB exists.
void EChannels::SetupNFrontEndBoards( int nFEBs )
{
  EChannelLog.infoStream() << "SetupNFrontEndBoards for " << nFEBs << " FEBs...";
  if ( ( nFEBs < 0 ) || (nFEBs > 10) ) {
    EChannelLog.fatalStream() << "Cannot have less than 0 or more than 10 FEBs on a Channel!";
    VMEThrow("Impossible number of FEBs requested for setup!");
  }
  if ( 0 == nFEBs ) return;
  std::tr1::shared_ptr<EChannelsConfigRegParser> config = this->GetChannelConfiguration();
  EChannelLog.infoStream() << "Channel " << this->channelNumber << " runs firmware ver " << 
    config->ChannelFirmware();
  unsigned char febFirmware = 0;
  for ( int i=1; i<=nFEBs; ++i ) {
    EChannelLog.infoStream() << "Setting up FEB " << i << " ...";
    FrontEndBoard *feb = 
      new FrontEndBoard( (FrameTypes::FEBAddresses)i, this->GetAddress(), this->GetCrateNumber() );
    if ( 1 == i ) {
      febFirmware = isAvailable( feb );
    }
    else {
      if ( febFirmware != isAvailable( feb ) ) {
        VMEThrow("FEB firwmare mismatch!");
      }
    }
    if ( 0 < febFirmware ) {
      FrontEndBoardsVector.push_back( feb );
    } else {
      EChannelLog.fatalStream() << "Requested FrontEndBoard with address " << i << " is not avialable!";
      VMEThrow("FEB not available!");
    }
  }
  config->SetNFEBs( static_cast<unsigned short>(nFEBs) );
  this->SetChannelConfiguration( config );
  this->SetupHeaderData( this->GetController()->GetCrateNumber(), 
      this->GetParentCROCNumber(),
      febFirmware );
#ifndef GOFAST
  unsigned short header = this->GetHeaderData();
  EChannelLog.debugStream() << " Read-back header data: 0x" << std::hex << header;
#endif
}

//----------------------------------------
//! Check carefully whenever we update FEB or Channel firmware.
void EChannels::ConfigureForStandardDataTaking() const
{
  std::tr1::shared_ptr<EChannelsConfigRegParser> config = this->GetChannelConfiguration();
  config->EnableSequencerReadout();
  //if using FEB v91
  //config->SetFourBitHitEncoding();
  //if using FEB v95
  config->SetFiveBitHitEncoding();
  config->SetFullPipelineReadout();
  config->DisableChannelTestPulse();
  config->DisableChannelReset();
  this->SetChannelConfiguration( config );
}

//----------------------------------------
//! Only update the enable bit.
void EChannels::EnableSequencerReadout() const
{
  std::tr1::shared_ptr<EChannelsConfigRegParser> config = this->GetChannelConfiguration();
  config->EnableSequencerReadout();
  this->SetChannelConfiguration( config );
}

//----------------------------------------
//! Only update the enable bit.
void EChannels::DisableSequencerReadout() const
{
  std::tr1::shared_ptr<EChannelsConfigRegParser> config = this->GetChannelConfiguration();
  config->DisableSequencerReadout();
  this->SetChannelConfiguration( config );
}

//----------------------------------------
//! Only update the hit bit. Use four bits for FEB max hits less than 15.
void EChannels::UseFourBitHitEncoding() const
{
  std::tr1::shared_ptr<EChannelsConfigRegParser> config = this->GetChannelConfiguration();
  config->SetFourBitHitEncoding();
  this->SetChannelConfiguration( config );
}

//----------------------------------------
//! Only update the hit bit. Use five bits for FEB max hits less than 31.
void EChannels::UseFiveBitHitEncoding() const
{
  std::tr1::shared_ptr<EChannelsConfigRegParser> config = this->GetChannelConfiguration();
  config->SetFiveBitHitEncoding();
  this->SetChannelConfiguration( config );
}

//----------------------------------------
//! Only update the hit bit. Single pipe readout might be appropriate for LI.
void EChannels::UseSinglePipelineReadout() const
{
  std::tr1::shared_ptr<EChannelsConfigRegParser> config = this->GetChannelConfiguration();
  config->SetSinglePipelineReadout();
  this->SetChannelConfiguration( config );
}

//----------------------------------------
//! Only update the hit bit. Read all timed hits and the untimed hit.
void EChannels::UseFullPipelineReadout() const
{
  std::tr1::shared_ptr<EChannelsConfigRegParser> config = this->GetChannelConfiguration();
  config->SetFullPipelineReadout();
  this->SetChannelConfiguration( config );
}

//----------------------------------------
std::tr1::shared_ptr<EChannelsConfigRegParser> EChannels::GetChannelConfiguration() const
{
  unsigned short configuration = 0;
  unsigned char receivedMessage[] = {0x0,0x0};

#ifndef GOFAST
  EChannelLog.debugStream() << "Read ReceiveMemoryPointer Address = 0x" << std::hex << configurationAddress;
#endif
  int error = ReadCycle( receivedMessage, configurationAddress, addressModifier, dataWidthReg); 
  if( error ) throwIfError( error, "Failure reading the Channel Configuration!"); 
  configuration = receivedMessage[1]<<0x08 | receivedMessage[0];
#ifndef GOFAST
  EChannelLog.debugStream() << "Channel " << channelNumber << " Configuration = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << configuration;
#endif
  std::tr1::shared_ptr<EChannelsConfigRegParser> config(
      new EChannelsConfigRegParser(configuration));

  return config;
}

//----------------------------------------
void EChannels::SetChannelConfiguration( std::tr1::shared_ptr<EChannelsConfigRegParser> config ) const
{
  unsigned short int configuration = config.get()->RawValue();
  unsigned char msg[] = {0x0,0x0};
  msg[0] = configuration & 0xFF;
  msg[1] = (configuration & 0xFF00)>>8;
  this->SetChannelConfiguration( msg );
}

//----------------------------------------
void EChannels::SetChannelConfiguration( unsigned char* message ) const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "Channel " << channelNumber << " Target Configuration: 0x" 
    << std::setfill('0') << std::setw( 2 ) << std::hex << (int)message[1] << (int)message[0];
#endif
  int error = WriteCycle( 2, message, configurationAddress, addressModifier, dataWidthReg); 
  if( error ) throwIfError( error, "Failure writing to Channel Configuration Register!"); 
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
unsigned char EChannels::isAvailable( FrontEndBoard* feb ) const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "isAvailable FrontEndBoard with class address = " << feb->GetBoardNumber();
#endif
  unsigned char firmware = 0;

  std::tr1::shared_ptr<FPGAFrame> frame = feb->GetFPGAFrame();
  unsigned int dataLength = this->ReadFPGAProgrammingRegistersToMemory( frame );
  unsigned char* dataBuffer = this->ReadMemory( dataLength ); 

  frame->SetReceivedMessage(dataBuffer);
  frame->DecodeRegisterValues();
#ifndef GOFAST
  EChannelLog.debugStream() << "Decoded FrontEndBoard address = " << (int)feb->GetBoardNumber();
#endif
  if( (int)feb->GetBoardNumber() == frame->GetFEBNumber() ) 
    firmware = frame->GetFirmwareVersion();

  EChannelLog.infoStream() << "FrontEndBoard " << feb->GetBoardNumber() 
    << " isAvailable with firmware = " << (int)firmware;
  return firmware;
}

//----------------------------------------
void EChannels::ResetSendMemoryPointer() const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "Command Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << commandAddress;
#endif
  int error = WriteCycle( 2,  RegisterWords::resetSendMemory,  
      commandAddress, addressModifier, dataWidthReg ); 
  if( error ) throwIfError( error, "Failure reseting the send memory pointer!");
}

//----------------------------------------
void EChannels::ResetReceiveMemoryPointer() const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "Command Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << commandAddress;
#endif
  int error = WriteCycle( 2,  RegisterWords::resetReceiveMemory, 
      commandAddress, addressModifier, dataWidthReg ); 
  if( error ) throwIfError( error, "Failure reseting the receive memory pointer!");
}

//----------------------------------------
void EChannels::ClearAndResetStatusRegister() const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "Clear And Reset Command Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << commandAddress;
#endif
  int error = WriteCycle( 2,  RegisterWords::channelReset,  
      commandAddress, addressModifier, dataWidthReg ); 
  if( error ) throwIfError( error, "Failure clearing the status!");
}

//----------------------------------------
unsigned short EChannels::ReadFrameCounterRegister() const
{
  unsigned char receivedMessage[] = {0x0,0x0};
#ifndef GOFAST
  EChannelLog.debugStream() << "Frame Counter Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << framesCounterAndLoopDelayAddress; 
#endif

  int error = ReadCycle(receivedMessage, framesCounterAndLoopDelayAddress, addressModifier, dataWidthReg); 
  if( error ) throwIfError( error, "Failure reading Frame Status!");

  unsigned short frameCount = ( (receivedMessage[1] << 8) | receivedMessage[0] ) & VMEModuleTypes::FramesCounterMask;
#ifndef GOFAST
  EChannelLog.debugStream() << " Raw Register = 0x" << std::hex << 
    ( (receivedMessage[1] << 8) | receivedMessage[0] );
  EChannelLog.debugStream() << " Frame Count  = " << std::dec << frameCount;
#endif

  return frameCount;
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
  if( error ) throwIfError( error, "Failure reading Frame Status!");

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
  if( error ) throwIfError( error, "Failure reading Tx/Rx Status!");

  unsigned short status = (receivedMessage[1] << 8) | receivedMessage[0];
#ifndef GOFAST
  EChannelLog.debugStream() << " Status = 0x" << std::hex << status;
#endif

  return status;
}


//----------------------------------------
void EChannels::ResetEventCounter() const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "Command Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex << commandAddress 
    << "; Message = 0x" << std::hex << (int)RegisterWords::clearEventCounter[1] 
    << (int)RegisterWords::clearEventCounter[0];
#endif
  int error = WriteCycle( 2, RegisterWords::clearEventCounter, commandAddress, 
      addressModifier, dataWidthReg); 
  if( error ) throwIfError( error, "Failure Clearing Event Counter!"); 

}

//----------------------------------------
void EChannels::SendMessage() const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "SendMessage Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex << commandAddress 
    << "; Message = 0x" << std::hex << (int)RegisterWords::sendMessage[1] 
    << (int)RegisterWords::sendMessage[0];
#endif
  int error = WriteCycle( 2, RegisterWords::sendMessage, commandAddress, addressModifier, dataWidthReg); 
  if( error ) throwIfError( error, "Failure writing to EChannel Send Message Register!"); 
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
  std::pair<int,std::string> error = DecodeStatusMessage(status);
  if (0 != error.first) {
    VMEThrow( error.second );
  }
#ifndef GOFAST
  EChannelLog.debugStream() << " Decoded Status Error Level = " << error.first;
  EChannelLog.debugStream() << "Message was received with status = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex << status;
#endif
  return status;
}

//----------------------------------------
unsigned short EChannels::WaitForSequencerReadoutCompletion() const
{
  unsigned short status = 0;
  unsigned short txrx = 0;
  do {
    status = this->ReadFrameStatusRegister();
    txrx = this->ReadTxRxStatusRegister();
    std::pair<int,std::string> stat_error = DecodeStatusMessage( status );
    std::pair<int,std::string> txrx_error = DecodeTxRxMessage( txrx );
    if (0 != stat_error.first) {
      EChannelLog.errorStream() << "   Status: 0x" << std::hex << status;
      EChannelLog.errorStream() << "   TxRx:   0x" << std::hex << txrx;
      EChannelLog.errorStream() << "   Frame Count = " << std::dec << this->ReadFrameCounterRegister();
      VMEThrow( stat_error.second );
    }
    if (0 != txrx_error.first) {
      EChannelLog.errorStream() << "   Status: 0x" << std::hex << status;
      EChannelLog.errorStream() << "   TxRx:   0x" << std::hex << txrx;
      EChannelLog.errorStream() << "   Frame Count = " << std::dec << this->ReadFrameCounterRegister();
      VMEThrow( txrx_error.second );
    }
  } while ( 0 == (status & VMEModuleTypes::SendMemoryRDFEDone) );  
  return status;
}

//----------------------------------------
//! The v2 CROCE uses a 128 kB memory. This is not fully addressable with a single 16-bit 
//! register. Therefore, the upper-most bit lives inside the EventCounter register.
unsigned int EChannels::ReadDPMPointer() const
{
  unsigned short receiveMemoryPointer = 0;
  unsigned char pointer[] = {0x0,0x0};

#ifndef GOFAST
  EChannelLog.debugStream() << "Read ReceiveMemoryPointer Address = 0x" 
    << std::hex << receiveMemoryPointerAddress;
#endif
  int error = ReadCycle( pointer, receiveMemoryPointerAddress, addressModifier, dataWidthReg ); 
  if( error ) throwIfError( error, "Failure reading the Receive Memory Pointer!"); 
  receiveMemoryPointer = pointer[1]<<0x08 | pointer[0];
#ifndef GOFAST
  EChannelLog.debugStream() << "16 bit Pointer Length = " << receiveMemoryPointer;
#endif

  unsigned short eventCounter = 0;
  unsigned char counter[] = {0x0,0x0};

#ifndef GOFAST
  EChannelLog.debugStream() << "Read EventCounter Address = 0x" << std::hex << eventCounterAddress;
#endif
  error = ReadCycle( counter, eventCounterAddress, addressModifier, dataWidthReg ); 
  if( error ) throwIfError( error, "Failure reading the Event Counter!"); 
  eventCounter = ( (counter[1]<<0x08 | counter[0]) & receiveMemoryMask ) >> receiveMemoryBits;
#ifndef GOFAST
  EChannelLog.debugStream() << "17th Pointer Bit = " << eventCounter;
#endif

  unsigned int finalPointer = static_cast<unsigned int>(receiveMemoryPointer);
  finalPointer |= (eventCounter << 16);

#ifndef GOFAST
  EChannelLog.debugStream() << "17 bit Pointer Length = " << finalPointer;
#endif
  return finalPointer;
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
  if( error ) throwIfError( error, "Failure reading the Event Counter!"); 
  eventCounter = counter[1]<<0x08 | counter[0];
#ifndef GOFAST
  EChannelLog.debugStream() << "Event Counter = " << eventCounter;
#endif

  return (eventCounter & eventCounterMask);
}

//----------------------------------------
unsigned char* EChannels::ReadMemory( unsigned int dataLength ) const
{
#ifndef GOFAST
  EChannelLog.debugStream() << "ReadMemory for buffer size = " << dataLength;
#endif
  unsigned char *dataBuffer = new unsigned char [dataLength];
  // dataLength should be no more than 17 bits, so it is safe to cast
  int error = ReadBLT( dataBuffer, (int)dataLength, receiveMemoryAddress, 
      bltAddressModifier, dataWidthSwapped );
  if( error ) throwIfError( error, "Error in BLT ReadCycle!");

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
  if( error ) throwIfError( error, "Failure writing to CROC FIFO!"); 
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
  unsigned int dataLength = this->ReadDPMPointer();

  return dataLength;
}

//----------------------------------------
void EChannels::SetupHeaderData( int crateNumber, int crocID, int febFirmware ) const
{
  using namespace VMEModuleTypes;
#ifndef GOFAST
  EChannelLog.debugStream() << "SetupHeaderData for crate " << crateNumber << 
    "; ECROC ID " << crocID << "; FEB firmware version " << febFirmware;
#endif
  int message = 
    ( (crateNumber<<HeaderDataVMECrateIDBits)  & HeaderDataVMECrateIDMask) |
    ( (crocID<<HeaderDataCROCEIDBits)          & HeaderDataCROCEIDMask)    |
    ( (febFirmware<<HeaderDataFEBFirmwareBits) & HeaderDataFEBFirmwareMask) ;
  unsigned short msg = static_cast<unsigned short>( message & 0xFFFF );
  unsigned char hdr[] = {0x0,0x0};
  hdr[0] = (msg & 0xFF00)>>8;
  hdr[1] = msg & 0xFF;
#ifndef GOFAST
  EChannelLog.debugStream() << " Message = 0x" << std::hex << (int)hdr[0] << (int)hdr[1];
#endif
  int error = WriteCycle( 2, hdr, headerDataAddress, addressModifier, dataWidthSwappedReg );
  if( error ) throwIfError( error, "Failure writing to EChannel Header Data Register!"); 
}

//----------------------------------------
unsigned short EChannels::GetHeaderData() const
{
  unsigned char receivedMessage[] = {0x0,0x0};

  int error = ReadCycle(receivedMessage, headerDataAddress, addressModifier, dataWidthReg); 
  if( error ) throwIfError( error, "Failure reading Tx/Rx Status!");

  unsigned short header = (receivedMessage[1] << 8) | receivedMessage[0];
#ifndef GOFAST
  EChannelLog.debugStream() << "Get Header Data = 0x" 
    << std::setfill('0') << std::setw( 4 ) << std::hex 
    << header;
#endif
  return header;
}

//----------------------------------------
void EChannels::throwIfError( int error, const std::string& msg ) const
{
  if (error) {
    std::stringstream ss;
    ss << "Fatal error for device " << (*this);
    ss << "; CROC Number = " << this->GetParentCROCNumber(); 
    ss << "; ";
    ss << msg;
    ss << "; ";
    ss << this->GetController()->ReportError(error);
    EChannelLog.fatalStream() << ss.str(); 
    VMEThrow( ss.str() );
  }
}

#endif
