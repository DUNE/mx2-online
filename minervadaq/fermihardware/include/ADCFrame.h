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

	public: 
		ADCFrame(FrameTypes::febAddresses a, FrameTypes::RAMFunctionsHit f); 
		~ADCFrame() {};

		// Not entirely sure why we need "+2", but we seem to...
    inline unsigned int GetOutgoingMessageLength() { 
			return (MinervaDAQSizes::FrameHeaderLengthOutgoing + 2); 
		};
		void MakeMessage();
		void DecodeRegisterValues(); 
};

#endif
