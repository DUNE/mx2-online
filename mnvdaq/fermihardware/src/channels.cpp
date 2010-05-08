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

// TODO - Be careful about all the "54's" showing up for the number of registers in an FPGA frame.

channels::channels(unsigned int a, int b) 
{
/*! \fn 
 * constructor takes the following arguments:
 * \param a:  The channel base address 
 * \param b:  The channel number
 */
	channelBaseAddress = a; //the address for the croc which contains this channel
	channelNumber = b; //the channel number (0-3 here, 1-4 is stenciled on the cards themselves)
	chainNumber   = b; //the chain number 0-3, now and forever.
	channelDirectAddress = channelBaseAddress + 0x4000 * (unsigned int)(chainNumber);
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
}


void channels::SetFEBs(int a, int nHits, log4cpp::Appender* appender) 
{
/*! \fn
 * This function loads FEB's belonging to this channel into a vector of febs once
 * the feb has been found
 * \param a the FEB number
 * \param nHits max Hits
 * \param appender log4cpp Appender
 */
	// if we found this feb on this channel, put it into the list 
	febs.push_back(new feb(nHits, false, (febAddresses)a, 54, appender)); 
	return;
}


feb *channels::MakeTrialFEB(int a, int nHits, log4cpp::Appender* appender) 
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


int channels::DecodeStatusMessage() 
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
		exit(-105); 
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
		exit(-106); 
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
		exit(-107); 
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
		exit(-108); 
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
		exit(-109); 
	}
	
	// PLL?, etc.?

	return 0;
}


void channels::SetBuffer(unsigned char *b) 
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


void channels::VectorizeFEBList() 
{
/*! \fn
 * Takes list of febs created during initialization and turns them into a vector.
 * TODO - Think about sorting, etc. to be sure indexing is right first (it is, but this is still "sloppy").
 * Also TODO - Think about a copy instead of pushing a pointer to an existing object.
 */
	if (has_febs) {
		std::list<feb*>::iterator fp;
		for (fp = febs.begin(); fp != febs.end(); fp++) {
			febsVector.push_back(*fp);
		}
	}

}
#endif
