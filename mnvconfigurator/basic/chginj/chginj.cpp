#include "acquire.h"
#include "MinervaDAQtypes.h"
#include "controller.h"
#include "feb.h"
#include "adctdc.h"
#include <iostream>
#include <iterator>
#include <fstream>
#include <iomanip>
#include <cstdlib>

using namespace std;

#define DEBUGLEVEL 10
#define CLEARANDRESETLEVEL 50
#define FPGAREADLEVEL 50
#define FPGAWRITELEVEL 50
#define TRIPTREADLEVEL 50
#define TRIPTWRITELEVEL 50
#define BLOCKRAMREADLEVEL 5 // using same for adc & discr

const int NRegisters = 54; // Using v80+ firmware on all FEBs on WH14NXO now.
const int maxHits    = 6;
const int adcHit     = 1;

// Note, indices are distinct from addresses!
const unsigned int crocCardAddress = 1 << 16;
const unsigned int crocChannel     = 1;	
const int crocID                   = 1;
const unsigned int crimCardAddress = 224 << 16;
const int crimID                   = 1;
const int nFEBs                    = 4; // USE SEQUENTIAL ADDRESSING!!!

const int tripRegIBP        =  60;
const int tripRegIBBNFOLL   = 120;
const int tripRegIFF        =   0;
const int tripRegIBPIFF1REF = 160;
const int tripRegIBOPAMP    =  40;
const int tripRegIB_T       =   0;
const int tripRegIFFP2      =   0;
const int tripRegIBCOMP     =  20;
const int tripRegVREF       = 165;
const int tripRegVTH        = 240;
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


int CROCClearStatusAndResetPointer(controller *myController, acquire *myAcquire, croc *myCroc);
int FEBFPGARead(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID);
int FEBFPGAWrite(controller *myController, acquire *myAcquire, croc *myCroc, 
 	unsigned int crocChannel, febAddresses boardID);
// Turn on some charge injection registers to get a discr push.
int FEBFPGAWriteChargeInjection(controller *myController, acquire *myAcquire, croc *myCroc, 
 	unsigned int crocChannel, febAddresses boardID);
// Read all 6 TRiP's
int FEBTRiPTRead(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID);
// Write to all 6 TRiP's
int FEBTRiPTWrite(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID);
// Write to all 6 TRiP's - setup for charge injection.
int FEBTRiPTWriteChargeInjection(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID);
// Open a gate
int FastCommandOpenGate(controller *myController, acquire *myAcquire, croc *myCroc);
// Set up an FEB to read the ADC's
int ReadADCTest(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID, int iHit);
// Set up an FEB to read the Discriminators
int ReadDiscrTest(controller *myController, acquire *myAcquire, croc *myCroc, 
	unsigned int crocChannel, febAddresses boardID);
// Initialize the CRIM for Data Taking
void InitCRIM(controller *myController, acquire *myAcquire, crim *myCrim, int runningMode);


int main() 
{
	int error;		
	int controllerID = 0;
	int runningMode = 0; // 0 == OneShot	
		
	bool doWriteCheck = true;
	
	bool doChjInjConfig = true;
	// bool doChjInjConfig = false;
	
	// Controller & Acquire class init, contact the controller
	controller *myController = new controller(0x00, controllerID);	
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
  
	std::cout << "Making CRIM with index == " << crimID << " && address == " 
		<< (crimCardAddress>>16) << std::endl;
	myController->MakeCrim(crimCardAddress,crimID);
	try {
		error = myController->GetCrimStatus(crimID); 
		if (error) throw error;
	} catch (int e)  {
		std::cout << "Unable to read the status register for CRIM " << 
			((myController->GetCrim(crimID)->GetCrimAddress())>>16) << std::endl;
		exit(-3);
	} 	
	crim *myCrim = myController->GetCrim(crimID);
	InitCRIM(myController, myAcquire, myCrim, runningMode);
	
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

	// Clear Status & Reset
	{
		error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
	}

	if (doChjInjConfig) 
	{	
		// Turn on TriPs, Write to the TRiPs & set up charge inj on FPGA's
		{
			for (std::list<febAddresses>::iterator p = febAddr.begin();
				p != febAddr.end();
				p++) {
					// Clear Status & Reset
					{
						error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
						if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
					}
					error = FEBTRiPTWriteChargeInjection(myController, myAcquire, myCroc, crocChannel, *p);
					if (error!=0) { cout<<"Error in FEB TRiPT Test Write!\n"; exit(error); }	
				}		  
		}
		// Check to see what we wrote...
		if (doWriteCheck) {
			for (std::list<febAddresses>::iterator p = febAddr.begin();
				p != febAddr.end();
				p++) {
					// Clear Status & Reset
					{
						error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
						if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
					}
					error = FEBTRiPTRead(myController, myAcquire, myCroc, crocChannel, *p);
					if (error!=0) { cout<<"Error in FEB TRiPT Test Read!\n"; exit(error); }		
				}		  			
		}	
		// Actually read the TDC's and ADC's...
		{
			for (std::list<febAddresses>::iterator p = febAddr.begin();
				p != febAddr.end();
				p++) {
					// Clear Status & Reset
					{
						error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
						if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }				
					}
					// Read the Discriminators
					{
						error = ReadDiscrTest(myController, myAcquire, myCroc, crocChannel, *p);
						if (error!=0) { cout<<"Error in FEB TRiPT Test Write!\n"; exit(error); }	
					}
					// Clear Status & Reset
					{
						error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
						if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }				
					}
					// Read the ADC Blocks
					{
						error = ReadADCTest(myController, myAcquire, myCroc, crocChannel, *p, adcHit);
						if (error!=0) { cout<<"Error in FEB TRiPT Test Write!\n"; exit(error); }	
					}
				}		  				
		}
		// Clear Status & Reset
		{
			error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
			if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
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
 	unsigned int crocChannel, febAddresses boardID)
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
	bool init; //is the FEB initialized?

	feb *myFeb = new feb(maxHits, init, boardID, NRegisters);
	myFeb->SetFEBDefaultValues(); // use defaults to build the message
	// Twiddle some parameters
	{
		unsigned char val[]={0x0};
		myFeb->SetTripPowerOff(val); //turn the trips on
		myFeb->SetGateStart(43000);      
		myFeb->SetGateLength(1702);  
		myFeb->SetHVPeriodManual(47806);
    	for (int i=0;i<4;i++) { myFeb->SetDiscrimEnableMask(0xFFFF,i); } //NRegisters==54 only!
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


// Write some stuff to the FEB FPGA Frame - turn on some basic charge injection stuff
int FEBFPGAWriteChargeInjection(controller *myController, acquire *myAcquire, croc *myCroc, 
 	unsigned int crocChannel, febAddresses boardID)
{
#if DEBUGLEVEL > FPGAWRITELEVEL
	printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
	printf("Entering FEBFPGAWriteChargeInjection for FEB %d\n", (int)boardID);
#endif
	unsigned int myAddress;
	int error;
	unsigned short status = 0;
	unsigned char pointer[] = {0x0,0x0};
	unsigned int dpmPointer;
	bool init; 
	bool lDecode = true;

	feb *myFeb = new feb(maxHits, init, boardID, NRegisters);
	myFeb->SetFEBDefaultValues(); // use defaults to build the message
	// Twiddle some parameters
	{
		unsigned char val[]={0x0};
		myFeb->SetTripPowerOff(val); //turn the trips on
		myFeb->SetGateStart(43000);  //count to 65535 in clock ticks, 43000 => 211.8 us
		myFeb->SetGateLength(1702);  //gate length for MINERvA in NuMI is 1702
		for (int i=0; i<4; i++) {    // inject registers, DON'T WRITE TO THE LOW GAIN TRIPS!
			unsigned char inj[] = { 1 + (unsigned char)i*40 };   // 15 integration ticks + ~20 reset ticks...
			unsigned char enable[] = {0x1}; // never enable low gain, or things get very confusing...
			myFeb->SetInjectCount(inj,i);
			myFeb->SetInjectEnable(enable,i);
		}
		unsigned short int dacval = 4000;
		myFeb->SetInjectDACValue(dacval);
		unsigned char injPhase[] = {0x1};
		myFeb->SetInjectPhase(injPhase);
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
	
	// Read the FPGA (don't really need to do this here...)
	// When writing to the FPGA's, the response frame contains the current (written) registers.
	if (lDecode) {
		if (dpmPointer%2) {dpmPointer -= 1;} else {dpmPointer -= 2;} //must be even
		unsigned char *testarr = new unsigned char [dpmPointer];
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocMemory;
		myAcquire->ReadBLT(myController->GetHandle(),testarr,dpmPointer,myAddress,BLT_AM,DWS);
		myFeb->message = testarr;
		myFeb->DecodeRegisterValues(dpmPointer);
#if DEBUGLEVEL > FPGAWRITELEVEL
		cout << "We wrote fpga's for feb " << (int)myFeb->GetBoardNumber() << endl; 
		cout << "-> We started the set-up...\n";
		myFeb->ShowValues();
		cout << endl;
#endif
		myFeb->message = 0;
		delete [] testarr;
	}

	// Set DAC Start
	//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	
	// First, clear status & pointer
	{
		error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
	}
	
	// Set new parameters
	{
		unsigned char injStart[] = {0x1};
		myFeb->SetInjectDACStart(injStart);
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
	
	// Read the FPGA (don't really need to do this here...)
	// When writing to the FPGA's, the response frame contains the current (written) registers.
	if (lDecode) {
		if (dpmPointer%2) {dpmPointer -= 1;} else {dpmPointer -= 2;} //must be even
		unsigned char *testarr = new unsigned char [dpmPointer];
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocMemory;
		myAcquire->ReadBLT(myController->GetHandle(),testarr,dpmPointer,myAddress,BLT_AM,DWS);
		myFeb->message = testarr;
		myFeb->DecodeRegisterValues(dpmPointer);
#if DEBUGLEVEL > FPGAWRITELEVEL
		cout << "We wrote fpga's for feb " << (int)myFeb->GetBoardNumber() << endl; 
		cout << "-> We set the DAC start...\n";
		myFeb->ShowValues();
		cout << endl;
#endif
		myFeb->message = 0;
		delete [] testarr;
	}

	// Reset DAC Start
	//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	// First, clear status & pointer
	{
		error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
	}

	// Set new parameters
	{
		unsigned char injReset[] = {0x0};
		myFeb->SetInjectDACStart(injReset);
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
	
	// Read the FPGA (don't really need to do this here...)
	// When writing to the FPGA's, the response frame contains the current (written) registers.
	if (lDecode) {
		if (dpmPointer%2) {dpmPointer -= 1;} else {dpmPointer -= 2;} //must be even
		unsigned char *testarr = new unsigned char [dpmPointer];
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocMemory;
		myAcquire->ReadBLT(myController->GetHandle(),testarr,dpmPointer,myAddress,BLT_AM,DWS);
		myFeb->message = testarr;
		myFeb->DecodeRegisterValues(dpmPointer);
#if DEBUGLEVEL > FPGAWRITELEVEL
		cout << "We wrote fpga's for feb " << (int)myFeb->GetBoardNumber() << endl; 
		cout << "-> We REset the DAC start...\n";
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


// Write to all 6 TRiP-T chip's programming registers for charge injection - also calls FPGA config
int FEBTRiPTWriteChargeInjection(controller *myController, acquire *myAcquire, croc *myCroc,
	unsigned int crocChannel, febAddresses boardID)
{
#if DEBUGLEVEL > TRIPTWRITELEVEL
	printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
	printf("Entering FEBTRiPTWriteChargeInjection for FEB %d\n", (int)boardID);
#endif
	int error;
	unsigned int myAddress;
	unsigned char pointer[] = {0x0,0x0};
	unsigned int dpmPointer;
	unsigned short status = 0;
	bool init; 
	
	// Do FPGA init (turn on trips, set inj registers, etc.)
	{
		error = FEBFPGAWriteChargeInjection(myController, myAcquire, myCroc, crocChannel, boardID);
		if (error!=0) { cout<<"Error in FEB FPGA Write!\n"; return error; }	
	}
	
	// Now let's fiddle with the TRiP's... Let's try to write to the registers...
	feb *myFeb = new feb(maxHits, init, boardID, NRegisters);
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
			myFeb->GetTrip(i)->SetRegisterValue(14, 0x1FE ); //inject, enable first word
			// Injection patterns:
			// ~~~~~~~~~~~~~~~~~~~
			// Funny structure... 34 bits... using "FermiDAQ" nomenclature...
			// InjEx0: 1 bit (extra channel - ignore)
			// InjB0: Byte 0 - 8 bits - visible to HIGH and LOW gain ->(mask) 0x1FE (0xFF<<1)
			// InjB1: Byte 1 - 8 bits - visible to HIGH and LOW gain ->(mask) 0x1FE00 (0xFF<<1)<<8
			// InjB2: Byte 2 - 8 bits - visible to MEDIUM and LOW gain ->(mask) 0x1FE0000, etc.
			// InjB3: Byte 3 - 8 bits - visible to MEDIUM and LOW gain ->(mask) 0x1FE000000, etc.
			// InjEx33: 1 bit (extra channel - ignore)
			// 
			// The high and medium gain channel mappings are straightforward:
			// B0+B1 -> 16 bits -> 16 (qhi) chs in sequence for each of the trips 0-3
			// B2+B3 -> 16 bits -> 16 (qmed) chs in sequence for each of the trips 0-3
			// 
			// The low gain channel mappings are more complicated.  See comments in DecodeRawEvent
			// in the MINERvA Framework.  To write to all 32 channels, we need to write to B0+B1+B2+B3.
			//
			// Note that we are writing to individual TriP's here!  To get a different pattern in 
			// "pixels" 0-15 && 16-31, you need to write something to TriP 0 and something 
			// different to TriP 1, etc.
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
	}

	registerFile.close();
	delete myFeb;
	
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


// Read ADC Block RAM
int ReadADCTest(controller *myController, acquire *myAcquire, croc *myCroc,
	unsigned int crocChannel, febAddresses boardID, int iHit) 
{
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
	printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
	printf("Entering ReadADCTest for FEB %d\n", (int)boardID);
#endif
	int error;
	unsigned int myAddress;
	unsigned char pointer[] = {0x0,0x0};
	unsigned int dpmPointer;
	unsigned short status = 0;
	bool init; 
	feb *myFeb = new feb(maxHits, init, boardID, NRegisters); 
	
	// Here we assume the TRiPs have been turned on & basically configured.
	// Add code here to fiddle with FPGA & TRiP parameters if desired.

	// Send an open gate command to the CROC fast command register.
	{
		error = FastCommandOpenGate(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot send FastCommand!\n"; return error; }
	}

	// Clear Status & Reset
	{
		error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
	}

	// Read an adc ram buffer; adc classes built in feb constructor
	// Write the message to the CROC FIFO, swapped!
	{
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocInput; 
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		printf("  FIFO Address   = 0x%X\n",myAddress);
		printf("  Message Length = %d\n",myFeb->GetADC(iHit)->GetMessageSize());
#endif
		error = myAcquire->WriteCycle(myController->GetHandle(), myFeb->GetADC(iHit)->GetMessageSize(),
			myFeb->GetADC(iHit)->GetOutgoingMessage(), myAddress, AM, DWS);
		if (error!=0) { cout<<"Failure writing to CROC FIFO!\n"; return error; }		
	}

	// Send the message.
	{
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + crocSendMessage;
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
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
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		printf("Status = 0x%04X\n",status);
#endif
	} while ( (status & MessageSent) && !(status & MessageReceived) && !(status & CRCError) 
		&& !(status & TimeoutError) && (status & RFPresent) && (status & SerializerSynch) 
		&& (status & DeserializerLock) && (status & PLLLocked) );
	// Decode the status.
	{
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
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
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		printf("Read DPM Address = %X\n",myAddress);
#endif
		error = myAcquire->ReadCycle(myController->GetHandle(),pointer,myAddress,AM,DWS);
		if (error!=0) { cout<<"Failure reading the DPM pointer!\n"; return error; }
		dpmPointer = pointer[0] | pointer[1]<<0x08; 
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		printf("Pointer Error  = %d\n",error);
		printf("Pointer Length = %d\n",dpmPointer);
#endif
	}
		
	// Now Read out... 
	{
		if (dpmPointer%2) {dpmPointer -= 1;} else {dpmPointer -= 2;} //must be even 
		unsigned char *testme = new unsigned char [dpmPointer];
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocMemory;
		error = myAcquire->ReadBLT(myController->GetHandle(),testme,dpmPointer,myAddress,BLT_AM,DWS);
		if (error!=0)  { cout<<"Error in BLT ReadCycle "<<error<<"\n"; return error; }
		myFeb->GetADC(iHit)->message = testme;
		myFeb->GetADC(iHit)->CheckForErrors(); // just for fun
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		// Print decoded frame...
		myFeb->GetADC(iHit)->DecodeRegisterValues((int)1);
#endif
		// Some clean-up... 
		myFeb->GetADC(iHit)->message = 0;
		delete [] testme;
	}

	// Some clean-up...
	delete myFeb;

	return 0;
}

	
// Read Discr Block RAM
int ReadDiscrTest(controller *myController, acquire *myAcquire, croc *myCroc,
	unsigned int crocChannel, febAddresses boardID) 
{
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
	printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
	printf("Entering ReadDiscrTest for FEB %d\n", (int)boardID);
#endif
	int error;
	unsigned int myAddress;
	unsigned char pointer[] = {0x0,0x0};
	unsigned int dpmPointer;
	unsigned short status = 0;
	bool init; 
	feb *myFeb = new feb(maxHits, init, boardID, NRegisters); 
	
	// Here we assume the TRiPs have been turned on & basically configured.
	// Add code here to fiddle with FPGA & TRiP parameters if desired.

	// Send an open gate command to the CROC fast command register.
	{
		error = FastCommandOpenGate(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot send FastCommand!\n"; return error; }
	}

	// Clear Status & Reset
	{
		error = CROCClearStatusAndResetPointer(myController, myAcquire, myCroc);
		if (error!=0) { cout<<"Cannot Clear Status & Reset Pointer!\n"; exit(error); }
	}

	// Read a discriminator buffer; tdc class built in feb constructor
	// Write the message to the CROC FIFO, swapped!
	{
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocInput; 
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		printf("  FIFO Address   = 0x%X\n",myAddress);
		printf("  Message Length = %d\n",myFeb->GetDisc()->GetMessageSize());
#endif
		error = myAcquire->WriteCycle(myController->GetHandle(), myFeb->GetDisc()->GetMessageSize(),
			myFeb->GetDisc()->GetOutgoingMessage(), myAddress, AM, DWS);
		if (error!=0) { cout<<"Failure writing to CROC FIFO!\n"; return error; }		
	}

	// Send the message.
	{
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + crocSendMessage;
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
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
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		printf("Status = 0x%04X\n",status);
#endif
	} while ( (status & MessageSent) && !(status & MessageReceived) && !(status & CRCError) 
		&& !(status & TimeoutError) && (status & RFPresent) && (status & SerializerSynch) 
		&& (status & DeserializerLock) && (status & PLLLocked) );
	// Decode the status.
	{
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
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
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		printf("Read DPM Address = %X\n",myAddress);
#endif
		error = myAcquire->ReadCycle(myController->GetHandle(),pointer,myAddress,AM,DWS);
		if (error!=0) { cout<<"Failure reading the DPM pointer!\n"; return error; }
		dpmPointer = pointer[0] | pointer[1]<<0x08; 
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		printf("Pointer Error  = %d\n",error);
		printf("Pointer Length = %d\n",dpmPointer);
#endif
	}
		
	// Now Read out... 
	{
		if (dpmPointer%2) {dpmPointer -= 1;} else {dpmPointer -= 2;} //must be even 
		unsigned char *testme = new unsigned char [dpmPointer];
		myAddress = myCroc->GetAddress() + 0x4000*(crocChannel-1) + (unsigned int)crocMemory;
		error = myAcquire->ReadBLT(myController->GetHandle(),testme,dpmPointer,myAddress,BLT_AM,DWS);
		if (error!=0)  { cout<<"Error in BLT ReadCycle "<<error<<"\n"; return error; }
		myFeb->GetDisc()->message = testme;
		myFeb->GetDisc()->CheckForErrors(); // just for fun
#if DEBUGLEVEL > BLOCKRAMREADLEVEL
		// Print decoded frame...
		myFeb->GetDisc()->DecodeRegisterValues((int)1);
#endif
		// Some clean-up... 
		myFeb->GetDisc()->message = 0;
		delete [] testme;
	}

	// Some clean-up...
	delete myFeb;

	return 0;
}


// Initialize the CRIM for Data Taking
void InitCRIM(controller *myController, acquire *myAcquire, crim *myCrim, int runningMode)
{

	
}
