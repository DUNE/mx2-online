#ifndef ADCFrame_h
#define ADCFrame_h

#include "LVDSFrame.h"
/*********************************************************************************
 * Class for creating RAM request frame objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 * 
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 ***********************************************************************************/

const int nPixelsPerFEB         = 64;
const int nHiMedTripsPerFEB     = 4;
const int nSides                = 2;
const int nPixelsPerTrip        = 16;  // nPixelsPerFEB / nHiMedTripsPerFEB
const int nPixelsPerSide        = 32;  // nPixelsPerFEB / nSides
const int nChannelsPerTrip      = 36;  // 1 dummy ADC reading + 32 real channel + 2 edge channels + 1 ADC latency
const int nSkipChannelsPerTrip  = 3;

/*! \class ADCFrame
 *
 * \brief This class controls the ADC frames.
 *
 * This class controls the adc frames.  It sets up the outgoing read request
 * frame and provides a buffer if desired for storing the message from
 * the ADC's
 */
class ADCFrame : public LVDSFrame {
	private:
		unsigned char *buffer; /*!<A buffer for holding ADC raw data */  

	public: 
		ADCFrame(febAddresses a, RAMFunctionsHit f); 
		~ADCFrame() { delete [] outgoingMessage; };

		int inline GetMessageSize() { return FrameHeaderLengthOutgoing; };
		void MakeMessage();
		int DecodeRegisterValues(int febFirmware); // debug function that parses an adc data block
};

#endif
