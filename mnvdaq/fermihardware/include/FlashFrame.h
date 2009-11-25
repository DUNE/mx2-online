#ifndef FlashFrame_h
#define FlashFrame_h

// system headers go here
#include<fstream>

// CAEN VME headers go here 

// custom headers go here
#include "Frames.h"

// ********************************************************************************
//  Class for creating Flash Frame objects for reprogramming the FEB FPGA chips.
// ********************************************************************************

class FlashFrame : public Frames {

	private:
		static const int Spartan_3E_Npages;
		static const int Spartan_3E_PageSize;
		febAddresses boardNumber;
	    
	public:
		 FlashFrame(febAddresses,std::ofstream &lf);
		//FlashFrame(febAddresses);
		virtual ~FlashFrame() { };
};

#endif
