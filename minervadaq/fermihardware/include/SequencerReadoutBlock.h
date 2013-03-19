#ifndef SequencerReadoutBlock_h
#define SequencerReadoutBlock_h
/*! \file SequencerReadoutBlock.h
*/

#include "LVDSFrame.h"
#include <list>

/*! 
  \class SequencerReadoutBlock
  \brief Holds blocks of data read from EChannels in sequencer (RDFE) mode.
  \author Gabriel Perdue
 */

class SequencerReadoutBlock {

	private:
	  unsigned char * data;	
    unsigned short dataLength;

    std::list<LVDSFrame*> frames;
		
	public:
		SequencerReadoutBlock(); 
		~SequencerReadoutBlock();    

    void SetData(unsigned char * data, unsigned short dataLength);
    void ClearData();
    unsigned char * GetData() const;
    unsigned short GetDataLength() const;

    void ProcessDataIntoFrames();
    LVDSFrame * PopOffFrame();
    inline unsigned int FrameCount() const { return frames.size(); };

};

#endif
