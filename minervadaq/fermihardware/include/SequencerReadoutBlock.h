#ifndef SequencerReadoutBlock_h
#define SequencerReadoutBlock_h

#include "LVDSFrame.h"
#include <list>


/*! \class SequencerReadoutBlock
 *
 * \brief The class which holds all of the information associated with an SequencerReadoutBlock.
 *
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
