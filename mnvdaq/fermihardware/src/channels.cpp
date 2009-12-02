#ifndef channels_cpp
#define channels_cpp

#include "channels.h"

/*********************************************************************************
* Class for creating Chain Read-Out Controller channel objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
**********************************************************************************/

channels::channels(unsigned int a, int b) 
{
/*! \fn 
 * constructor takes the following arguments:
 * \param a:  The channel base address 
 * \param b:  The channel number
 */
	channelBaseAddress = a; //the address for the croc which contains this channel
	channelNumber = b; //the channel number (0-3 here, 1-4 is stenciled on the cards themselves)
	channelDirectAddress = channelBaseAddress + 0x4000 * (unsigned int)(channelNumber);
	FIFOMaxSize = 2048; // bytes; largest number of bytes the FIFO buffer can hold
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

	bltAddressModifier = cvA24_U_BLT; //the Block Transfer Reads (BLT's) require a special address modifier

	channelStatus = 0; //the channel starts out with no status information kept
	has_febs=false; //and no feb's loaded

	// std::string filename;
	// std::stringstream channel_no;
	// channel_no<<channelDirectAddress;
	// filename = "channel_"+channel_no.str();
	// log_file.open(filename.c_str());
}


void channels::SetFEBs(int a, int nHits) 
{
/*! \fn
 * This function loads FEB's belonging to this channel into a vector of febs once
 * the feb has been found
 * \param a the FEB number
 */
	// if we found this feb on this channel, put it into the list 
	febs.push_back(new feb(nHits, false, (febAddresses)a, 54)); 
	return;
}


feb *channels::MakeTrialFEB(int a, int nHits) 
{
/*! \fn 
 * This function creates a disposable "trial" FEB.
 * \param a the FEB number
 * \param nHits max Hits
 */
	febAddresses f = (febAddresses)a; //store the trial feb address
	feb *trialFeb = new feb(nHits, false, f, 54); //make up the trial feb
	trialFeb->SetFEBDefaultValues(); //set default values for convenience; be careful about *writing*!
	return trialFeb;
}


int channels::DecodeStatusMessage() 
{
/*! \fn 
 * This function decodes the status message for this channel.
 */
	bool error = false;

	StatusBits checkValue = MessageSent; 
	error = ( (channelStatus & checkValue)!=0 ); //bit should be HIGH
	try {
#if DEBUG_VERBOSE
		std::cout << "Message Sent? " << error << std::endl; 
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "Message was not sent." << std::endl;
		return -103; //if the message was not send, stop execution
	}
	
	checkValue = MessageReceived;
	error = ( (channelStatus & checkValue)!=0 ); //bit should be HIGH
	try {
#if DEBUG_VERBOSE
		std::cout << "Message Received? " << error << std::endl; 
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "Message was not received." << std::endl;
		return -104; 
	}

	checkValue = CRCError;
	error = ( (channelStatus & checkValue)==0 ); //bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "CRC Error? " << error << std::endl; 
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "CRC Error." << std::endl;
		exit(-105); 
	}
	
	checkValue = TimeoutError;
	error = ( (channelStatus & checkValue)==0 ); //bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "Timeout Error? " << error << std::endl;
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "Timeout Error." << std::endl;
		exit(-106); 
	}
	
	checkValue = FIFONotEmpty;
	error = ( (channelStatus & checkValue)==0 ); //Check FIFO buffer status; bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "FIFO Empty? " << error << std::endl;
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "FIFO Not Empty!" << std::endl;
		exit(-107); 
	}

	checkValue = FIFOFull;
	error = ( (channelStatus & checkValue)==0 ); //Check FIFO buffer status; bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "FIFO Full? " << error << std::endl;
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "FIFO Full!" << std::endl;
		exit(-108); 
	}

	checkValue = DPMFull;
	error = ( (channelStatus & checkValue)==0 ); //Check DPM status; bit should be LOW
	try  {
#if DEBUG_VERBOSE
		std::cout << "DPM Full? " << error << std::endl;
#endif
		if (!error) throw error;
	} catch (bool e) {
		std::cout << "DPM Full!" << std::endl;
		exit(-109); 
	}
	
	// PLL?, etc.?

	return 0;
}


void channels::SetBuffer(unsigned char *b) {
/*! \fn 
 * Puts data into the data buffer assigned to this channel.
 * \param b the data buffer
 */

#if DEBUG_VERBOSE
	std::cout << "Setting Buffer for Channel " << this->GetChannelNumber() << std::endl;
#endif
	buffer = new unsigned char [(int)dpmPointer];
	for (int i=0;i<(int)dpmPointer;i++) {
		buffer[i]=b[i];
#if DEBUG_VERBOSE
		std::cout << "  SetBuffer: " << buffer[i] << " i: " << i << std::endl;
#endif
	}
#if DEBUG_VERBOSE
	std::cout << "Done with SetBuffer... Returning..." << std::endl;
#endif
	return; 
}

#endif
