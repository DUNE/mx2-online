#ifndef FlashFrame_h
#define FlashFrame_h

#include<fstream>

#include "LVDSFrame.h"

// ********************************************************************************
//  Class for creating Flash Frame objects for reprogramming the FEB FPGA chips.
// ********************************************************************************

class FlashFrame : public LVDSFrame {

  private:
    static const int Spartan_3E_Npages;
    static const int Spartan_3E_PageSize;

  public:
    FlashFrame(FrameTypes::febAddresses theAddress);
    virtual ~FlashFrame() { };

};

#endif
