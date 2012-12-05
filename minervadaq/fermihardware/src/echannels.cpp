#ifndef echannels_cpp
#define echannels_cpp

#include "echannels.h"
#include "exit_codes.h"

/*********************************************************************************
 * Class for creating CROC-E channel objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

// TODO - Be careful about all the "54's" showing up for the number of registers in an FPGA frame.

//----------------------------------------
echannels::echannels( unsigned int vmeAddress, unsigned int number ) 
{
	/*! \fn 
	 * constructor takes the following arguments:
	 * \param vmeAddress:  The channel base address (already bit-shifted)
	 * \param number    :  The channel number
	 */
	channelBaseAddress   = vmeAddress;   //the address for the croc which contains this channel
	channelNumber        = number;       //the channel number (0-3 here, 1-4 is stenciled on the cards themselves)
	channelDirectAddress = channelBaseAddress + 0x4000 * (unsigned int)(channelNumber);
	bltAddressModifier   = cvA32_U_BLT; //the Block Transfer Reads (BLT's) require a special address modifier

	receiveMemoryAddress             = channelDirectAddress + (unsigned int)ecrocReceiveMemory;
	sendMemoryAddress                = channelDirectAddress + (unsigned int)ecrocSendMemory;
	framePointersMemoryAddress       = channelDirectAddress + (unsigned int)ecrocFramePointersMemory;
	configurationAddress             = channelDirectAddress + (unsigned int)ecrocConfiguration;
	commandAddress                   = channelDirectAddress + (unsigned int)ecrocCommand;
	eventCounterAddress              = channelDirectAddress + (unsigned int)ecrocEventCounter;
	framesCounterAndLoopDelayAddress = channelDirectAddress + (unsigned int)ecrocFramesCounterAndLoopDelay;
	frameStatusAddress               = channelDirectAddress + (unsigned int)ecrocFrameStatus;
	txRxStatusAddress                = channelDirectAddress + (unsigned int)ecrocTxRxStatus;
	receiveMemoryPointerAddress      = channelDirectAddress + (unsigned int)ecrocReceiveMemoryPointer;

	channelStatus = 0;     // the channel starts out with no status information kept
	dpmPointer    = 0;     // start pointing at zero
}

//----------------------------------------
echannels::~echannels() 
{
	for (std::vector<feb*>::iterator p=febsVector.begin(); p!=febsVector.end(); p++) delete (*p);
	febsVector.clear();
}

//----------------------------------------
unsigned int echannels::GetChannelNumber() 
{
	return channelNumber;
}

//----------------------------------------
unsigned int echannels::GetParentECROCAddress() 
{
	return channelBaseAddress;
}

//----------------------------------------
unsigned int echannels::GetDirectAddress() 
{
	return channelDirectAddress;
}

//----------------------------------------
CVAddressModifier echannels::GetBLTModifier() 
{
	return bltAddressModifier;
}

//----------------------------------------
unsigned int echannels::GetReceiveMemoryAddress()
{
	return receiveMemoryAddress;
}

//----------------------------------------
unsigned int echannels::GetSendMemoryAddress()
{
	return sendMemoryAddress;
}

//----------------------------------------
unsigned int echannels::GetFramePointersMemoryAddress() 
{
	return framePointersMemoryAddress;
}

//----------------------------------------
unsigned int echannels::GetConfigurationAddress() 
{
	return configurationAddress;
}

//----------------------------------------
unsigned int echannels::GetCommandAddress() 
{
	return commandAddress;
}

//----------------------------------------
unsigned int echannels::GetEventCounterAddress() 
{
	return eventCounterAddress;
}

//----------------------------------------
unsigned int echannels::GetFramesCounterAndLoopDelayAddress() 
{
	return framesCounterAndLoopDelayAddress;
}

//----------------------------------------
unsigned int echannels::GetFrameStatusAddress() 
{
	return frameStatusAddress;
}

//----------------------------------------
unsigned int echannels::GetTxRxStatusAddress() 
{
	return txRxStatusAddress;
}

//----------------------------------------
unsigned int echannels::GetReceiveMemoryPointerAddress() 
{
	return receiveMemoryPointerAddress;
}

//----------------------------------------
unsigned short echannels::GetChannelStatus() 
{
	return channelStatus;
}

//----------------------------------------
void echannels::SetChannelStatus(unsigned short status) 
{
	channelStatus = status;
}

//----------------------------------------
unsigned int echannels::GetDPMPointer() 
{
	return dpmPointer;
}

//----------------------------------------
void echannels::SetDPMPointer( unsigned short pointer ) 
{
	dpmPointer = pointer;
}

//----------------------------------------
unsigned char* echannels::GetBuffer() 
{
	return buffer;
}

//----------------------------------------
void echannels::SetBuffer( unsigned char *data ) 
{
	/*! \fn 
	 * Puts data into the data buffer assigned to this channel.
	 * \param data the data buffer
	 */

#if DEBUG_VERBOSE
	std::cout << "     Setting Buffer for Chain " << this->GetChainNumber() << std::endl;
#endif
	buffer = new unsigned char [(int)dpmPointer];
	for (int i=0;i<(int)dpmPointer;i++) {
		buffer[i]=data[i];
#if DEBUG_VERBOSE
		printf("       SetBuffer: buffer[%03d] = 0x%02X\n",i,buffer[i]);
#endif
	}
#if DEBUG_VERBOSE
	std::cout << "     Done with SetBuffer... Returning..." << std::endl;
#endif
	return; 
}

//----------------------------------------
void echannels::DeleteBuffer() 
{
	delete [] buffer;
}

//----------------------------------------
int echannels::DecodeStatusMessage() 
{
	/* TODO: Re-implement this correctly for new channels. */
	return 0;
}

//----------------------------------------
int echannels::CheckHeaderErrors(int dataLength)
{                  
	/* TODO: Re-implement this correctly for new channels. */
	return 0;
}

//----------------------------------------
void echannels::AddFEB( feb* FEB ) 
{
	febsVector.push_back( FEB );
}

std::vector<feb*>* echannels::GetFebVector() 
{
	return &febsVector;
}

feb* echannels::GetFebVector( int index /* should always equal FEB address */ ) 
{
	return febsVector[index];
}


#endif
