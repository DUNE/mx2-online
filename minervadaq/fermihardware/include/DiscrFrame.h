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
 *   row(TempHitArray)    ch0 ch1 ch2 ch3 ch4 ... ch15
 *     0                   0   0   0   0   0   ... 
 *     1                   1   0   0   0   0   ... 
 *     2                   1   1   0   0   0   ... 
 *     3                   1   1   1   0   0   ... 
 *     4                   1   1   1   0   0   ... 
 *     5                   1   1   1   0   0   ... 
 *     ...     
 *    15                   1   1   1   0   0   ...
 *    ----------------------------------------
 *     Sum                15  14  13   0   0   ...
 *     Delay Ticks         1   2   3   0   0   ... 
 *
 * \note 
 * Note: once a delay tick is formed, all subsequent entries for the channel must also be one, so there 
 * are several valid algorithms that could pick this information out.  Also note: this example should not 
 * be interpreted to imply the delay tick number should or will always climb with channel number.
 */
class DiscrFrame : public LVDSFrame {
	private:
		int MaxHits;
		unsigned char *buffer; 
		
		int GetBitFromWord(unsigned short int word, int index); /*!< Helper function to decode */
		int GetBitFromWord(unsigned int word, int index);       /*!< Helper function to decode */
		int GetBitFromWord(long_m word, int index);             /*!< Helper function to decode */

	public: 

		DiscrFrame(FrameTypes::FEBAddresses a); 
		~DiscrFrame() {};

		void MakeMessage();  
		void DecodeRegisterValues(); 
    unsigned int GetOutgoingMessageLength();

    unsigned int GetNHitsOnTRiP(const unsigned int& tripNumber) const; /*!< 0 <= tripNumber <= 3 */

};
#endif
