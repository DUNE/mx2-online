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
    log4cpp::Appender* appender, const Controller* controller ) : 
  VMECommunicator( vmeAddress, appender, controller )
{
	/*! \fn 
	 * constructor takes the following arguments:
	 * \param vmeAddress  :  The channel base address (already bit-shifted)
	 * \param number      :  The channel number (0-3)
   * \param *appender   :  Pointer to the log4cpp appender.
   * \param *controller :  Pointer to the VME 2718 Controller servicing this device.
	 */
	channelNumber        = number;       //the channel number (0-3 here, 1-4 is stenciled on the cards themselves)
	channelDirectAddress = this->address + EChannelOffset * (unsigned int)(channelNumber);
  echanAppender        = appender;
  if ( echanAppender == 0 ) {
    std::cout << "EChannel Log Appender is NULL!" << std::endl;
    exit(EXIT_CROC_UNSPECIFIED_ERROR);
  }
  EChannelLog.setPriority(log4cpp::Priority::DEBUG);  

  receiveMemoryAddress             = channelDirectAddress + (unsigned int)ECROCReceiveMemory;
  sendMemoryAddress                = channelDirectAddress + (unsigned int)ECROCSendMemory;
  framePointersMemoryAddress       = channelDirectAddress + (unsigned int)ECROCFramePointersMemory;
  configurationAddress             = channelDirectAddress + (unsigned int)ECROCConfiguration;
  commandAddress                   = channelDirectAddress + (unsigned int)ECROCCommand;
  eventCounterAddress              = channelDirectAddress + (unsigned int)ECROCEventCounter;
  framesCounterAndLoopDelayAddress = channelDirectAddress + (unsigned int)ECROCFramesCounterAndLoopDelay;
  frameStatusAddress               = channelDirectAddress + (unsigned int)ECROCFrameStatus;
  txRxStatusAddress                = channelDirectAddress + (unsigned int)ECROCTxRxStatus;
  receiveMemoryPointerAddress      = channelDirectAddress + (unsigned int)ECROCReceiveMemoryPointer;
}

//----------------------------------------
EChannels::~EChannels() 
{
  for (std::vector<FEB*>::iterator p=FEBsVector.begin(); p!=FEBsVector.end(); p++) delete (*p);
  FEBsVector.clear();
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
  return ( this->address >> ECROCAddressShift);
}

//----------------------------------------
unsigned int EChannels::GetDirectAddress() const
{
  return channelDirectAddress;
}

//----------------------------------------
int EChannels::DecodeStatusMessage( const unsigned short& status ) const
{
  /* TODO: Re-implement this correctly for new channels. */
  return 0;
}

//----------------------------------------
int EChannels::CheckHeaderErrors(int dataLength) const
{                  
  /* TODO: Re-implement this correctly for new channels. */
  return 0;
}

//----------------------------------------
void EChannels::SetupNFEBs( int nFEBs )
{
  EChannelLog.debugStream() << "SetupNFEBs for " << nFEBs << " FEBs...";
  if ( ( nFEBs < 0 ) || (nFEBs > 10) ) {
    EChannelLog.fatalStream() << "Cannot have less than 0 or more than 10 FEBs on a Channel!";
    exit(EXIT_CONFIG_ERROR);
  }
  for ( int i=1; i<=nFEBs; ++i ) {
    EChannelLog.debugStream() << "Setting up FEB " << i << " ...";
    FEB *feb = new FEB( (febAddresses)i, echanAppender );
    if ( isAvailable( feb ) ) {
      FEBsVector.push_back( feb );
    } else {
      EChannelLog.fatalStream() << "Requested FEB with address " << i << " is not avialable!";
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
std::vector<FEB*>* EChannels::GetFEBVector() 
{
  return &FEBsVector;
}

//----------------------------------------
FEB* EChannels::GetFEBVector( int index /* should always equal FEB address - 1 (vect:0..., addr:1...) */ ) 
{
  // TODO: add check for null here? or too slow? (i.e., live fast and dangerouss)
  // Check that address = index?
  // Maybe add a precompiler flag, SAFE_MODE or something, that makes these checks, 
  // but we wouldn't use it when optimizing for speed...
  return FEBsVector[index];
}

//----------------------------------------
bool EChannels::isAvailable( FEB* feb ) const
{
  EChannelLog.debugStream() << "isAvailable FEB with class address = " << feb->GetBoardNumber();
  bool available = false;
  this->ClearAndResetStatusRegister();

  unsigned short dataLength = this->ReadFPGAProgrammingRegistersToMemory( feb );
  unsigned char* dataBuffer = this->ReadMemory( dataLength ); 

  feb->message = dataBuffer;
  feb->DecodeRegisterValues(dataLength);
  EChannelLog.debugStream() << "Decoded FEB address = " << (int)feb->GetBoardID();
  if( (int)feb->GetBoardID() == feb->GetBoardNumber() ) available = true;

  feb->message = 0;
  delete [] dataBuffer;

  EChannelLog.debugStream() << "FEB " << feb->GetBoardNumber() << " isAvailable = " << available;
  return available;
}

//----------------------------------------
void EChannels::ClearAndResetStatusRegister() const
{
  EChannelLog.debugStream() << "Command Address        = 0x" 
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

  return ( (receivedMessage[1] << 8) | receivedMessage[0] );
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

  return ( (receivedMessage[1] << 8) | receivedMessage[0] );
}


//----------------------------------------
void EChannels::SendMessage() const
{
  //#ifndef GOFAST
  //#endif
  EChannelLog.debugStream() << "SendMessage Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex << commandAddress 
    << "; Message = 0x" << std::hex << RegisterWords::sendMessage[1] << RegisterWords::sendMessage[0];
  int error = WriteCycle( 2, RegisterWords::sendMessage, commandAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure writing to CROC Send Message Register!"); 
}

//----------------------------------------
unsigned short EChannels::WaitForMessageReceived() const
{
  unsigned short status = 0;
  do {
    status = this->ReadFrameStatusRegister();
  } while ( 
      (status & 0x1000) &&   // TODO: MAGIC NUMBERS MUST DIE
      !(status & 0x8000) &&  // send memory full
      !(status & 0x0080) &&  // receive memory full
      !(status & 0x0010) &&  // frame received
      !(status & 0x0008) &&  // timeout error
      !(status & 0x0004) &&  // crc error
      !(status & 0x0002)     // header error
      );
  // TODO decodeStatus(status); // maybe use this in the while instead?
  // TODO if error(status) exit(code); 
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
  } while ( 0 == (status & 0x0400) );  // TODO: MAGIC NUMBERS MUST DIE
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
  if (dataLength%2) {dataLength -= 1;} else {dataLength -= 2;} //must be even  //TODO: should this be in ReadDPMPointer?
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
void EChannels::WriteFPGAProgrammingRegistersToMemory( FEB *feb ) const
{
  // Note: this function does not send the message! It only write the message to the CROC memory.
  feb->MakeMessage(); 
  this->WriteMessageToMemory( feb->GetOutgoingMessage(), feb->GetOutgoingMessageLength() );
  feb->DeleteOutgoingMessage(); 
}

//----------------------------------------
void EChannels::WriteFPGAProgrammingRegistersReadFrameToMemory( FEB *feb ) const
{
  // Note: this function does not send the message! It only write the message to the CROC memory.
  Devices dev     = FPGA;
  Broadcasts b    = None;
  Directions d    = MasterToSlave;
  FPGAFunctions f = Read;
  feb->MakeDeviceFrameTransmit( dev, b, d, f, (unsigned int)feb->GetBoardNumber() );
  this->WriteFPGAProgrammingRegistersToMemory( feb );
}

//----------------------------------------
void EChannels::WriteTRIPRegistersToMemory( FEB *feb, int tripNumber ) const
{
  feb->GetTrip(tripNumber)->MakeMessage();
  this->WriteMessageToMemory( feb->GetTrip(tripNumber)->GetOutgoingMessage(), 
      feb->GetTrip(tripNumber)->GetOutgoingMessageLength() );
  feb->GetTrip(tripNumber)->DeleteOutgoingMessage();
}

//----------------------------------------
void EChannels::WriteTRIPRegistersReadFrameToMemory( FEB *feb, int tripNumber ) const
{
  feb->GetTrip(tripNumber)->SetRead(true);
  this->WriteTRIPRegistersToMemory( feb, tripNumber );
}

//----------------------------------------
unsigned short EChannels::ReadFPGAProgrammingRegistersToMemory( FEB *feb ) const
{
  // Note: this function does not retrieve the data from memory! It only loads it and reads the pointer.
  this->ClearAndResetStatusRegister();
  this->WriteFPGAProgrammingRegistersReadFrameToMemory( feb );
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
