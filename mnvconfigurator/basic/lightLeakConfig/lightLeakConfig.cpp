// General Headers
#include <iostream>
#include <iterator>
#include <fstream>
#include <iomanip>
#include <cstdlib>


// Minerva Headers (log4cpp Headers contained within). 
#include "acquire.h"
#include "MinervaDAQtypes.h"
#include "controller.h"
#include "feb.h"
#include "adctdc.h"

using namespace std;

#define DEBUGLEVEL 10
#define CLEARANDRESETLEVEL 50
#define FPGAREADLEVEL 50
#define FPGAWRITELEVEL 50
#define TRIPTREADLEVEL 50
#define TRIPTWRITELEVEL 50

// Implement this interface for your own strategies for printing log statements.
log4cpp::Appender* myAppender;
// Return the root of the Category hierarchy?...
log4cpp::Category& root     = log4cpp::Category::getRoot();
// Further category hierarchy.
log4cpp::Category& llConfig = log4cpp::Category::getInstance(std::string("llConfig"));

const int NRegisters = 54; // Using v80+ firmware on all FEBs now.
const int maxHits    = 6;  // maxHits should not be changed independent of the DAQ!

const int tripRegIBP        =  60;
const int tripRegIBBNFOLL   = 120;
const int tripRegIFF        =   0;
const int tripRegIBPIFF1REF = 160;
const int tripRegIBOPAMP    =  40;
const int tripRegIB_T       =   0;
const int tripRegIFFP2      =   0;
const int tripRegIBCOMP     =  20;
const int tripRegVREF       = 165;
const int tripRegVTH        =   0; // Turn discr. off for light leak checkout.
// const int tripRegPIPEDEL    =  2*maxHits - 1; 
const int tripRegGAIN       =  11;
const int tripRegIRSEL      =   3;
const int tripRegIWSEL      =   3;

const CVRegisters ControllerStatusAddress = cvStatusReg;
const CVDataWidth DW                      = cvD16;
const CVDataWidth DWS                     = cvD16_swapped;
const CVAddressModifier AM                = cvA24_U_DATA;
const CVAddressModifier BLT_AM            = cvA24_U_BLT;
unsigned char sendMessage[]               = {0x01,0x01}; //Send to CROC to send FIFO message to FEB
unsigned char crocChanResetValue[]        = {0x02,0x02}; //Good for clear status reg., reset reg.
unsigned char crocDPMResetValue[]         = {0x08,0x08};
unsigned char crocResetAndTestPulseMask[] = {0x0F,0x0F}; // enable reset (0F) and test pulse (2nd 0F) 

// Clear status && reset DPM pointer for all four channels on the CROC.
int CROCClearStatusAndResetPointer(controller *myController, acquire *myAcquire, croc *myCroc);
// Pure Readback of FPGA's - not needed or used here...
int FEBFPGARead(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID);
// Basic Setup of FPGA's
int FEBFPGAWrite(controller *myController, acquire *myAcquire, croc *myCroc, 
 	unsigned int crocChannel, febAddresses boardID, int HVTarget, int HVEnableFlag);
// Read all 6 TRiP's
int FEBTRiPTRead(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID);
// Write to all 6 TRiP's
int FEBTRiPTWrite(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID);
// Open a gate - not used, but here anyway...
int FastCommandOpenGate(controller *myController, acquire *myAcquire, croc *myCroc);


int main(int argc, char *argv[]) 
{
	if (argc < 2) {
		cout << "Usage : lightLeakConfig -c <CROC Address> -h <CHANNEL Number> -f <Number of FEBs> ";
		cout << "-v <HV Target> -e <enable 1 or 0>\n";
		exit(0);
	}
	
	// Note, indices are distinct from addresses!
	unsigned int crocCardAddress = 1 << 16;
	unsigned int crocChannel     = 1;	
	int crocID                   = 1;
	int nFEBs                    = 4; // USE SEQUENTIAL ADDRESSING!!!
	int HVTarget                 = 32000;
	int HVEnableFlag             = 0; // disable by default
	
	int error;		
	int controllerID = 0;
	bool doTriPReadBackCheck = false;
#if DEBUGLEVEL > TRIPTREADLEVEL
	doTriPReadBackCheck = true;
#endif

	// Process the command line argument set.
	int optind = 1;
	// Decode Arguments
	cout << "\n\nArguments: " << endl;
	while ((optind < argc) && (argv[optind][0]=='-')) {
		string sw = argv[optind];
		if (sw=="-c") {
			optind++;
			crocCardAddress = (unsigned int)( atoi(argv[optind]) << 16 );
			cout << "\tCROC Address   = " << (crocCardAddress>>16) << endl;
        	}
		else if (sw=="-h") {
			optind++;
			crocChannel = (unsigned int)( atoi(argv[optind]) );
			cout << "\tCROC Channel   = " << crocChannel << endl;
        	}
		else if (sw=="-f") {
			optind++;
			nFEBs = atoi(argv[optind]);
			cout << "\tNumber of FEBs = " << nFEBs << endl;
        	}
		else if (sw=="-v") {
			optind++;
			HVTarget = atoi(argv[optind]);
			cout << "\tTarget HV      = " << HVTarget << endl;
        	}
		else if (sw=="-e") {
			optind++;
			HVEnableFlag = atoi(argv[optind]);
			cout << "\tHV Enable Flag = " << HVEnableFlag << endl;
		}
		else
			cout << "Unknown switch: " << argv[optind] << endl;
		optind++;
	}
	cout << endl;
	// Report the rest of the command line...
	if (optind < argc) {
		cout << "There were remaining arguments!  Are you sure you set the run up correctly?" << endl;
		cout << "  Remaining arguments = ";
		for (;optind<argc;optind++) cout << argv[optind];
		cout << endl;
	}

	myAppender = new log4cpp::FileAppender("default", "/work/data/logs/config.txt");
	myAppender->setLayout(new log4cpp::BasicLayout());
	root.addAppender(myAppender);
	root.setPriority(log4cpp::Priority::ERROR); 	
	llConfig.setPriority(log4cpp::Priority::INFO);

	llConfig.info("--Starting lightLeakConfig script.--");	

	// Controller & Acquire class init, contact the controller
	controller *myController = new controller(0x00, controllerID, myAppender);	
	acquire *myAcquire = new acquire(); 				
	if ((error=myController->ContactController())!=0) { 
		cout<<"Controller contact error: "<<error<<endl; exit(error); // Exit due to no controller!
	}
	cout<<"Controller & Acquire Initialized..."<<endl;
	cout<<endl;

	//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	std::list<febAddresses> febAddr;
	for (int nboard = 1; nboard <= nFEBs; nboard++) {
		febAddr.push_back( (febAddresses)nboard );
	}
  	
	std::cout << "Making CROC with index == " << crocID << " && address == " 
		<< (crocCardAddress>>16) << std::endl;
	myController->MakeCroc(crocCardAddress,(crocID));
	try {
		error = myController->GetCrocStatus(crocID); 
		if (error) throw error;
	} catch (int e)  {
		std::cout << "Unable to read the status register for CROC " << 
			((myController->GetCroc(crocID)->GetCrocAddress())>>16) << std::endl;
		exit(-3);
	} 	
	croc *myCroc = myController->GetCroc(crocID);    
	//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	// Setup FPGA's, then setup TriP's
	{
		for (std::list<febAddresses>::iterator p = febAddr.begin();
			p != febAddr.end();
			p++) {
				// Clear Status & Reset
				{
					error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
					if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
				}
				// Setup FPGA's
				{
					error = FEBFPGAWrite(myController, myAcquire, myCroc, crocChannel, *p, HVTarget, 
						HVEnableFlag);
					if (error!=0) { cout<<"Error in FEB FPGA Write!\n"; exit(error); }	
				}
				// Setup TriPT's
				{
					error = FEBTRiPTWrite(myController, myAcquire, myCroc, crocChannel, *p);
					if (error!=0) { cout<<"Error in FEB TRiPT Write!\n"; exit(error); }	
				}
				if (doTriPReadBackCheck) {
					error = FEBTRiPTRead(myController, myAcquire, myCroc, crocChannel, *p);
					if (error!=0) { cout<<"Error in FEB TRiPT Read!\n"; exit(error); }						
				}
			}		  
	}


	delete myAcquire;
	delete myController; //also deletes associated crocs && crims;
	
	return 0;
}


// Clear & Reset all four channels on a CROC
int CROCClearStatusAndResetPointer(controller *myController, acquire *myAcquire, croc *myCroc)
{
	unsigned int myAddress;
	int error;
	bool deserializer = false;
	bool synch        = false;
	
	for (unsigned int i = 0; i<4; i++) { // loop over *chains*
		unsigned char myData[] = {0x0,0x0};
		// Reset DPM.
		myAddress = myCroc->GetAddress() + (unsigned int)crocClearStatus +i*0x4000;
		error = myAcquire->WriteCycle(myController->GetHandle(),2,crocDPMResetValue,myAddress,AM,DW);
#if DEBUGLEVEL > CLEARANDRESETLEVEL
		cout << "DPMReset Error = " << error << endl;
#endif
		// Clear Status.
		error = myAcquire->WriteCycle(myController->GetHandle(),2,crocChanResetValue,myAddress,AM,DW);
#if DEBUGLEVEL > CLEARANDRESETLEVEL
		cout << "Clear Status Error = " << error << endl;		
#endif
		// Read Status
		myAddress = myCroc->GetAddress() + (unsigned int)crocStatus + i*0x4000;
		error = myAcquire->ReadCycle(myController->GetHandle(),myData,myAddress,AM,DW);
#if DEBUGLEVEL > CLEARANDRESETLEVEL
		printf("Address  = 0x%X\n", myAddress);
		printf("  Status = 0x%02X%02X\n", myData[1],myData[0]);
#endif
		// Let's check to see if the deserializer & sync worked OK 
		deserializer = myData[1] & 0x04;
		synch        = myData[1] & 0x02;
#if DEBUGLEVEL > CLEARANDRESETLEVEL
		cout<<"  deserializer = " << deserializer << endl; 
		cout<<"  synch        = " << synch << endl;
#endif
		if ( (deserializer == false) || (synch == false) ) {
#if DEBUGLEVEL > CLEARANDRESETLEVEL
			cout<<"Error on CROC Channel " << i+1 << endl;
			cout<<"  deserializer = " << deserializer << endl;  
			cout<<"  synch        = " << synch << endl;
#endif
			return 1;
		}
	} //end loop over *chains*	

#if DEBUGLEVEL > CLEARANDRESETLEVEL
	cout << endl;
#endif

	return 0;
}


// Read the values in the FEB FPGA Frame
int FEBFPGARead(controller *myController, acquire *myAcquire, croc *myCroc,
	unsigned int crocChannel, febAddresses boardID)
{
#if DEBUGLEVEL > FPGAREADLEVEL
	printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
	printf("Entering FEBFPGARead for FEB %d\n", (int)boardID);
#endif
	unsigned int myAddress;
	int error;
	unsigned short status = 0;
	unsigned char pointer[] = {0x0,0x0};
	unsigned int dpmPointer;
	bool init; 
	
	feb *myFeb = new feb(maxHits, init, boardID, NRegisters);
	myFeb->SetFEBDefaultValues(); 
	
	// Write the message to CROC FIFO, swapped!
	{
		myFeb->MakeMessage();
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocInput; 
#if DEBUGLEVEL > FPGAREADLEVEL
		printf("  FIFO Address   = 0x%X\n",myAddress);
		printf("  Message Length = %d\n",myFeb->GetOutgoingMessageLength());
#endif
		error = myAcquire->WriteCycle(myController->GetHandle(),myFeb->GetOutgoingMessageLength(),
			myFeb->GetOutgoingMessage(),myAddress,AM,DWS);
		if (error!=0) { cout<<"Failure writing to CROC FIFO!\n"; return error; }
		myFeb->DeleteOutgoingMessage(); // must clean up FEB messages manually on a case-by-case basis
	}
		
	// Send the message; crocSendMessage from MinervaDAQTypes.h
	{
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + crocSendMessage;
#if DEBUGLEVEL > FPGAREADLEVEL
		printf("  Send Address   = 0x%X\n",myAddress);
		printf("  Message        = 0x%02X%02X\n",sendMessage[1],sendMessage[0]);
#endif
		error = myAcquire->WriteCycle(myController->GetHandle(),2,sendMessage,myAddress,AM,DW);
		if (error!=0) { cout<<"Failure writing to CROC Send Message Register!\n"; return error; }
	}

	// Be sure the entire message is received before moving on!
	do {
		unsigned char reset_status[] = {0x0,0x0};
		// Read out the status register; crocStatus from MinervaDAQTypes.h
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocStatus;
		error = myAcquire->ReadCycle(myController->GetHandle(),reset_status,myAddress,AM,DW);
		status = reset_status[0] | reset_status[1]<<0x08; 
#if DEBUGLEVEL > FPGAREADLEVEL
		printf("Status = 0x%04X\n",status);
#endif
	} while ( (status & MessageSent) && !(status & MessageReceived) && !(status & CRCError) 
		&& !(status & TimeoutError) && (status & RFPresent) && (status & SerializerSynch) 
		&& (status & DeserializerLock) && (status & PLLLocked) );
	// Decode the status.
	{
#if DEBUGLEVEL > FPGAREADLEVEL
		StatusBits checkValue = MessageSent;
		printf("    Message Sent? => 0x%X\n",(status & checkValue));
		checkValue = MessageReceived;
		printf("    Message Received? => 0x%X\n",(status & checkValue));
		checkValue = CRCError;
		printf("    CRC Error? => 0x%X\n",(status & checkValue));
		checkValue = TimeoutError;
		printf("    Timeout Error? => 0x%X\n",(status & checkValue));
		checkValue = FIFONotEmpty;
		printf("    FIFO Empty? => 0x%X\n",(status & checkValue));
		checkValue = FIFOFull;
		printf("    FIFO Full? => 0x%X\n",(status & checkValue));
		checkValue = DPMFull;
		printf("    DPM Full? => 0x%X\n",(status & checkValue));
		cout << endl;
#endif
	}

	// Read out the pointer to see if we have any data available.
	{
		pointer[0] = 0x0; pointer[1] = 0x0;
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocDPMPointer;
#if DEBUGLEVEL > FPGAREADLEVEL
		printf("Read DPM Address = %X\n",myAddress);
#endif
		error = myAcquire->ReadCycle(myController->GetHandle(),pointer,myAddress,AM,DWS);
		if (error!=0) { cout<<"Failure reading the DPM pointer!\n"; return error; }
		dpmPointer = pointer[0] | pointer[1]<<0x08; 
#if DEBUGLEVEL > FPGAREADLEVEL
		printf("Pointer Error  = %d\n",error);
		printf("Pointer Length = 0x%04X\n",dpmPointer);
#endif
	}
	
	// Read the FPGA.
	{
		if (dpmPointer%2) {dpmPointer -= 1;} else {dpmPointer -= 2;} //must be even
		unsigned char *testarr = new unsigned char [dpmPointer];
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocMemory;
		error = myAcquire->ReadBLT(myController->GetHandle(),testarr,dpmPointer,myAddress,BLT_AM,DWS);
		if (error!=0)  { cout<<"Error in BLT ReadCycle "<<error<<"\n"; return error; }
		myFeb->message = testarr;
		myFeb->DecodeRegisterValues(dpmPointer);
#if DEBUGLEVEL > FPGAREADLEVEL
		cout << "We read fpga's for feb " << (int)myFeb->GetBoardNumber() << endl; 
		myFeb->ShowValues();
		cout << endl;
#endif
		myFeb->message = 0;
		delete [] testarr;
	}

	// Close & Clean up memory
	delete myFeb;

	return 0;
}


// Write some stuff to the FEB FPGA Frame
int FEBFPGAWrite(controller *myController, acquire *myAcquire, croc *myCroc, 
 	unsigned int crocChannel, febAddresses boardID, int HVTarget, int HVEnableFlag)
{
#if DEBUGLEVEL > FPGAWRITELEVEL
	printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
	printf("Entering FEBFPGAWrite for FEB %d\n", (int)boardID);
#endif
	unsigned int myAddress;
	int error;
	unsigned short status = 0;
	unsigned char pointer[] = {0x0,0x0};
	unsigned int dpmPointer;
	bool init; // Is the FEB initialized?

	feb *myFeb = new feb(maxHits, init, boardID, NRegisters);
	myFeb->SetFEBDefaultValues(); // Use defaults to build the basic message.
	// Adjust the relevant parameters.
	{
		unsigned char val[]={0x0};
		myFeb->SetTripPowerOff(val); //turn the trips on
		myFeb->SetGateStart(43000);      
		myFeb->SetGateLength(1702);  
		if (HVEnableFlag) {
			std::cout << "HV Enable Flag is set to ON!\n";
			val[0]=0x1; 
		} else {
			std::cout << "HV Enable Flag is set to OFF!\n";
			val[0]=0x0; 
		}
		myFeb->SetHVEnabled(val);
		myFeb->SetHVTarget(HVTarget);
		val[0]=0x2; myFeb->SetHVNumAve(val);
		val[0]=0x19; myFeb->SetHVPulseWidth(val);
		val[0]=0x0; myFeb->SetHVManual(val);
    	for (int i=0;i<4;i++) { myFeb->SetDiscrimEnableMask(0xFFFF,i); } 
		// Change FEB fpga function to write
		Devices dev = FPGA;
		Broadcasts b = None;
		Directions d = MasterToSlave;
		FPGAFunctions f = Write;
		myFeb->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) myFeb->GetBoardNumber());
	}
	
	// Write the message to CROC FIFO, swapped!
	{
		myFeb->MakeMessage();
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocInput; 
#if DEBUGLEVEL > FPGAWRITELEVEL
		printf("  FIFO Address   = 0x%X\n",myAddress);
		printf("  Message Length = %d\n",myFeb->GetOutgoingMessageLength());
#endif
		error = myAcquire->WriteCycle(myController->GetHandle(),myFeb->GetOutgoingMessageLength(),
			myFeb->GetOutgoingMessage(),myAddress,AM,DWS);
		if (error!=0) { cout<<"Failure writing to CROC FIFO!\n"; return error; }
		myFeb->DeleteOutgoingMessage(); // must clean up FEB messages manually on a case-by-case basis
	}

	// Send the message.
	{
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + crocSendMessage;
#if DEBUGLEVEL > FPGAWRITELEVEL
		printf("  Send Address   = 0x%X\n",myAddress);
		printf("  Message        = 0x%02X%02X\n",sendMessage[1],sendMessage[0]);
#endif
		error = myAcquire->WriteCycle(myController->GetHandle(),2,sendMessage,myAddress,AM,DW);
		if (error!=0) { cout<<"Failure writing to CROC Send Message Register!\n"; return error; }
	}

	// Be sure the entire message is received before moving on!
	do {
		unsigned char reset_status[] = {0x0,0x0};
		// Read out the status register; crocStatus from MinervaDAQTypes.h
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocStatus;
		error = myAcquire->ReadCycle(myController->GetHandle(),reset_status,myAddress,AM,DW);
		status = reset_status[0] | reset_status[1]<<0x08; 
#if DEBUGLEVEL > FPGAWRITELEVEL
		printf("Status = 0x%04X\n",status);
#endif
	} while ( (status & MessageSent) && !(status & MessageReceived) && !(status & CRCError) 
		&& !(status & TimeoutError) && (status & RFPresent) && (status & SerializerSynch) 
		&& (status & DeserializerLock) && (status & PLLLocked) );
	// Decode the status.
	{
#if DEBUGLEVEL > FPGAWRITELEVEL
		StatusBits checkValue = MessageSent;
		printf("    Message Sent? => 0x%X\n",(status & checkValue));
		checkValue = MessageReceived;
		printf("    Message Received? => 0x%X\n",(status & checkValue));
		checkValue = CRCError;
		printf("    CRC Error? => 0x%X\n",(status & checkValue));
		checkValue = TimeoutError;
		printf("    Timeout Error? => 0x%X\n",(status & checkValue));
		checkValue = FIFONotEmpty;
		printf("    FIFO Empty? => 0x%X\n",(status & checkValue));
		checkValue = FIFOFull;
		printf("    FIFO Full? => 0x%X\n",(status & checkValue));
		checkValue = DPMFull;
		printf("    DPM Full? => 0x%X\n",(status & checkValue));
		cout << endl;
#endif
	}

	// Read out the pointer to see if we have any data available.
	{
		pointer[0] = 0x0; pointer[1] = 0x0;
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocDPMPointer;
#if DEBUGLEVEL > FPGAWRITELEVEL
		printf("Read DPM Address = %X\n",myAddress);
#endif
		error = myAcquire->ReadCycle(myController->GetHandle(),pointer,myAddress,AM,DWS);
		if (error!=0) { cout<<"Failure reading the DPM pointer!\n"; return error; }
		dpmPointer = pointer[0] | pointer[1]<<0x08; 
#if DEBUGLEVEL > FPGAWRITELEVEL
		printf("Pointer Error  = %d\n",error);
		printf("Pointer Length = 0x%04X\n",dpmPointer);
#endif
	}
	
	// Read the FPGA.
	// When writing to the FPGA's, the response frame contains the current (written) registers.
	{
		if (dpmPointer%2) {dpmPointer -= 1;} else {dpmPointer -= 2;} //must be even
		unsigned char *testarr = new unsigned char [dpmPointer];
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocMemory;
		myAcquire->ReadBLT(myController->GetHandle(),testarr,dpmPointer,myAddress,BLT_AM,DWS);
		myFeb->message = testarr;
		myFeb->DecodeRegisterValues(dpmPointer);
#if DEBUGLEVEL > FPGAWRITELEVEL
		cout << "We read fpga's for feb " << (int)myFeb->GetBoardNumber() << endl; 
		myFeb->ShowValues();
		cout << endl;
#endif
		myFeb->message = 0;
		delete [] testarr;
	}

	// Close & Clean up memory
	delete myFeb;
	
	return 0;
}


// Read all 6 TRiP-T chip's programming registers
// Assume the TRiPs have already been turned on!
int FEBTRiPTRead(controller *myController, acquire *myAcquire, croc *myCroc,
	unsigned int crocChannel, febAddresses boardID)
{
#if DEBUGLEVEL > TRIPTREADLEVEL
	printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
	printf("Entering FEBTRiPTRead for FEB %d\n", (int)boardID);
#endif
	int error;
	unsigned int myAddress;
	unsigned char pointer[] = {0x0,0x0};
	unsigned int dpmPointer;
	unsigned short status = 0;
	bool init; 
	feb *myFeb = new feb(maxHits, init, boardID, NRegisters);

	// Now let's fiddle with the TRiP's... Let's try to read the registers...
	int maxTrips = 6;
	ofstream registerFile;
	registerFile.open("trip_read_frame.txt");
	
	for (int i=0;i<maxTrips;i++) {
		// clear the status register & dpm pointer 
		// should actually limit this to only channel of interest, but general fn does all 4...
		error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; return error; }
		
		// Set up the message...
		myFeb->GetTrip(i)->SetRead(true); //Default is false...
		myFeb->GetTrip(i)->MakeMessage(); //With read==true, 0's for all "values" to be "written"

		// Record the outgoing frame to text...
		{ 
			int tmpML = myFeb->GetTrip(i)->GetMessageSize();
			unsigned char *testme = myFeb->GetTrip(i)->GetOutgoingMessage(); 
			registerFile << "Trip " << i << endl;
			registerFile << "In read... GetMessageSize=" << tmpML << endl;
			for (int j=0;j<tmpML;j+=4) {
				registerFile << j << "\t" << (int)testme[j];
				if (j+1 < tmpML) registerFile << "\t" << (int)testme[j+1];
				if (j+2 < tmpML) registerFile << "\t" << (int)testme[j+2];
				if (j+3 < tmpML) registerFile << "\t" << (int)testme[j+3];
				registerFile << endl;
			}
			testme = 0;
		}

		// Write the message to CROC FIFO.
		{
			myAddress = myCroc->GetAddress() + (unsigned int)crocInput + 0x4000*(crocChannel-1);
#if DEBUGLEVEL > TRIPTREADLEVEL
			printf("  FIFO Address   = 0x%X\n",myAddress);
			printf("  Message Length = %d\n",myFeb->GetTrip(i)->GetMessageSize());
#endif
			error = myAcquire->WriteCycle(myController->GetHandle(),myFeb->GetTrip(i)->GetMessageSize(),
				myFeb->GetTrip(i)->GetOutgoingMessage(),myAddress,AM,DWS);
			if (error!=0) { cout<<"Failure writing to CROC FIFO!\n"; return error; }		
		}   
		myFeb->GetTrip(i)->DeleteOutgoingMessage(); // must clean up FEB messages manually on a case-by-case basis

		// Send the message.
		{
			myAddress = myCroc->GetAddress() + (unsigned int)crocSendMessage + 0x4000*(crocChannel-1);
#if DEBUGLEVEL > TRIPTREADLEVEL
			printf("  Send Address   = 0x%X\n",myAddress);
			printf("  Message        = 0x%02X%02X\n",sendMessage[1],sendMessage[0]);
#endif			
			error = myAcquire->WriteCycle(myController->GetHandle(),2,sendMessage,myAddress,AM,DW);
			if (error!=0) { cout<<"Failure writing to CROC Send Message Register!\n"; return error; }
		}
		
		// Read out the status register; Be sure the entire message is received before moving on!
		// TRiP programming frames are big!  MUST pull check on (status & MessageSent) &&
		do {
			unsigned char reset_status[] = {0x0,0x0};
			// Read out the status register; crocStatus from MinervaDAQTypes.h
			myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocStatus;
			error = myAcquire->ReadCycle(myController->GetHandle(),reset_status,myAddress,AM,DW);
			status = reset_status[0] | reset_status[1]<<0x08; 
#if DEBUGLEVEL > TRIPTREADLEVEL
			printf("Status = 0x%04X\n",status);
#endif
		} while ( !(status & MessageReceived) && !(status & CRCError) 
			&& !(status & TimeoutError) && (status & RFPresent) && (status & SerializerSynch) 
			&& (status & DeserializerLock) && (status & PLLLocked) );
		// Decode the status.
		{
#if DEBUGLEVEL > TRIPTREADLEVEL
			StatusBits checkValue = MessageSent;
			printf("    Message Sent? => 0x%X\n",(status & checkValue));
			checkValue = MessageReceived;
			printf("    Message Received? => 0x%X\n",(status & checkValue));
			checkValue = CRCError;
			printf("    CRC Error? => 0x%X\n",(status & checkValue));
			checkValue = TimeoutError;
			printf("    Timeout Error? => 0x%X\n",(status & checkValue));
			checkValue = FIFONotEmpty;
			printf("    FIFO Empty? => 0x%X\n",(status & checkValue));
			checkValue = FIFOFull;
			printf("    FIFO Full? => 0x%X\n",(status & checkValue));
			checkValue = DPMFull;
			printf("    DPM Full? => 0x%X\n",(status & checkValue));
			cout << endl;
#endif
		}

		// Read out the pointer, swapped!, to see if we have any data available.
		{
			pointer[0] = 0x0; pointer[1] = 0x0;
			myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocDPMPointer;
#if DEBUGLEVEL > TRIPTREADLEVEL
			printf("Read DPM Address = %X\n",myAddress);
#endif
			error = myAcquire->ReadCycle(myController->GetHandle(),pointer,myAddress,AM,DWS);
			if (error!=0) { cout<<"Failure reading the DPM pointer!\n"; return error; }
			dpmPointer = pointer[0] | pointer[1]<<0x08; 
#if DEBUGLEVEL > TRIPTREADLEVEL
			printf("Pointer Error  = %d\n",error);
			printf("Pointer Length = 0x%04X\n",dpmPointer);
#endif
		}

		// Now Read out... 
		// Note that for "read" frames, we should read what is in the registers.
		{
			if (dpmPointer%2) {dpmPointer -= 1;} else {dpmPointer -= 2;} //must be even	
			unsigned char *testme = new unsigned char [dpmPointer];
			myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocMemory;
			error = myAcquire->ReadBLT(myController->GetHandle(),testme,dpmPointer,myAddress,BLT_AM,DWS);
			if (error!=0)  { cout<<"Error in BLT ReadCycle\n"; return error; }			
			myFeb->GetTrip(i)->message = testme;
			myFeb->GetTrip(i)->DecodeRegisterValues(dpmPointer);
#if DEBUGLEVEL > TRIPTREADLEVEL
			printf("Trip %d:\n",i);
			for (unsigned int k=0;k<14;k++) {
				printf("Trip Register %d Value = %d\n",k,(int)myFeb->GetTrip(i)->GetTripValue(k));
			}
			cout << endl;
#endif
			// Some clean-up...
			myFeb->GetTrip(i)->message = 0;
			delete [] testme;
		}			
	}

	// Close & Clean up memory
	delete myFeb;
	registerFile.close();

	return 0;
}


// Write to all 6 TRiP-T chip's programming registers 
// Assume the TRiPs have already been turned on!
int FEBTRiPTWrite(controller *myController, acquire *myAcquire, croc *myCroc,
	unsigned int crocChannel, febAddresses boardID)
{
#if DEBUGLEVEL > TRIPTWRITELEVEL
	printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
	printf("Entering FEBTRiPTWrite for FEB %d\n", (int)boardID);
#endif
	int error;
	unsigned int myAddress;
	unsigned char pointer[] = {0x0,0x0};
	unsigned int dpmPointer;
	unsigned short status = 0;
	bool init; 
	feb *myFeb = new feb(maxHits, init, boardID, NRegisters);

	// Now let's fiddle with the TRiP's... Let's try to write to the registers...
	int maxTrips = 6;
	ofstream registerFile;
	registerFile.open("trip_write_frame.txt");
	
	for (int i=0;i<maxTrips;i++) {
		// clear the status register & dpm pointer 
		// should actually limit this to only channel of interest, but general fn does all 4...
		error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; return error; }
		
		// Set up the message...
		myFeb->GetTrip(i)->SetRead(false); 
		{
			myFeb->GetTrip(i)->SetRegisterValue( 0, tripRegIBP ); //ibp
			myFeb->GetTrip(i)->SetRegisterValue( 1, tripRegIBBNFOLL ); //ibbnfoll
			myFeb->GetTrip(i)->SetRegisterValue( 2, tripRegIFF ); //iff
			myFeb->GetTrip(i)->SetRegisterValue( 3, tripRegIBPIFF1REF ); //ibpiff1ref
			myFeb->GetTrip(i)->SetRegisterValue( 4, tripRegIBOPAMP ); //ibopamp
			myFeb->GetTrip(i)->SetRegisterValue( 5, tripRegIB_T ); //ib_t
			myFeb->GetTrip(i)->SetRegisterValue( 6, tripRegIFFP2 ); //iffp2
			myFeb->GetTrip(i)->SetRegisterValue( 7, tripRegIBCOMP ); //ibcomp
			myFeb->GetTrip(i)->SetRegisterValue( 8, tripRegVREF ); //v_ref
			myFeb->GetTrip(i)->SetRegisterValue( 9, tripRegVTH ); //v_th
			myFeb->GetTrip(i)->SetRegisterValue(10, 2*maxHits-1); //pipedelay
			myFeb->GetTrip(i)->SetRegisterValue(11, tripRegGAIN ); //gain
			myFeb->GetTrip(i)->SetRegisterValue(12, tripRegIRSEL ); //irsel
			myFeb->GetTrip(i)->SetRegisterValue(13, tripRegIWSEL ); //iwsel
		}
		myFeb->GetTrip(i)->MakeMessage(); 

		// Record the outgoing frame to text...
		{ 
			int tmpML = myFeb->GetTrip(i)->GetMessageSize();
			unsigned char *testme = myFeb->GetTrip(i)->GetOutgoingMessage(); 
			registerFile << "Trip " << i << endl;
			registerFile << "In read... GetMessageSize=" << tmpML << endl;
			for (int j=0;j<tmpML;j+=4) {
				registerFile << j << "\t" << (int)testme[j];
				if (j+1 < tmpML) registerFile << "\t" << (int)testme[j+1];
				if (j+2 < tmpML) registerFile << "\t" << (int)testme[j+2];
				if (j+3 < tmpML) registerFile << "\t" << (int)testme[j+3];
				registerFile << endl;
			}
			testme = 0;
		}

		// Write the message to CROC FIFO.
		{
			myAddress = myCroc->GetAddress() + (unsigned int)crocInput + 0x4000*(crocChannel-1);
#if DEBUGLEVEL > TRIPTWRITELEVEL
			printf("  FIFO Address   = 0x%X\n",myAddress);
			printf("  Message Length = %d\n",myFeb->GetTrip(i)->GetMessageSize());
#endif
			error = myAcquire->WriteCycle(myController->GetHandle(),myFeb->GetTrip(i)->GetMessageSize(),
				myFeb->GetTrip(i)->GetOutgoingMessage(),myAddress,AM,DWS);
			if (error!=0) { cout<<"Failure writing to CROC FIFO!\n"; return error; }		
		}   
		myFeb->GetTrip(i)->DeleteOutgoingMessage(); // must clean up FEB messages manually on a case-by-case basis

		// Send the message.
		{
			myAddress = myCroc->GetAddress() + (unsigned int)crocSendMessage + 0x4000*(crocChannel-1);
#if DEBUGLEVEL > TRIPTWRITELEVEL
			printf("  Send Address   = 0x%X\n",myAddress);
			printf("  Message        = 0x%02X%02X\n",sendMessage[1],sendMessage[0]);
#endif			
			error = myAcquire->WriteCycle(myController->GetHandle(),2,sendMessage,myAddress,AM,DW);
			if (error!=0) { cout<<"Failure writing to CROC Send Message Register!\n"; return error; }
		}
		
		// Read out the status register; Be sure the entire message is received before moving on!
		// TRiP programming frames are big!  MUST pull check on (status & MessageSent) &&
		do {
			unsigned char reset_status[] = {0x0,0x0};
			// Read out the status register; crocStatus from MinervaDAQTypes.h
			myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocStatus;
			error = myAcquire->ReadCycle(myController->GetHandle(),reset_status,myAddress,AM,DW);
			status = reset_status[0] | reset_status[1]<<0x08; 
#if DEBUGLEVEL > TRIPTWRITELEVEL
			printf("Status = 0x%04X\n",status);
#endif
		} while ( !(status & MessageReceived) && !(status & CRCError) 
			&& !(status & TimeoutError) && (status & RFPresent) && (status & SerializerSynch) 
			&& (status & DeserializerLock) && (status & PLLLocked) );
		// Decode the status.
		{
#if DEBUGLEVEL > TRIPTWRITELEVEL
			StatusBits checkValue = MessageSent;
			printf("    Message Sent? => 0x%X\n",(status & checkValue));
			checkValue = MessageReceived;
			printf("    Message Received? => 0x%X\n",(status & checkValue));
			checkValue = CRCError;
			printf("    CRC Error? => 0x%X\n",(status & checkValue));
			checkValue = TimeoutError;
			printf("    Timeout Error? => 0x%X\n",(status & checkValue));
			checkValue = FIFONotEmpty;
			printf("    FIFO Empty? => 0x%X\n",(status & checkValue));
			checkValue = FIFOFull;
			printf("    FIFO Full? => 0x%X\n",(status & checkValue));
			checkValue = DPMFull;
			printf("    DPM Full? => 0x%X\n",(status & checkValue));
			cout << endl;
#endif
		}

		// Read out the pointer, swapped!, to see if we have any data available.
		{
			pointer[0] = 0x0; pointer[1] = 0x0;
			myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocDPMPointer;
#if DEBUGLEVEL > TRIPTWRITELEVEL
			printf("Read DPM Address = %X\n",myAddress);
#endif
			error = myAcquire->ReadCycle(myController->GetHandle(),pointer,myAddress,AM,DWS);
			if (error!=0) { cout<<"Failure reading the DPM pointer!\n"; return error; }
			dpmPointer = pointer[0] | pointer[1]<<0x08; 
#if DEBUGLEVEL > TRIPTWRITELEVEL
			printf("Pointer Error  = %d\n",error);
			printf("Pointer Length = 0x%04X\n",dpmPointer);
#endif
		}

		// No real point in reading and decoding the response frame - the TRiP's send 
		// a response frame composed entirely of zeroes when being *written* to.	
		// Decoding and checking everything is 0 on the read-back can be a sanity check tho...
	}
	
	// Close & Clean up memory
	delete myFeb;
	registerFile.close();

	return 0;
}


// Open a gate
int FastCommandOpenGate(controller *myController, acquire *myAcquire, croc *myCroc)
{
	int error = 0;
	unsigned int myAddress = myCroc->GetAddress() + (unsigned int)crocFastCommand; 
	unsigned char openGateCommand[] = {0xB1};
	int ml = sizeof(openGateCommand)/sizeof(unsigned char);
	error = myAcquire->WriteCycle(myController->GetHandle(), ml, openGateCommand, myAddress, AM, DW);
	if (error!=0) { cout<<"Failure writing to CROC FastCommand Register!\n"; return error; }		
	
	return 0;
}




