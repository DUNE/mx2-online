#ifndef FrameHeader_cxx
#define FrameHeader_cxx

#include "FrameHeader.h"

// "LHCb" Header structure:
//    [ Bank Length - 2 bytes ][ Magic Pattern - 2 bytes (0xCBCB) ]
//    [  Source ID - 2 bytes  ][ Version  1 byte ][ Type  1 byte  ]
// Or, in byte array form:
//  h[0] = Magic Pattern LSByte
//  h[1] = Magic Pattern MSByte
//  h[2] = Bank Length LSByte
//  h[3] = Bank Length MSByte
//  h[4] = Type (Bank Type - FPGA, ADC, TDC, DAQ, etc.)
//  h[5] = Version (FEB firmware version or DAQ Header Version (needed for unpacking)
//  h[6] = Source ID LSByte
//  h[7] = Source ID MSByte

// log4cpp category hierarchy.
log4cpp::Category& frameheader = log4cpp::Category::getInstance(std::string("frameheader"));

FrameHeader::FrameHeader(int crateID, int crocID, int chanID, 
	int bank, int feb_no, int firmware, int hit, int length, 
	log4cpp::Appender* theAppender) 
{
/*! \fn 
 *
 * The constructor which makes the FrameHeader for a data block
 *
 * \param int crateID crate from which data came
 * \param int crocID CROC from which data came
 * \param int chanID channel from which data came
 * \param int bank data banke type
 * \param int feb_no FEB number
 * \param int firmware FEB firmware
 * \param int hit hit number
 * \param int length message length
 * \param log4cpp::Appender* appender sets the log file to use
 */
	appender = theAppender; // log4cpp appender
	if (appender) frameheader.setPriority(log4cpp::Priority::DEBUG);

	unsigned short source_id = (crateID&0x03)<<0x0E; //2 bits for the crate id number
	source_id |= (crocID&0x1F) << 0x09; //5 bits for the croc id number
	source_id |= (chanID&0x03) << 0x07; //2 bits for the channel id number
	source_id |= (feb_no&0x0F) << 0x03; //4 bits for the feb id number
	source_id |= hit&0x07; //the hit number

	if (appender) {
		frameheader.debugStream() << "->Entering FrameHeader::FrameHeader for a Data Header...";
		frameheader.debugStream() << " crateID:    " << crateID;
		frameheader.debugStream() << " crocID:     " << crocID;
		frameheader.debugStream() << " chanID:     " << chanID;
		frameheader.debugStream() << " bank:       " << bank;
		frameheader.debugStream() << " feb_number: " << feb_no;
		frameheader.debugStream() << " firmware:   " << firmware;
		frameheader.debugStream() << " hit:        " << hit;
		frameheader.debugStream() << " length:     " << length;
	}

	unsigned short magic_pattern = 0xCBCB; 
	bank_header[0] =  magic_pattern; 
	bank_header[1] = length; 
	bank_header[2] = ((firmware) << 0x08) | (bank&0xFF); 
	bank_header[3] = source_id; 
	if (appender) {
		frameheader.debug("\tHeader Words:");
		frameheader.debug("\t  [1]0x%04X [0]0x%04X",bank_header[1],bank_header[0]);
		frameheader.debug("\t  [3]0x%04X [2]0x%04X",bank_header[3],bank_header[2]);
	}
}




#endif
