// General Headers
#include <stdio.h>
#include <unistd.h>
#include <iostream>
#include <iterator>
#include <fstream>
#include <iomanip>
#include <cstdlib>

// log4cpp Headers
#include "log4cpp/Portability.hh"
#include "log4cpp/Category.hh"
#include "log4cpp/Appender.hh"
#include "log4cpp/FileAppender.hh"
#include "log4cpp/OstreamAppender.hh"
#include "log4cpp/SyslogAppender.hh"
#include "log4cpp/Layout.hh"
#include "log4cpp/BasicLayout.hh"
#include "log4cpp/Priority.hh"
#include "log4cpp/NDC.hh"

// MINERvA DAQ Headers
#include "acquire.h"
#include "MinervaDAQtypes.h"
#include "controller.h"
#include "feb.h"
#include "adctdc.h"


// Implement this interface for your own strategies for printing log statements.
log4cpp::Appender* appender;
// Return the root of the Category hierarchy.
log4cpp::Category& root = log4cpp::Category::getRoot();
// Further category hierarchy.
log4cpp::Category& clearAndReset = log4cpp::Category::getInstance(std::string("clearAndReset"));
// log4cpp Priority Chain.  Messages of higher numerical priority will not pass.
/*
Priorities
typedef enum {
	EMERG  = 0, 
	FATAL  = 0,
	ALERT  = 100,
	CRIT   = 200,
	ERROR  = 300, 
	WARN   = 400,
	NOTICE = 500,
	INFO   = 600,
	DEBUG  = 700,
	NOTSET = 800
} PriorityLevel;
*/

using namespace std;

#define DEBUGLEVEL 10
#define CLEARANDRESETLEVEL 50
#define FPGAREADLEVEL 50
#define FPGAWRITELEVEL 50
#define TRIPTREADLEVEL 50
#define TRIPTWRITELEVEL 50
#define BLOCKRAMREADLEVEL 5 // using same for adc & discr

const int NRegisters = 54; // Using v80+ firmware on all FEBs now.
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

void SetPriorities() {
	root.setPriority(log4cpp::Priority::ERROR); 
	clearAndReset.setPriority(log4cpp::Priority::DEBUG);
};

int CROCClearStatusAndResetPointer(controller *myController, acquire *myAcquire, croc *myCroc);



int main(int argc, char** argv) 
{
	// FileAppender appends to named files.  Supply full path (otherwise sits in program dir).
	if (argc < 2) {
		appender = new log4cpp::FileAppender("default", "testlog.txt");
	} else {
		appender = new log4cpp::FileAppender("default", argv[1]);
	}

	// BasicLayout is a simple fixed format Layout implementation. 
	appender->setLayout(new log4cpp::BasicLayout());

	// Add appender & set priorities.
	root.addAppender(appender);
	SetPriorities();
	
	int error;		
	int controllerID = 0;
	int runningMode  = 0; // 0 == OneShot	
	
	// Controller & Acquire class init, contact the controller
	controller *myController = new controller(0x00, controllerID);	
	acquire *myAcquire = new acquire(); 				
	if ((error=myController->ContactController())!=0) { 
		root.critStream() << "Controller contact error: " << error << log4cpp::eol; 
		exit(error); // Exit due to no controller!
	}
	root.infoStream() << "Controller & Acquire Initialized..." << log4cpp::eol;


	
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
		clearAndReset.debugStream() << "DPMReset Flag = " << error << log4cpp::eol;
		// Clear Status.
		error = myAcquire->WriteCycle(myController->GetHandle(),2,crocChanResetValue,myAddress,AM,DW);
		clearAndReset.debugStream() << "Clear Status Flag = " << error << log4cpp::eol;		
		// Read Status
		myAddress = myCroc->GetAddress() + (unsigned int)crocStatus + i*0x4000;
		error = myAcquire->ReadCycle(myController->GetHandle(),myData,myAddress,AM,DW);
		clearAndReset.debugStream() << "Read Status Flag = " << error << log4cpp::eol;				
		clearAndReset.debugStream() << "Address  = " << myAddress << log4cpp::eol;		
		clearAndReset.debugStream() << "  Status = " << (myData[0] + myData[1]<<8) << log4cpp::eol;		
		// Let's check to see if the deserializer & sync worked OK 
		deserializer = myData[1] & 0x04;
		synch        = myData[1] & 0x02;
		clearAndReset.debugStream() <<"  deserializer = " << deserializer << log4cpp::eol;
		clearAndReset.debugStream() <<"  synch        = " << synch << log4cpp::eol;
		if ( (deserializer == false) || (synch == false) ) {
			clearAndReset.debugStream() << "Error on CROC Channel " << i+1 << log4cpp::eol;
			clearAndReset.debugStream() << "  deserializer = " << deserializer << log4cpp::eol;  
			clearAndReset.debugStream() << "  synch        = " << synch << log4cpp::eol;
			return 1;
		}
	} //end loop over *chains*	

	return 0;
}
