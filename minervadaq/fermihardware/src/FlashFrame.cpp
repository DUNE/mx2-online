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

FlashFrame::FlashFrame(febAddresses a) : Frames() 
{ 
  boardNumber = a;
  febNumber[0] = (unsigned char) a; //put the feb number into it's character.

  // Build the header for this frame; default is NO FLASH.
  Devices dev = Flash; 
  Broadcasts b = None; 
  Directions d = MasterToSlave; 
  FlashFunctions f = NoFlash; 

  MakeDeviceFrameTransmit(dev, b, d, f, (unsigned int)febNumber[0]);  

  flashLog.setPriority(log4cpp::Priority::DEBUG);  // ERROR?

}

#endif
