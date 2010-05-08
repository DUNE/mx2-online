// General Headers
#include <iostream>
#include <iterator>
#include <fstream>
#include <iomanip>
#include <cstdlib>

#include "newReadout.h"

log4cpp::Appender* theAppender;
log4cpp::Category& root    = log4cpp::Category::getRoot();
log4cpp::Category& newread = log4cpp::Category::getInstance(std::string("newread"));

// Controller and VME readout objects - used throughout.
controller *daqController;
acquire    *daqAcquire;

int main(int argc, char *argv[])
{
	if (argc < 2) {
		std::cout << "Usage : chginj -c <CROC Address> -h <CHANNEL Number> ";
		std::cout << "-f <Number of FEBs> ";
		std::cout << std::endl;
		exit(1);
	}

	// Note, indices are distinct from addresses!
	unsigned int crocCardAddress = 1 << 16;
	int crocID                   = 1;
	unsigned int crimCardAddress = 224 << 16;
	int crimID                   = 1;

	int controllerID = 0;
	int runningMode  = 0; // 0 == OneShot   
	int openGate     = 0; // Don't open a gate.

	// Process the command line argument set.
	int optind = 1;
	// Decode Arguments
	printf("\nArguments: ");
	while ((optind < argc) && (argv[optind][0]=='-')) {
		std::string sw = argv[optind];
		if (sw=="-croc") {
			optind++;
			crocCardAddress = (unsigned int)( atoi(argv[optind]) << 16 );
			printf(" CROC Address = %03d ", (crocCardAddress>>16));
		}
		else if (sw=="-crim") {
			optind++;
			crimCardAddress = (unsigned int)( atoi(argv[optind]) << 16 );
			printf(" CRIM Address = %03d ", (crimCardAddress>>16));
		}
		else if (sw=="-g") {
			openGate = 1;
		}
		else
			std::cout << "\nUnknown switch: " << argv[optind] << std::endl;
			optind++;
	}
	std::cout << std::endl;

	// Report the rest of the command line...
	if (optind < argc) {
		std::cout << "There were remaining arguments!  Are you sure you set the run up correctly?" << std::endl;
		std::cout << "  Remaining arguments = ";
		for (;optind<argc;optind++) std::cout << argv[optind] << " ";
		std::cout << std::endl;
	}

	theAppender = new log4cpp::FileAppender("default", "/work/data/logs/newReadout.txt");
	theAppender->setLayout(new log4cpp::BasicLayout());
	root.addAppender(theAppender);
	root.setPriority(log4cpp::Priority::ERROR);
	newread.setPriority(log4cpp::Priority::DEBUG);
	newread.info("--Starting newReadout script.--");

	// Controller & Acquire class init, contact the controller
	daqController = new controller(0x00, controllerID, theAppender);
	daqAcquire    = new acquire();
	try {
		int error = daqController->ContactController();
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error contacting the VME controller!" << std::endl;
		newread.fatalStream() << "Error contacting the VME controller!";
		exit(e);
	}

	// Very basic CRIM setup.
	daqController->MakeCrim(crimCardAddress,crimID);
	crim *theCrim = daqController->GetCrim(crimID);
	InitCRIM(theCrim, runningMode);

	// Very basic CROC setup.
	daqController->MakeCroc(crocCardAddress,(crocID));
	croc *theCroc = daqController->GetCroc(crocID);
	InitCROC(theCroc);

	std::list<readoutObject*> readoutObjects;
	for (int i=1; i<5; i++) {
		readoutObjects.push_back(new readoutObject(i));
	}
	InitializeReadoutObjects(&readoutObjects); 

	// Open a gate?
	if (openGate) {
		std::cout << "Opening a gate!" << std::endl;
		if (FastCommandOpenGate(theCroc)) {
			std::cout << "Couldn't open a gate!" << std::endl;
			newread.critStream() << "Couldn't open a gate!";
		}
	} else { 
		std::cout << "Not opening a gate." << std::endl;
	}

	std::cout << "Doing a readout..." << std::endl;
	// Do an "FPGA read"
	std::list<readoutObject*>::iterator rop = readoutObjects.begin();
	for (rop = readoutObjects.begin(); rop != readoutObjects.end(); rop++) {
		int febid = (*rop)->getFebID();
		std::cout << "feb id == " << febid << std::endl;	

		// Clear and reset all channels that have an FEB with id febid.
		std::list<channels*> *chanList = (*rop)->getChannelsList();
		std::list<channels*>::iterator chp;
		for (chp = chanList->begin(); chp != chanList->end(); chp++) {
			SendClearAndReset(*chp);
			if (ReadStatus(*chp, doNotCheckForMessRecvd)) return 1; // Error, stop!
			unsigned int clrstsAddr = (*chp)->GetClearStatusAddress();	
			printf("  Clear Status Address = 0x%X\n", clrstsAddr);
		}	

		// Now send FPGA read frame request to each channel with an FEB with id febid.
		for (chp = chanList->begin(); chp != chanList->end(); chp++) {


		}
	}	
	

	// Cleanup
	delete daqAcquire;
	delete daqController;
	for (std::list<readoutObject*>::iterator p=readoutObjects.begin(); p!=readoutObjects.end();p++) delete (*p);
	readoutObjects.clear();

	return 0;       
}                               


// Initialize list of readoutObjects
void InitializeReadoutObjects(std::list<readoutObject*> *objectList)
{
	std::list<readoutObject*>::iterator rop = objectList->begin();

	for (rop = objectList->begin(); rop != objectList->end(); rop++) {
		int febid = (*rop)->getFebID();
		std::cout << "feb id == " << febid << std::endl;	
		std::vector<croc*> *crocVector          = daqController->GetCrocVector();
		std::vector<croc*>::iterator crocp      = crocVector->begin();
		for (crocp = crocVector->begin(); crocp != crocVector->end(); crocp++) {
			int crocid = (*crocp)->GetCrocID();
			std::cout << " croc id == " << crocid << std::endl;
			std::list<channels*> *chanList = (*crocp)->GetChannelsList();
			std::list<channels*>::iterator chp;
			for (chp = chanList->begin(); chp != chanList->end(); chp++) {
				int chainid = (*chp)->GetChainNumber();
				bool addChain = false;
				std::cout << "  chain id == " << chainid << std::endl;
				std::list<feb*> *febList = (*chp)->GetFebList();
				std::list<feb*>::iterator fp;
				for (fp = febList->begin(); fp != febList->end(); fp++) {
					int innerfebid = (int)(*fp)->GetBoardNumber();
					std::cout << "   innr febid == " << innerfebid << std::endl;
					if (innerfebid == febid) { addChain = true; }
				}
				if (addChain) {
					std::cout << "     should add chain" << std::endl;
					(*rop)->addChannel(*chp);
				}
			}
		}
	}

	std::cout << "After assignment..." << std::endl;
	for (rop = objectList->begin(); rop != objectList->end(); rop++) {
		int febid = (*rop)->getFebID();
		std::cout << "feb id == " << febid << std::endl;	
		std::list<channels*> *chanList = (*rop)->getChannelsList();
		std::list<channels*>::iterator chp;
		for (chp = chanList->begin(); chp != chanList->end(); chp++) {
			unsigned int clrstsAddr = (*chp)->GetClearStatusAddress();	
			printf("  Clear Status Address = 0x%X\n", clrstsAddr);
		}	
	}
	 
}

// Initialize the CRIM. 
void InitCRIM(crim *theCrim, int runningMode)
{
	int index   = theCrim->GetCrimID();
	int address = ( theCrim->GetAddress() )>>16;
	newread.infoStream() << "Initializing CRIM with index " << index << " and address " << address;

	// Make sure that we can actually talk to the card.
	try {           
		int status = daqController->GetCrimStatus(index);
		if (status) throw status;
	} catch (int e)  {
		std::cout << "Unable to read the status register for CRIM with Address " <<
			((daqController->GetCrim(index)->GetCrimAddress())>>16) << std::endl;
		newread.fatalStream() << "Unable to read the status register for CRIM with Address " <<
			((daqController->GetCrim(index)->GetCrimAddress())>>16);
		exit(e); 
	}       

	unsigned short GateWidth    = 0x1;       // GetWidth must never be zero!
	unsigned short TCALBDelay   = 0x1;       // Delay should also be non-zero.
	unsigned short TCALBEnable  = 0x1;       // Enable pulse delay.
	crimTimingFrequencies Frequency  = ZeroFreq; // Used to set ONE frequency bit!  ZeroFreq ~no Frequency.
	crimTimingModes       TimingMode = MTM;      // Default to MTM.

	switch (runningMode) {
		// "OneShot" is the casual name for CRIM internal timing with software gates.
		case 0:
			std::cout << "Running Mode is OneShot." << std::endl;
			newread.infoStream() << "Running Mode is OneShot."; 
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = ZeroFreq;
			TimingMode   = crimInternal; 
			TCALBEnable  = 0x1;
			break;
		default:
			std::cout << "Invalid running mode in this script!" << std::endl;
			newread.fatalStream() << "Invalid running mode in this script!"; 
			exit(1);
	}

	daqController->GetCrim(index)->SetupTiming(TimingMode, Frequency);
	daqController->GetCrim(index)->SetupGateWidth(TCALBEnable, GateWidth);
	daqController->GetCrim(index)->SetupTCALBPulse(TCALBDelay);
	newread.info("  CRIM Timing Setup    = 0x%04X", daqController->GetCrim(index)->GetTimingSetup());
	newread.info("  CRIM GateWidth Setup = 0x%04X", daqController->GetCrim(index)->GetGateWidthSetup());
	newread.info("  CRIM TCALB Setup     = 0x%04X", daqController->GetCrim(index)->GetTCALBPulse());

	unsigned char crim_message[2];
	// Set GateWidth.
	try {   
		crim_message[0] = daqController->GetCrim(index)->GetGateWidthSetup() & 0xFF;
		crim_message[1] = (daqController->GetCrim(index)->GetGateWidthSetup()>>8) & 0xFF;
		int error = daqAcquire->WriteCycle(daqController->handle, 2, crim_message,
			daqController->GetCrim(index)->GetSGATEWidthRegister(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in InitCRIM!  Cannot write to the Gate Width register!" << std::endl;
		daqController->ReportError(e);
		newread.fatalStream() << "Error in InitCRIM!  Cannot write to the Gate Width register!";
		exit (e);    
	}       
	// Setup TCALB Delay.
	try {   
		crim_message[0] = daqController->GetCrim(index)->GetTCALBPulse() & 0xFF;
		crim_message[1] = (daqController->GetCrim(index)->GetTCALBPulse()>>8) & 0xFF;
		int error = daqAcquire->WriteCycle(daqController->handle, 2, crim_message,
			daqController->GetCrim(index)->GetTCALBRegister(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in InitCRIM!  Cannot write to the TCALB register!" << std::endl;
		daqController->ReportError(e);
		newread.fatalStream() << "Error in InitCRIM!  Cannot write to the TCALB register!";
		exit (e);
	}       
	// Setup Timing register.
	try {   
		crim_message[0] = daqController->GetCrim(index)->GetTimingSetup() & 0xFF;
		crim_message[1] = (daqController->GetCrim(index)->GetTimingSetup()>>8) & 0xFF;
		int error = daqAcquire->WriteCycle(daqController->handle, 2, crim_message,
			daqController->GetCrim(index)->GetTimingRegister(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in InitCRIM!  Cannot write to the Timing Setup register!" << std::endl;
		daqController->ReportError(e);
		newread.fatalStream() << "Error in InitCRIM!  Cannot write to the Timing Setup register!";
		exit (e);
	}       

	// IRQ Setup not really needed for this script.
	newread.infoStream() << "No IRQ setup.";

	// Done!
	std::cout << "Finished initializing CRIM at address " << address << std::endl;
	newread.infoStream() << "Finished initializing CRIM at address " << address;

// Exit InitCRIM.
}


// Initialize the CROC. 
void InitCROC(croc *theCroc)
{
	int crocID  = theCroc->GetCrocID();
	int address = ( theCroc->GetAddress() )>>16;
	newread.infoStream() << "Initializing CROC with index " << index << " and address " << address;

	int nChains         = 4; 
	int nFEBsPerChain[] = { 4, 0, 0, 0 };

	// Make sure that we can actually talk to the cards.
	try {   
		int status = daqController->GetCardStatus(crocID);
		if (status) throw status;
	} catch (int e)  {
		std::cout << "Error in InitCROC!  Cannot read the status register for CROC " << address << std::endl;
		newread.fatalStream() << "Error in InitCROC!  Cannot read the status register for CROC " << address;
		exit(e);
	}

	// Set the timing mode to EXTERNAL: clock mode, test pulse enable, test pulse delay
	unsigned char croc_message[2];
	croc_message[0] = (unsigned char)(daqController->GetCroc(crocID)->GetTimingRegister() & 0xFF);
	croc_message[1] = (unsigned char)( (daqController->GetCroc(crocID)->GetTimingRegister()>>8) & 0xFF);
	newread.info("  Timing Register Address  = 0x%X",daqController->GetCroc(crocID)->GetTimingAddress());
	newread.info("  Timing Register Message  = 0x%X",daqController->GetCroc(crocID)->GetTimingRegister());
	newread.info("  Timing Message (Sending) = 0x%02X%02X",croc_message[1],croc_message[0]);
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, 2, croc_message,
			daqController->GetCroc(crocID)->GetTimingAddress(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Unable to set the CROC timing mode for CROC " << address << std::endl;
		daqController->ReportError(e);
		newread.fatalStream() << "Unable to set the CROC timing mode for CROC " << address;
		exit (e);
	}
	
	newread.infoStream() << "Making FEB List:";
	for (int i = 0; i < nChains; i++) {
		bool avail = theCroc->GetChainAvailable(i);
		if (avail && nFEBsPerChain[i]) {
			try {   
				int error = MakeFEBList(theCroc->GetChain(i), nFEBsPerChain[i]);
				if (error) throw error;
			} catch (int e) { 
				std::cout << "Cannot locate all FEB's on CROC " << address << 
					" Chain " << i << std::endl;
				newread.fatalStream() << "Cannot locate all FEB's on CROC " << address <<
				" Chain " << i;
				exit(e);
			}
		}
	}

	// Done!
	std::cout << "Finished initialization for CROC " << address << std::endl;
	newread.infoStream() << "Finished initialization for CROC " << address;
// Exit InitCROC.
}


int MakeFEBList(channels *theChain, int nFEBs)
{               
/*
 *  Finds FEB's by sending a message to each 1 through nFEBs potential FEB's
 *  per channel.  Those channels which respond with "message received"
 *  for that FEB have and FEB of the corresponding number loaded into an 
 *  STL list containing objects of type feb.
 *
 *  Returns a status value (0 for success).
 */
	int crocAddress = ( theChain->GetClearStatusAddress() & 0xFFFF0000 )>>16;
	int success     = -1; // Failure!  0==Success.
	newread.infoStream() << "Entering MakeFEBList for CROC " <<
		crocAddress << " Chain " << theChain->GetChainNumber();
	newread.infoStream() << " Looking for " << nFEBs << " FEBs.";

	// Prep the Channel for readout.
	SendClearAndReset(theChain);
	if (ReadStatus(theChain, doNotCheckForMessRecvd)) return 1; // Error, stop!

	// This is a dynamic look-up of the FEB's on the channel.
	// Addresses numbers range from 1 to Max and we'll loop
	// over all of them and look for S2M message headers.
	for (int j = 1; j <= nFEBs; j++) {
		newread.infoStream() << "    Trying to make FEB " << j;
		// Make a temp FEB for the current address.
		feb *tmpFEB = theChain->MakeTrialFEB(j, numberOfHits, theAppender);

		// Build an outgoing message to test if an FEB of this address is available on this channel.
		tmpFEB->MakeMessage();

		// Send the message & delete the outgoingMessage.
		SendFrameData(tmpFEB, theChain);
		//SendFrameDataFIFOBLT(tmpFEB, theChain); //Some kind of odd behavior...
		tmpFEB->DeleteOutgoingMessage();

		// Check that the message was sent and recv'd.
		if (ReadStatus(theChain, checkForMessRecvd)) return 1; // Error, stop!

		// Read the DPM & delete the message shell.
		success = RecvFrameData(tmpFEB, theChain);
		delete [] tmpFEB->message;

		// If the FEB is available, load it into the channel's FEB list and initialize the TriPs. 
		if (!success) {
			newread.infoStream() << "FEB: " << tmpFEB->GetBoardNumber() << " is available on CROC "
				<< crocAddress << " Chain " << theChain->GetChainNumber();
			// Add the FEB to the list.  (Makes a new FEB.)
			theChain->SetFEBs(j, numberOfHits, theAppender); 
			theChain->SetHasFebs(true);
			// Clean up the memory.
			delete tmpFEB;
		} else {
			newread.critStream() << "FEB: " << tmpFEB->GetBoardNumber() << " is NOT available on CROC "
				<< crocAddress << " Chain "<< theChain->GetChainNumber();
			newread.critStream() << "CRITICAL! FEB: " << tmpFEB->GetBoardNumber() << " is NOT available on CROC "
				<< crocAddress << " Chain "<< theChain->GetChainNumber();
			// Clean up the memory.
			delete tmpFEB; 
			// Return an error, stop!
			return 1;
		}

		// Clear & Reset to prep for next FEB.
		SendClearAndReset(theChain);
		if (ReadStatus(theChain, doNotCheckForMessRecvd)) return 1; // Error, stop!
	}

	// Turn *list* of FEB's into a vector.  Obviously could have built a vector from the start,
	// but starting with a list for now because of all the other functions in the DAQ that 
	// expect to be able to access a list of FEB's.
	theChain->VectorizeFEBList();

	newread.infoStream() << "Returning from MakeFEBList for chain " << theChain->GetChainNumber();
	return 0;
}


// Send a Clear and Reset to a CROC FE Channel
void SendClearAndReset(channels *theChain)
{
	int crocAddress = ( theChain->GetClearStatusAddress() & 0xFFFF0000 )>>16;
	newread.debugStream() << "--> Entering SendClearAndReset for CROC " << crocAddress <<
		" Chain " << theChain->GetChainNumber();
	newread.debug("  Clear Status Address = 0x%X",theChain->GetClearStatusAddress());
	CVAddressModifier    AM  = daqController->GetAddressModifier();
	CVDataWidth          DW  = daqController->GetDataWidth();
	unsigned char message[2] = {0x0A, 0x0A}; // 0202 + 0808 for clear status AND reset.

	// Clear the status & reset the pointer.
	try {
		int success = daqAcquire->WriteCycle(daqController->handle, 2, message,
			theChain->GetClearStatusAddress(), AM, DW);
		if (success) throw success;
	} catch (int e) {
		std::cout << "VME Error in SendClearAndReset!  Cannot write to the status register!" << std::endl;
		daqController->ReportError(e);
		newread.critStream() << "VME Error in SendClearAndReset!  Cannot write to the status register!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		exit(e);
	}	
	newread.debugStream() << "Executed SendClearAndReset for CROC " << crocAddress <<
		" Chain " << theChain->GetChainNumber();
}


// Read the status register on a CROC FE Channel
int ReadStatus(channels *theChain, bool receiveCheck)
{
	int crocAddress = ( theChain->GetClearStatusAddress() & 0xFFFF0000 )>>16;
	newread.debugStream() << "--> Entering ReadStatus for CROC " << crocAddress << 
		" Chain " << (theChain->GetChainNumber());
	newread.debug("  Status Address = 0x%X",theChain->GetStatusAddress());

	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth DW       = daqController->GetDataWidth();

	unsigned short MessageReceivedCheck = 0xFFFF;
	if (receiveCheck) MessageReceivedCheck = MessageReceived;
	unsigned char statusBytes[] = {0x0,0x0};
	unsigned short status;

	do {
		try {
			int error = daqAcquire->ReadCycle(daqController->handle, statusBytes,
				theChain->GetStatusAddress(), AM, DW);
			if (error) throw error;
		} catch (int e) {
			std::cout << "VME Error in ReadStatus while reading the status register!"
				<< std::endl;
			daqController->ReportError(e);
			newread.critStream() << "VME Error in ReadStatus while reading the status register!";
			newread.critStream() << "  Error on CROC " << crocAddress <<
				" Chain " << theChain->GetChainNumber();
			return e;
		}
		status = (unsigned short)( statusBytes[0] | statusBytes[1]<<0x08 );
		theChain->SetChannelStatus(status);
		newread.debug("  Read Status - Chain %d status = 0x%04X",
			theChain->GetChainNumber(),status);
	} while ( !(status & MessageReceivedCheck) && !(status & CRCError) && !(status & TimeoutError)
		&& (status & RFPresent) && (status & SerializerSynch) && (status & DeserializerLock)
		&& (status & PLLLocked) );

	// Check for errors & handle them.
	if ( (status & CRCError) ) {
		std::cout << "CRC Error!\n";
		newread.critStream() << "CRC Error in ReadStatus!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-10);
	}
	if ( (status & TimeoutError) ) {
		std::cout << "Timeout Error!\n";
		newread.critStream() << "Timeout Error in acquire_data::SendMessage!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-11);
	}
	if ( (status & FIFONotEmpty) ) {
		std::cout << "FIFO Not Empty!\n";
		newread.critStream() << "FIFO Not Empty Error in acquire_data::SendMessage!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
	}
	if ( (status & FIFOFull) ) {
		std::cout << "FIFO Full!\n";
		newread.critStream() << "FIFO Full Error in acquire_data::SendMessage!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
	}
	if ( (status & DPMFull) ) {
		std::cout << "DPM Full!\n";
		newread.critStream() << "DPM Full Error in acquire_data::SendMessage!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
	}
	if ( !(status & RFPresent) ) {
		std::cout << "No RF Present!\n";
		newread.critStream() << "No RF Error in acquire_data::SendMessage!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-12);
	}
	if ( !(status & SerializerSynch) ) {
		std::cout << "No SerializerSynch!\n";
		newread.critStream() << "No SerializerSynch Error in acquire_data::SendMessage!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-13);
	}
	if ( !(status & DeserializerLock) ) {
		std::cout << "No DeserializerLock!\n";
		newread.critStream() << "DeserializerLock Error in acquire_data::SendMessage!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-14);
	}
	if ( !(status & PLLLocked) ) {
		std::cout << "No PLLLock!\n";
		newread.critStream() << "PLLLock Error in acquire_data::SendMessage!";
		newread.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-15);
	}

	newread.debugStream() << "Executed ReadStatus for CROC " << crocAddress <<
		" Chain " << theChain->GetChainNumber();
	return 0;
}


// send messages to a generic device using normal write cycle
// -> write the outgoing message to the CROC FIFO, send the message
template <class X> void SendFrameData(X *device, channels *theChannel)
{
	newread.debugStream() << "   -->Entering SendFrameData.";
	CVAddressModifier AM = cvA24_U_DATA;  // *Default* Controller Address Modifier
	CVDataWidth DW       = cvD16;         // *Default* Controller Data Width
	CVDataWidth DWS      = cvD16_swapped; // *Always* CROC DataWidthSwapped
	unsigned char send_message[2] ={0x01, 0x01}; 

	// Write the message to the channel FIFO.
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, device->GetOutgoingMessageLength(),
			device->GetOutgoingMessage(), theChannel->GetFIFOAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error in SendFrameData while writing to the FIFO!" << std::endl;
		daqController->ReportError(e);
		newread.fatalStream() << "Error in SendFrameData while writing to the FIFO!";
		newread.fatalStream() << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		// Hard exit used for thread "friendliness" later...
		exit(e);
	}
	// Send the message.
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, 2, send_message,
			theChannel->GetSendMessageAddress(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error in SendFrameData while writing to the SendMessage address!" << std::endl;
		daqController->ReportError(e);
		newread.critStream() << "Error in SendFrameData while writing to the SendMessage address!";
		newread.critStream() << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
		" Chain " << theChannel->GetChainNumber();
		// Hard exit used for thread "friendliness" later...
		exit(e);
	}
	newread.debugStream() << "   Finished SendFrameData!";
}

// send messages to a generic device using FIFO BLT write cycle
// -> write the outgoing message to the CROC FIFO, send the message (for FPGA's only)
template <class X> void SendFrameDataFIFOBLT(X *device, channels *theChannel)
{
	newread.debugStream() << "   -->Entering SendFrameDataFIFOBLT.";
	CVAddressModifier AM = cvA24_U_DATA;  // *Default* Controller Address Modifier
	CVDataWidth DW       = cvD16;         // *Default* Controller Data Width
	CVDataWidth DWS      = cvD16_swapped; // *Always* CROC DataWidthSwapped
	unsigned char send_message[2] ={0x01, 0x01}; 

	// Write the message to the channel FIFO using BLT.
	try {
		int error = daqAcquire->WriteFIFOBLT(daqController->handle, device->GetOutgoingMessageLength(),
			device->GetOutgoingMessage(), theChannel->GetFIFOAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error in SendFrameDataFIFOBLT while writing to the FIFO!" << std::endl;
		daqController->ReportError(e);
		newread.fatalStream() << "Error in SendFrameDataFIFOBLT while writing to the FIFO!";
		newread.fatalStream() << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		// Hard exit used for thread "friendliness" later...
		exit(e);
	}
	// Send the message.
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, 2, send_message,
			theChannel->GetSendMessageAddress(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error in SendFrameDataFIFOBLT while writing to the SendMessage address!" << std::endl;
		daqController->ReportError(e);
		newread.critStream() << "Error in SendFrameDataFIFOBLT while writing to the SendMessage address!";
		newread.critStream() << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
		" Chain " << theChannel->GetChainNumber();
		// Hard exit used for thread "friendliness" later...
		exit(e);
	}
	newread.debugStream() << "   Finished SendFrameDataFIFOBLT!";

}

// recv messages from a generic device
// -> read DPM pointer, read BLT
template <class X> int RecvFrameData(X *device, channels *theChannel)
{
	newread.debugStream() << "   -->Entering RecvFrameData.";
	CVAddressModifier AM     = cvA24_U_DATA;  // *Default* Controller Address Modifier
	CVAddressModifier AM_BLT = cvA24_U_BLT;   // *Always* Channel Address Modifier
	CVDataWidth DWS          = cvD16_swapped; // *Always* CROC DataWidthSwapped
	unsigned short dpmPointer;
	unsigned char status[] = {0x0,0x0};

	try {
		int error = daqAcquire->ReadCycle(daqController->handle, status,
			theChannel->GetDPMPointerAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in RecvFrameData!  Cannot read the status register!" << std::endl;
		daqController->ReportError(e);
		newread.critStream() << "Error in RecvFrameData!  Cannot read the status register!";
		return e;
	}
	dpmPointer = (unsigned short) (status[0] | status[1]<<0x08);
	newread.debugStream() << "    RecvFrameData DPM Pointer: " << dpmPointer;
	device->SetIncomingMessageLength(dpmPointer-2);
	// We must read an even number of bytes.
	if (dpmPointer%2) {
		device->message = new unsigned char [dpmPointer+1];
	} else {
		device->message = new unsigned char [dpmPointer];
	}

	try {
		int error = daqAcquire->ReadBLT(daqController->handle, device->message, dpmPointer,
			theChannel->GetDPMAddress(), AM_BLT, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in RecvFrameData!  Cannot ReadBLT!" << std::endl;
		daqController->ReportError(e);
		newread.critStream() << "Error in RecvFrameData!  Cannot ReadBLT!";
		newread.critStream() << "  Error on CROC " << 
			((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		return e;
	}

	// Check Device Header for error flags (S2M, etc.)
	bool success = device->CheckForErrors();
	if (success) {
		return success; // There were errors.
	}
	// TODO - DecodeRegVals does some useful error checking (message length), but is inefficient.
	// TODO - Split out the useful part and just call it... (make it part of CheckForErrors?  Probably no...)
	// Also TODO - figure out the right argument to pass this function... for some reason, if we did a FIFO 
	// write beforehand, we get back a different DPM pointer than if we had done a regular write...
	device->DecodeRegisterValues(dpmPointer-2);
	//device->DecodeRegisterValues(dpmPointer);

	newread.debugStream() << "   Finished RecvFrameData!  Returning " << success;
	return ((int)success);
}


// Open a gate
int FastCommandOpenGate(croc *theCroc)
{
	unsigned char openGateCommand[] = {0xB1};
	int ml = sizeof(openGateCommand)/sizeof(unsigned char);

	try {
		int error = daqAcquire->WriteCycle(daqController->handle, ml, openGateCommand,
			theCroc->GetFastCommandAddress(),
			daqController->GetAddressModifier(), daqController->GetDataWidth());
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::WriteCROCFastCommand for CROC " <<
			(theCroc->GetCrocAddress()>>16) << std::endl;
		daqController->ReportError(e);
		newread.critStream() << "Error in acquire_data::WriteCROCFastCommand for CROC " <<
			(theCroc->GetCrocAddress()>>16);
		return e;
	}

	return 0;
}

