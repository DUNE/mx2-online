#ifndef FlashFrame_cpp
#define FlashFrame_cpp
/*! \file FlashFrame.cpp
*/

#include "FlashFrame.h"
#include "exit_codes.h"

const int FlashFrame::Spartan_3E_Npages = 1075;
const int FlashFrame::Spartan_3E_PageSize = 264;

log4cpp::Category& flashLog = log4cpp::Category::getInstance(std::string("flash"));

FlashFrame::FlashFrame(
    FrameTypes::FEBAddresses a,
    unsigned int theChannelAddress,
    int theCrateNumber) : LVDSFrame() 
{ 
  using namespace FrameTypes;

  febNumber[0] = (unsigned char) a; 
  channelAddress = theChannelAddress;
  crateNumber = theCrateNumber;
  Devices dev = Flash; 
  Broadcasts b = None; 
  Directions d = MasterToSlave; 
  FlashFunctions f = NoFlash; 

  MakeDeviceFrameTransmit(dev, b, d, f, (unsigned int)febNumber[0]);  
  flashLog.setPriority(log4cpp::Priority::DEBUG); 
}

#endif
