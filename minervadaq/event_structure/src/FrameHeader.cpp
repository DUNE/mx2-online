#ifndef FrameHeader_cxx
#define FrameHeader_cxx
/*! \file FrameHeader.cpp
*/

#include "log4cppHeaders.h"
#include "FrameHeader.h"

// Minerva Frame Header (Channel Status replaces the Magic Pattern)
// 
// [ [Frame Length MSB] [Frame Length LSB] ]  // word0: Minerva Frame Header
// [ [ Channel Status ] [ Channel Status ] ]  // word1: Replaces "Magic Pattern"
// [ [ FEB Firmware V.] [ Dev. Functions ] ]  // word2: Minerva Frame Header
// [ [ Source ID MSB  ] [ Source ID LSB  ] ]  // word3: Minerva Frame Header

log4cpp::Category& frameheader = log4cpp::Category::getInstance(std::string("frameheader"));

//! Default ctor.
/*!
  \param crateID  crate from which data came
  \param crocID   CROC from which data came
  \param chanID   channel from which data came
  \param bank     data banke type
  \param feb_no   FEB number
  \param firmware FEB firmware
  \param hit      hit number
  \param length   message length
  */
FrameHeader::FrameHeader(int crateID, int crocID, int chanID, 
    int bank, int feb_no, int firmware, int hit, int length) 
{
#ifndef GOFAST
  frameheader.setPriority(log4cpp::Priority::DEBUG);
#else
  frameheader.setPriority(log4cpp::Priority::INFO);
#endif

  unsigned short source_id = 0;
  source_id |= (crateID & 0x03) << 14; // 2 bits for the crate id number
  source_id |= (hit     & 0x08) << 13; // 1 bits for the hit number
  source_id |= (crocID  & 0x0F) <<  9; // 4 bits for the croc id number
  source_id |= (chanID  & 0x03) <<  7; // 2 bits for the channel id number
  source_id |= (feb_no  & 0x0F) <<  3; // 4 bits for the feb id number
  source_id |= (hit     & 0x07);       // 3 bits for the hit number

#ifndef GOFAST
  frameheader.debugStream() << "->Entering FrameHeader::FrameHeader for a Data Header...";
  frameheader.debugStream() << " crateID:    " << crateID;
  frameheader.debugStream() << " crocID:     " << crocID;
  frameheader.debugStream() << " chanID:     " << chanID;
  // bank decoding: 0==ADC, 1==Discr, 2==FPGA, 3==DAQ, 4==TRiP, 5==Sentinel
  frameheader.debugStream() << " bank:       " << bank;
  frameheader.debugStream() << " feb_number: " << feb_no;
  frameheader.debugStream() << " firmware:   " << firmware;
  frameheader.debugStream() << " hit:        " << hit;
  frameheader.debugStream() << " length:     " << length;
#endif

  // in addition to the channel status, CBCB will also be accepted
  unsigned short magic_pattern = 0xCBCB; 
  bank_header[0] = byteSwap( length ); 
  bank_header[1] = magic_pattern; 
  bank_header[2] = ((bank&0xFF)<<8) | (firmware&0xFF); 
  bank_header[3] = byteSwap( source_id ); 
#ifndef GOFAST
  frameheader.debug("\tHeader Words (32-bit format, [MSW][LSW]:");
  frameheader.debug("\t  [1]0x%04X [0]0x%04X",bank_header[1],bank_header[0]);
  frameheader.debug("\t  [3]0x%04X [2]0x%04X",bank_header[3],bank_header[2]);
#endif
}

//-----------------------------
unsigned short FrameHeader::byteSwap( unsigned short data ) const
{
	unsigned char b0 = data & 0xFF;
	unsigned char b1 = (data >> 8) & 0xFF;
	return ( (b0 << 8) | b1 );
}

//-----------------------------
std::ostream& operator<<(std::ostream& out, const FrameHeader& s)
{
	const unsigned short *header = s.GetBankHeader();
	for (unsigned int i = 0; i < 4; ++i)
		out << "Word[" << std::dec << i << "] = 0x" << std::hex << header[i] << " ";

	return out;
}




#endif
