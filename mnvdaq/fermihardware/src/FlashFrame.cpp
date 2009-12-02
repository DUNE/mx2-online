#ifndef FlashFrame_cpp
#define FlashFrame_cpp

#include "FlashFrame.h"

// ********************************************************************************
//  Class for creating Flash Frame objects for reprogramming the FEB FPGA chips.
// ********************************************************************************

const int FlashFrame::Spartan_3E_Npages = 1075;
const int FlashFrame::Spartan_3E_PageSize = 264;

FlashFrame::FlashFrame(febAddresses a) 
{ 
	boardNumber = a;
	febNumber[0] = (unsigned char) a; //put the feb number into it's character.
	
	// Build the header for this frame; default is NO FLASH.
	Devices dev = Flash; //the device type for the header
	Broadcasts b = None; //broadcast type for header
	Directions d = MasterToSlave; //message direction for header
	FlashFunctions f = NoFlash; //operation to be performed;

	MakeDeviceFrameTransmit(dev, b, d, f, (unsigned int)febNumber[0]);  //make up the transmission header
}

#endif
