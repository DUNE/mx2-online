// General Headers
#include <iostream>
#include <iterator>
#include <fstream>
#include <iomanip>
#include <cstdlib>

#include "newReadout.h"

log4cpp::Appender* myAppender;
log4cpp::Category& root    = log4cpp::Category::getRoot();
log4cpp::Category& newread = log4cpp::Category::getInstance(std::string("newread"));

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

	myAppender = new log4cpp::FileAppender("default", "/work/data/logs/newReadout.txt");
	myAppender->setLayout(new log4cpp::BasicLayout());
	root.addAppender(myAppender);
	root.setPriority(log4cpp::Priority::ERROR);
	newread.setPriority(log4cpp::Priority::DEBUG);
	newread.info("--Starting newReadout script.--");

	// Controller & Acquire class init, contact the controller
	controller *daqController = new controller(0x00, controllerID, myAppender);
	acquire *daqAcquire = new acquire();
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
	crim *myCrim = daqController->GetCrim(crimID);
	InitCRIM(daqController, daqAcquire, myCrim, runningMode);

	// Very basic CROC setup.
	daqController->MakeCroc(crocCardAddress,(crocID));
	croc *myCroc = daqController->GetCroc(crocID);
	InitCROC(daqController, daqAcquire, myCroc);

	// Try a quick and dirty test.
	int rerror;
	for (int i=0; i<4; i++) {
		SendClearAndReset( daqController, daqAcquire, myCroc->GetChain(i) );
	}
	for (int i=0; i<4; i++) {
		// Should not see mess rec'd after clear.	
		rerror = ReadStatus( daqController, daqAcquire, myCroc->GetChain(i), false ); 
		std::cout << "ReadStatus return value for chain " << i << " = " << rerror << std::endl;
		newread.debugStream() << "ReadStatus return value for chain " << i << " = " << rerror;
	}

	return 0;       
}                               


// Initialize the CRIM. 
void InitCRIM(controller *daqController, acquire *daqAcquire, crim *myCrim, int runningMode)
{
	int index   = myCrim->GetCrimID();
	int address = ( myCrim->GetAddress() )>>16;
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
void InitCROC(controller *daqController, acquire *daqAcquire, croc *myCroc)
{
	int crocNo   = myCroc->GetCrocID();
	int address = ( myCroc->GetAddress() )>>16;
	newread.infoStream() << "Initializing CROC with index " << index << " and address " << address;

	int nChains         = 4; 
	int nFEBsPerChain[] = { 4, 0, 0, 0 };

	// Make sure that we can actually talk to the cards.
	try {   
		int status = daqController->GetCardStatus(crocNo);
		if (status) throw status;
	} catch (int e)  {
		std::cout << "Error in InitCROC!  Cannot read the status register for CROC " <<
			(address>>16) << std::endl;
		newread.fatalStream() << "Error in InitCROC!  Cannot read the status register for CROC " <<
			(address>>16);
		exit(e);
	}

	// Set the timing mode to EXTERNAL: clock mode, test pulse enable, test pulse delay
	unsigned char croc_message[2];
	croc_message[0] = (unsigned char)(daqController->GetCroc(crocNo)->GetTimingRegister() & 0xFF);
	croc_message[1] = (unsigned char)( (daqController->GetCroc(crocNo)->GetTimingRegister()>>8) & 0xFF);
	newread.info("  Timing Register Address  = 0x%X",daqController->GetCroc(crocNo)->GetTimingAddress());
	newread.info("  Timing Register Message  = 0x%X",daqController->GetCroc(crocNo)->GetTimingRegister());
	newread.info("  Timing Message (Sending) = 0x%02X%02X",croc_message[1],croc_message[0]);
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, 2, croc_message,
			daqController->GetCroc(crocNo)->GetTimingAddress(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Unable to set the CROC timing mode!" << std::endl;
		daqController->ReportError(e);
		newread.fatalStream() << "Unable to set the CROC timing mode!";
		exit (e);
	}
	
	// Build the FEB list for each channel.
	newread.infoStream() << "Building FEB List:";
	for (int i = 0; i < nChains; i++) {
		// Now set up the channels and FEB's.
		bool avail = myCroc->GetChainAvailable(i);
		if (avail && nFEBsPerChain[i]) {
			try {   
				int error = BuildFEBList(daqController, daqAcquire, myCroc, i, nFEBsPerChain[i]);
				if (error) throw error;
			} catch (int e) { 
				std::cout << "Cannot locate all FEB's on CROC " <<
					(daqController->GetCroc(crocNo)->GetCrocAddress()>>16) <<
					" Chain " << i << std::endl;
				newread.fatalStream() << "Cannot locate all FEB's on CROC " << 
					(daqController->GetCroc(crocNo)->GetCrocAddress()>>16) <<
				" Chain " << i;
				exit(e);
			}
		}
	}

	// Done!
	std::cout << "Finished initialization for CROC " <<
		(daqController->GetCroc(crocNo)->GetCrocAddress()>>16) << std::endl;
	newread.infoStream() << "Finished initialization for CROC " <<
		(daqController->GetCroc(crocNo)->GetCrocAddress()>>16);

// Exit InitCROC.
}


int BuildFEBList(controller *daqController, acquire *daqAcquire, croc *myCroc, int i, int nFEBs)
{               
/*
 *  Finds FEB's by sending a message to each 1 through nFEBs potential FEB's
 *  per channel.  Those channels which respond with "message received"
 *  for that FEB have and FEB of the corresponding number loaded into an 
 *  STL list containing objects of type feb.
 *
 *  Returns a status value (0 for success).
 */
	newread.infoStream() << "Entering BuildFEBList for CROC " <<
		(myCroc->GetCrocAddress()>>16) << " Chain " << i;
	newread.infoStream() << " Looking for " << nFEBs << " FEBs.";
	// Exract the CROC object and Channel object from the controller 
	// and assign them to a tmp of each type for ease of use.
	//channels *tmpChan = myCroc->GetChain(i);

	// This is a dynamic look-up of the FEB's on the channel.
	// Addresses numbers range from 1 to Max and we'll loop
	// over all of them and look for S2M message headers.
/*
	for (int j = 1; j <= nFEBs; j++) {
		newread.infoStream() << "    Trying to make FEB " << j << " on chain " << i;
		// Make a "trial" FEB for the current address.
		feb *tmpFEB = tmpChan->MakeTrialFEB(j, numberOfHits, acqAppender);

		// Build an outgoing message to test if an FEB of this address is available on this channel.
		tmpFEB->MakeMessage();
		// Send the message & delete the outgoingMessage.
		int success = SendMessage(tmpFEB, tmpCroc, tmpChan, true);
		tmpFEB->DeleteOutgoingMessage();


		// Read the DPM & delete the message shell.
		success = ReceiveMessage(tmpFEB, tmpCroc, tmpChan);
		delete [] tmpFEB->message;


		// If the FEB is available, load it into the channel's FEB list and initialize the TriPs. 
		if (!success) {
			newread.infoStream() << "FEB: " << tmpFEB->GetBoardNumber() << " is available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " 
				<< tmpChan->GetChainNumber() << " with init. level " << tmpFEB->GetInit();
			// Add the FEB to the list.
			tmpChan->SetFEBs(j, numberOfHits, acqAppender);
			// Set the FEB available flag.
			tmpChan->SetHasFebs(true);
			// Clean up the memory.
			delete tmpFEB;
		} else {
			newread.critStream() << "FEB: " << tmpFEB->GetBoardNumber() << " is NOT available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain "
				<< tmpChan->GetChainNumber();
			std::cout << "\nCRITICAL!  FEB: " << tmpFEB->GetBoardNumber() << " is NOT available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain "
				<< tmpChan->GetChainNumber() << "\n" << std::endl;
			// Clean up the memory.
			delete tmpFEB; 
			// Return an error, stop!
			return 1;
		}
	}
*/

	std::cout << "Returning from BuildFEBList for chain " << i << std::endl;
	newread.infoStream() << "Returning from BuildFEBList for chain " << i;
	return 0;
}


// Send a Clear and Reset to a CROC FE Channel
void SendClearAndReset(controller *daqController, acquire *daqAcquire,  channels *theChain)
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
int ReadStatus(controller *daqController, acquire *daqAcquire, channels *theChain, bool receiveCheck)
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

	return 0;
}

