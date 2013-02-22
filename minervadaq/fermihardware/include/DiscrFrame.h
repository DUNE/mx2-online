#ifndef DiscrFrame_h
#define DiscrFrame_h

#include "LVDSFrame.h"

const int nPixelsPerFEB         = 64;
const int nHiMedTripsPerFEB     = 4;
const int nSides                = 2;
const int nPixelsPerTrip        = 16;  // nPixelsPerFEB / nHiMedTripsPerFEB
const int nPixelsPerSide        = 32;  // nPixelsPerFEB / nSides
const int nChannelsPerTrip      = 36;  // 1 dummy ADC reading + 32 real channel + 2 edge channels + 1 ADC latency
const int nSkipChannelsPerTrip  = 3;

/*! \class DiscrFrame
 * 
 * \brief This class controls the discriminator frames.
 *
 * This class controls the discriminator frames.  It sets up the outgoing read request
 * frame and provides a buffer if desired for storing the message from
 * the discriminators.
 */
/*! \note
 *   update the DiscDelTicks (Discriminator's Delay Tick is an integer between 0 and 
 *   SRLDepth(16) inclusive.
 *   it counts the number of zeros (if any) before the SRL starts to be filled with ones - see VHDL code... 
 *   We pick a bit from each 16-bit row as a function of channel and sum them.  The true delay tick value is 
 *   16 minus this sum.  So, for example:
 *
 *   row(TempHitArray)    ch0 ch1 ch2 ch3 ch4 ... ch15\n
 *     0                   0   0   0   0   0   ... \n
 *     1                   1   0   0   0   0   ... \n
 *     2                   1   1   0   0   0   ... \n
 *     3                   1   1   1   0   0   ... \n
 *     4                   1   1   1   0   0   ... \n
 *     5                   1   1   1   0   0   ... \n
 *     ...     \n
 *    15                   1   1   1   0   0   ...\n
 *    ----------------------------------------\n
 *     Sum                15  14  13   0   0   ...\n
 *     Delay Ticks         1   2   3   0   0   ... \n
 *
 * \note Note: once a delay tick is formed, all subsequent entries for the channel must also be one, so there 
 * are several valid algorithms that could pick this information out.  Also note: this example should not 
 * be interpreted to imply the delay tick number should or will always climb with channel number.
 */
class DiscrFrame : public LVDSFrame {
	private:
		int MaxHits;
		unsigned char *buffer; /*!<A buffer for holding discriminator raw data */ 

		/*! Helper functions to decode */
		int GetBitFromWord(unsigned short int word, int index);
		int GetBitFromWord(unsigned int word, int index);
		int GetBitFromWord(long_m word, int index);

	public: 

		DiscrFrame(febAddresses a); // always takes the same RAMFunction, outgoing message is always the same!
		~DiscrFrame() { delete [] outgoingMessage; }; //we build a new outgoing message in MakeMessage!

		int inline GetMessageSize() { return FrameHeaderLengthOutgoing; };
		void inline MakeMessage();  //makes the outgoing message
		int DecodeRegisterValues(int a); // debug function that parses the discriminator block
		int GetDiscrFired(int a); //decodes the registers (so we can get the number of hits to process)

    unsigned int GetNHitsOnTRiP(const unsigned int& tripNumber) const; // 0 <= tripNumber <= 3

};
#endif
