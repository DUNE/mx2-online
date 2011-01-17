#ifndef channels_cpp
#define channels_cpp

#include "channels.h"
#include "exit_codes.h"

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

	channelStatus = 0;     // the channel starts out with no status information kept
	has_febs      = false; // and no feb's loaded
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
		exit(EXIT_CROC_DMPFULL_ERROR); 
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


unsigned short channels::GetPreviewHV(int febid)
{
/*! \fn Parse the preview hit data to get the HV on FEB febid. 
 */
#if DEBUG_CHPREVIEW
	std::cout << "GetPreviewHV: febid = " << febid << std::endl;
#endif
	int ml    = sizeof(buffer)/sizeof(unsigned char);
#if DEBUG_CHPREVIEW
	std::cout << "  preview hit ml = " << ml << std::endl;
#endif
	if (ml <= 0) return 0; 
#if DEBUG_CHPREVIEW
	for (int i=0; i<ml; i++) { printf("%02X ",buffer[i]); }
	std::cout << std::endl;
#endif
	int nfebs = ml/6;
#if DEBUG_CHPREVIEW
	std::cout << "  preview hit nfebs = " << nfebs << std::endl;
#endif
	if (nfebs == 0) return 0;
	for (int i=0; i<nfebs; i++) {
		int index   = i * 6;
#if DEBUG_CHPREVIEW
		std::cout << "  index = " << index << std::endl;
#endif
		int febaddr = buffer[index + 2] & 0x0F;
#if DEBUG_CHPREVIEW
		printf("    %02X\n",buffer[index+2]);
		printf("    %02X\n",buffer[index+3]);
		std::cout << "  febaddr = " << febaddr << std::endl;
#endif
		if (febaddr == febid) {
#if DEBUG_CHPREVIEW
			std::cout << "    HV = " << 
				(unsigned short)( buffer[index+4] + buffer[index+5]<<8 ) << std::endl;
#endif
			return (unsigned short)( buffer[index+4] + buffer[index+5]<<8 ); 
		}
	}
	return (unsigned short)0;
}


int channels::GetPreviewHits(int febid)
{
/*! \fn Parse the preview hit data to get the max hits on FEB febid. 
 */
#if DEBUG_CHPREVIEW
	std::cout << "GetPreviewHits: febid = " << febid << std::endl;
#endif
	//int ml    = dpmPointer-2; // dangerous to rely on this being set for some reason? 
	int ml    = sizeof(buffer)/sizeof(unsigned char) - 2;
#if DEBUG_CHPREVIEW
	std::cout << "  preview hit ml = " << ml << std::endl;
#endif
	if (ml <= 0) return -1;
#if DEBUG_CHPREVIEW
	for (int i=0; i<ml; i++) { printf("%02X ",buffer[i]); }
	std::cout << std::endl;
#endif
	int nfebs = ml/6;
#if DEBUG_CHPREVIEW
	std::cout << "  preview hit nfebs = " << nfebs << std::endl;
#endif
	if (nfebs == 0) return -1;
	for (int i=0; i<nfebs; i++) {
		int index   = i * 6;
#if DEBUG_CHPREVIEW
		std::cout << "  index = " << index << std::endl;
#endif
		int febaddr = buffer[index + 2] & 0x0F;
#if DEBUG_CHPREVIEW
		printf("    %02X\n",buffer[index+2]);
		printf("    %02X\n",buffer[index+3]);
		std::cout << "  febaddr = " << febaddr << std::endl;
#endif
		if (febaddr == febid) {
			unsigned char hit01 = buffer[index + 3] & 0x0F;
#if DEBUG_CHPREVIEW
			std::cout << "    preview hit01 = " << (int)hit01 << std::endl;
#endif
			unsigned char hit23 = (buffer[index + 3] & 0xF0)>>4;
#if DEBUG_CHPREVIEW
			std::cout << "    preview hit23 = " << (int)hit23 << std::endl;
#endif
			return (int)( hit01>=hit23 ? hit01 : hit23 );	
		}
	}
	return -1;
}


int channels::CheckHeaderErrors(int dataLength)
{                  
/*! \fn channels::CheckHeaderErrors(int dataLength)
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
