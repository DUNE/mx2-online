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
EChannels::EChannels( unsigned int vmeAddress, unsigned int number, log4cpp::Appender* appender, Controller* controller ) : 
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

	dpmPointer    = 0;     // start pointing at zero

  EChannelLog.setPriority(log4cpp::Priority::DEBUG);
}

//----------------------------------------
EChannels::~EChannels() 
{
	for (std::vector<feb*>::iterator p=febsVector.begin(); p!=febsVector.end(); p++) delete (*p);
	febsVector.clear();
}

//----------------------------------------
unsigned int EChannels::GetChannelNumber() 
{
	return channelNumber;
}

//----------------------------------------
unsigned int EChannels::GetParentECROCAddress() 
{
	return this->address;
}

//----------------------------------------
unsigned int EChannels::GetDirectAddress() 
{
	return channelDirectAddress;
}

//----------------------------------------
unsigned int EChannels::GetReceiveMemoryAddress()
{
	return receiveMemoryAddress;
}

//----------------------------------------
unsigned int EChannels::GetSendMemoryAddress()
{
	return sendMemoryAddress;
}

//----------------------------------------
unsigned int EChannels::GetFramePointersMemoryAddress() 
{
	return framePointersMemoryAddress;
}

//----------------------------------------
unsigned int EChannels::GetConfigurationAddress() 
{
	return configurationAddress;
}

//----------------------------------------
unsigned int EChannels::GetCommandAddress() 
{
	return commandAddress;
}

//----------------------------------------
unsigned int EChannels::GetEventCounterAddress() 
{
	return eventCounterAddress;
}

//----------------------------------------
unsigned int EChannels::GetFramesCounterAndLoopDelayAddress() 
{
	return framesCounterAndLoopDelayAddress;
}

//----------------------------------------
unsigned int EChannels::GetFrameStatusAddress() 
{
	return frameStatusAddress;
}

//----------------------------------------
unsigned int EChannels::GetTxRxStatusAddress() 
{
	return txRxStatusAddress;
}

//----------------------------------------
unsigned int EChannels::GetReceiveMemoryPointerAddress() 
{
	return receiveMemoryPointerAddress;
}

//----------------------------------------
unsigned int EChannels::GetDPMPointer() 
{
	return dpmPointer;
}

//----------------------------------------
void EChannels::SetDPMPointer( unsigned short pointer ) 
{
	dpmPointer = pointer;
}

//----------------------------------------
unsigned char* EChannels::GetBuffer() 
{
	return buffer;
}

//----------------------------------------
void EChannels::SetBuffer( unsigned char *data ) 
{
	/*! \fn 
	 * Puts data into the data buffer assigned to this channel.
	 * \param data the data buffer
	 */

	EChannelLog.debugStream() << "     Setting Buffer for Chain " << this->GetChannelNumber();
	buffer = new unsigned char [(int)dpmPointer];
	for (int i=0;i<(int)dpmPointer;i++) {
		buffer[i]=data[i];
		EChannelLog.debugStream() << "       SetBuffer: buffer[" 
      << std::setfill('0') << std::setw( 3 ) << i  << "] = 0x" 
      << std::setfill('0') << std::setw( 2 ) << std::hex << buffer[i];
	}
	EChannelLog.debugStream() << "     Done with SetBuffer... Returning...";
	return; 
}

//----------------------------------------
void EChannels::DeleteBuffer() 
{
	delete [] buffer;
}

//----------------------------------------
int EChannels::DecodeStatusMessage() 
{
	/* TODO: Re-implement this correctly for new channels. */
	return 0;
}

//----------------------------------------
int EChannels::CheckHeaderErrors(int dataLength)
{                  
	/* TODO: Re-implement this correctly for new channels. */
	return 0;
}

//----------------------------------------
void EChannels::AddFEB( feb* FEB ) 
{
	febsVector.push_back( FEB );
}

//----------------------------------------
std::vector<feb*>* EChannels::GetFebVector() 
{
	return &febsVector;
}

//----------------------------------------
feb* EChannels::GetFebVector( int index /* should always equal FEB address */ ) 
{
	return febsVector[index];
}

//----------------------------------------
void EChannels::ClearAndResetStatusRegister()
{
  EChannelLog.debugStream() << " Command Address        = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << commandAddress;
  EChannelLog.debugStream() << " Address Modifier       = " 
    << (CVAddressModifier)addressModifier;
  EChannelLog.debugStream() << " Data Width (Registers) = " << dataWidthReg;

  int error = WriteCycle( 2,  RegisterWords::channelReset,  commandAddress, addressModifier, dataWidthReg ); 
  if( error ) exitIfError( error, "Failure clearing the status!");
}

//----------------------------------------
unsigned short EChannels::ReadFrameStatusRegister()
{
  unsigned char receivedMessage[] = {0x0,0x0};
  EChannelLog.debugStream() << " Frame Status Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << frameStatusAddress;

  int error = ReadCycle(receivedMessage, frameStatusAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure reading Frame Status!");

  return ( (receivedMessage[1] << 8) | receivedMessage[0] );
}

//----------------------------------------
unsigned short EChannels::ReadTxRxStatusRegister()
{
  unsigned char receivedMessage[] = {0x0,0x0};
  EChannelLog.debugStream() << " Tx/Rx Status Address = 0x" 
    << std::setfill('0') << std::setw( 8 ) << std::hex 
    << txRxStatusAddress;

  int error = ReadCycle(receivedMessage, txRxStatusAddress, addressModifier, dataWidthReg); 
  if( error ) exitIfError( error, "Failure reading Tx/Rx Status!");

  return ( (receivedMessage[1] << 8) | receivedMessage[0] );
}



#endif
