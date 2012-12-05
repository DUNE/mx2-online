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

echannels::echannels(unsigned int a, int b) 
{
	/*! \fn 
	 * constructor takes the following arguments:
	 * \param a:  The channel base address 
	 * \param b:  The channel number
	 */
	channelBaseAddress   = a;     //the address for the croc which contains this channel
	channelNumber        = b;     //the channel number (0-3 here, 1-4 is stenciled on the cards themselves)
	channelDirectAddress = channelBaseAddress + 0x4000 * (unsigned int)(channelNumber);
	FIFOMaxSize   = 2048; // bytes; largest number of bytes the FIFO buffer can hold
	MemoryMaxSize = 6144; // bytes;  largest number of bytes the DPM Memory can hold

	crocRegisters registerOffset = crocInput;
	fifoAddress = channelDirectAddress + (unsigned int)registerOffset; //FIFO address
	registerOffset = crocMemory;
	dpmAddress = channelDirectAddress + (unsigned int)registerOffset; //DPM Address
	registerOffset = crocSendMessage;
	sendMessageAddress = channelDirectAddress + (unsigned int)registerOffset; //Send message register
	registerOffset = crocStatus;
	statusAddress = channelDirectAddress + (unsigned int)registerOffset; //status register
	registerOffset = crocDPMPointer;
	dpmPointerAddress = channelDirectAddress + (unsigned int)registerOffset; //DPM Pointer register
	registerOffset = crocClearStatus;
	clearStatusAddress = channelDirectAddress + (unsigned int)registerOffset; //clear status register

	bltAddressModifier = cvA32_U_BLT; //the Block Transfer Reads (BLT's) require a special address modifier

	channelStatus = 0;     // the channel starts out with no status information kept
	has_febs      = false; // and no feb's loaded
}


echannels::~echannels() 
{
	for (std::vector<feb*>::iterator p=febsVector.begin(); p!=febsVector.end(); p++) delete (*p);
	febsVector.clear();
}


unsigned int echannels::GetReceiveMemoryAddress()
{
	return getReceiveMemoryAddress;
}

unsigned int echannels::GetCrocSendMemoryAddress()
{
	return getCrocSendMemoryAddress;
}

unsigned int echannels::GetFramePointersMemoryAddress()
{
	return getFramePointersMemoryAddress;
}

unsigned int echannels::GetConfigurationAddress()
{
	return getConfigurationAddress;
}

unsigned int echannels::GetCommandAddress()
{
	return getCommandAddress;
}

unsigned int echannels::GetEventCounterAddress()
{
	return getEventCounterAddress;
}

unsigned int echannels::GetFramesCounterAndLoopDelayAddress()
{
	return getFramesCounterAndLoopDelayAddress()
}


unsigned int echannels::GetFrameStatusAddress()
{
	return getFrameStatusAddress;
}

unsigned int echannels::GetTxRxStatusAddress()
{
	return getTxRxStatusAddress;
}

unsigned int echannels::GetReceiveMemoryPointerAddress()
{
	return getReceiveMemoryPointerAddress;
}

unsigned int echannels::GetChannelNumber() 
{
	return channelNumber;
}


void echannels::SetFEBs(int a, int nHits, log4cpp::Appender* appender) 
{
	/*! \fn
	 * This function loads FEB's belonging to this channel into a vector of febs once
	 * the feb has been found
	 * \param a the FEB number
	 * \param nHits max Hits
	 * \param appender log4cpp Appender
	 */
	// if we found this feb on this channel, put it into the list 
	febsVector.push_back(new feb(nHits, false, (febAddresses)a, 54, appender)); 
	return;
}


feb *echannels::MakeTrialFEB(int a, int nHits, log4cpp::Appender* appender) 
{
	/*! \fn 
	 * This function creates a disposable "trial" FEB.
	 * \param a the FEB number
	 * \param nHits max Hits
	 * \param appender log4cpp Appender
	 */
	febAddresses f = (febAddresses)a; //store the trial feb address
	feb *trialFeb = new feb(nHits, false, f, 54, appender); //make up the trial feb
	trialFeb->SetFEBDefaultValues(); //set default values for convenience; be careful about *writing*!
	return trialFeb;
}


int echannels::DecodeStatusMessage() 
{
	/*! \fn 
	 * This function decodes the status message for this channel.
	 */
	// TODO - Actually, we don't want this function returning anything or exiting.  Error 
	// handling decisions should be made in the function that calls this one...
	bool error = false;

	StatusBits checkValue = MessageSent; 
	error = ( (channelStatus & checkValue)!=0 ); // bit should be HIGH
	try {
#if DEBUG_VERBOSE
		std::cout << "\tMessage Sent? " << error << std::endl; 
#endif
		if (!error) throw error;
	} catch (bool e) {
#if DEBUG_VERBOSE
		std::cout << "\tMessage was not sent." << std::endl;
#endif
		// return -103; // Do not want to return on 0x3700...
	}

	checkValue = MessageReceived;
	error = ( (channelStatus & checkValue)!=0 ); // bit should be HIGH
	try {
#if DEBUG_VERBOSE
		std::cout << "\tMessage Received? " << error << std::endl; 
#endif
		if (!error) throw error;
	} catch (bool e) {
#if DEBUG_VERBOSE
		std::cout << "\tMessage was not received." << std::endl;
#endif
		// return -104; // Do not want to return on 0x3700...
	}

	checkValue = CRCError;
	error = ( (channelStatus & checkValue)==0 ); // bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "\tCRC Error? " << !error << std::endl; 
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "\tCRC Error!" << std::endl;
		exit(EXIT_CROC_CRC_ERROR); 
	}

	checkValue = TimeoutError;
	error = ( (channelStatus & checkValue)==0 ); // bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "\tTimeout Error? " << !error << std::endl;
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "\tTimeout Error!" << std::endl;
		exit(EXIT_CROC_TIMEOUT_ERROR); 
	}

	checkValue = FIFONotEmpty;
	error = ( (channelStatus & checkValue)==0 ); // Check FIFO buffer status; bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "\tFIFO Empty? " << !error << std::endl;
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "\tFIFO Not Empty!" << std::endl;
		exit(EXIT_CROC_FIFOEMPTY_ERROR); 
	}

	checkValue = FIFOFull;
	error = ( (channelStatus & checkValue)==0 ); // Check FIFO buffer status; bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "\tFIFO Full? " << !error << std::endl;
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "\tFIFO Full!" << std::endl;
		exit(EXIT_CROC_FIFOFULL_ERROR); 
	}

	checkValue = DPMFull;
	error = ( (channelStatus & checkValue)==0 ); // Check DPM status; bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "\tDPM Full? " << !error << std::endl;
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "\tDPM Full!" << std::endl;
		exit(EXIT_CROC_DPMFULL_ERROR); 
	}

	// PLL?, etc.?

	return 0;
}


void echannels::SetBuffer(unsigned char *b) 
{
	/*! \fn 
	 * Puts data into the data buffer assigned to this channel.
	 * \param b the data buffer
	 */

#if DEBUG_VERBOSE
	std::cout << "     Setting Buffer for Chain " << this->GetChainNumber() << std::endl;
#endif
	buffer = new unsigned char [(int)dpmPointer];
	for (int i=0;i<(int)dpmPointer;i++) {
		buffer[i]=b[i];
#if DEBUG_VERBOSE
		printf("       SetBuffer: buffer[%03d] = 0x%02X\n",i,buffer[i]);
#endif
	}
#if DEBUG_VERBOSE
	std::cout << "     Done with SetBuffer... Returning..." << std::endl;
#endif
	return; 
}


int echannels::CheckHeaderErrors(int dataLength)
{                  
	/*! \fn echannels::CheckHeaderErrors(int dataLength)
	 *
	 * Check incoming message header data for errors by checking the raw data buffer in the channel.
	 * This function assumes the buffer begins with index 0 (there is only one frame of data in the 
	 * buffer).
	 *
	 * \param int dataLength, the length of the buffer in memory (from the DPM Pointer value)
	 */
	int buffLen = ((buffer[ResponseLength1]<<8)|buffer[ResponseLength0]) + 2;
	if (buffLen%2) buffLen++;
	if ( dataLength != buffLen ) {
		std::cout << "\tInvalid Message Length!" << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	if ( !(buffer[FrameStart] & Direction) ) {
		std::cout << "\tCheckForErrors: Direction: " << !(buffer[FrameStart] & Direction) << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	if ( !(buffer[DeviceStatus] & DeviceOK) ) {
		std::cout << "\tCheckForErrors: DeviceOK: " << !(buffer[DeviceStatus] & DeviceOK) << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	if ( !(buffer[DeviceStatus] & FunctionOK) ) {
		std::cout << "\tCheckForErrors: FunctionOK: " << !(buffer[DeviceStatus] & FunctionOK) << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	if ( !(buffer[FrameStatus] & CRCOK) ) {
		std::cout << "\tCheckForErrors: CRCOK: " << !(buffer[FrameStatus] & CRCOK) << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	if ( !(buffer[FrameStatus] & EndHeader) ) {
		std::cout << "\tCheckForErrors: EndHeader: " << !(buffer[FrameStatus] & EndHeader) << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	if ( (buffer[FrameStatus] & MaxLen) ) {
		std::cout << "\tCheckForErrors: MaxLen: " << (buffer[FrameStatus] & MaxLen) << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	if ( (buffer[FrameStatus] & SecondStart) ) {
		std::cout << "\tCheckForErrors: SecondStart: " << (buffer[FrameStatus] & SecondStart) << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	if ( (buffer[FrameStatus] & NAHeader) ) {
		std::cout << "\tCheckForErrors: NAHeader: " << (buffer[FrameStatus] & NAHeader) << std::endl;
		std::cout << "\t\tCROC = " << (channelBaseAddress>>16) << ", Chain = " << chainNumber << std::endl;
		return 1;
	}
	return 0; // no errros
}



#endif
