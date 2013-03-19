#ifndef DiscrFrame_h
#define DiscrFrame_h
/*! \file DiscrFrame.h
*/

#include "LVDSFrame.h"

/*! 
  \class DiscrFrame
  \brief This class controls the discriminator frames.
  \author Cristian Gingu
  \author Gabriel Perdue
  \author Elaine Schulte
 */
/*! \note
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
 * \note 
 * Note: once a delay tick is formed, all subsequent entries for the channel must also be one, so there 
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

		DiscrFrame(FrameTypes::febAddresses a); 
		~DiscrFrame() {};

		void MakeMessage();  
		void DecodeRegisterValues(); 
    unsigned int GetOutgoingMessageLength();

    unsigned int GetNHitsOnTRiP(const unsigned int& tripNumber) const; /*!< 0 <= tripNumber <= 3 */

};
#endif
