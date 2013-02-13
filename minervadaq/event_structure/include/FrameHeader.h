#ifndef FrameHeader_h
#define FrameHeader_h

#include "log4cppHeaders.h"

/*! \class FrameHeader
 *
 * \brief Class for the Minerva Frame Header.
 *
 * See DocDB 8405. For most frames the CROC-E channel will write 
 * this information directly into the data stream.
 */
class FrameHeader {
	private:
		unsigned short bank_header[4]; 
		log4cpp::Appender* appender; 

	public:
		FrameHeader(int crateID, int crocID, int chanID, 
			int bank, int feb_number, int firmware, int hit, int length, 
			log4cpp::Appender* theAppender=0);
		~FrameHeader() { };
		unsigned short inline *GetBankHeader() { return bank_header; };
};


#endif
