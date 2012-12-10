#ifndef FlashFrame_h
#define FlashFrame_h

#include<fstream>

#include "Frames.h"

// ********************************************************************************
//  Class for creating Flash Frame objects for reprogramming the FEB FPGA chips.
// ********************************************************************************

class FlashFrame : public Frames {

	private:
		static const int Spartan_3E_Npages;
		static const int Spartan_3E_PageSize;
		febAddresses boardNumber;

                log4cpp::Appender* flashAppender;

	public:
		FlashFrame(febAddresses, log4cpp::Appender* appender);
		virtual ~FlashFrame() { };

};

#endif
