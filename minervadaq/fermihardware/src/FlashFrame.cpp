#ifndef FlashFrame_cpp
#define FlashFrame_cpp

#include "FlashFrame.h"
#include "exit_codes.h"

// ********************************************************************************
//  Class for creating Flash Frame objects for reprogramming the FEB FPGA chips.
// ********************************************************************************

const int FlashFrame::Spartan_3E_Npages = 1075;
const int FlashFrame::Spartan_3E_PageSize = 264;

// log4cpp category hierarchy.
log4cpp::Category& flashLog = log4cpp::Category::getInstance(std::string("flash"));

FlashFrame::FlashFrame(febAddresses a, log4cpp::Appender* appender) : Frames(appender) 
{ 
	boardNumber = a;
	febNumber[0] = (unsigned char) a; //put the feb number into it's character.
	
	// Build the header for this frame; default is NO FLASH.
	Devices dev = Flash; //the device type for the header
	Broadcasts b = None; //broadcast type for header
	Directions d = MasterToSlave; //message direction for header
	FlashFunctions f = NoFlash; //operation to be performed;

	MakeDeviceFrameTransmit(dev, b, d, f, (unsigned int)febNumber[0]);  //make up the transmission header

        flashAppender  = appender; // log4cpp appender
        if (flashAppender == 0 ) {
                std::cout << "Flash Log Appender is NULL!" << std::endl;
                exit(EXIT_FEB_UNSPECIFIED_ERROR);
        }
        flashLog.setPriority(log4cpp::Priority::DEBUG);  // ERROR?

}

#endif
