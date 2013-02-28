#ifndef FrameHeader_cxx
#define FrameHeader_cxx

#include "FrameHeader.h"

// Minerva Frame Header (Channel Status replaces the Magic Pattern)
// 
// [ [Frame Length MSB] [Frame Length LSB] ]  // word0: Minerva Frame Header
// [ [ Channel Status ] [ Channel Status ] ]  // word1: Replaces "Magic Pattern"
// [ [ FEB Firmware V.] [ Dev. Functions ] ]  // word2: Minerva Frame Header
// [ [ Source ID MSB  ] [ Source ID LSB  ] ]  // word3: Minerva Frame Header

log4cpp::Category& frameheader = log4cpp::Category::getInstance(std::string("frameheader"));

FrameHeader::FrameHeader(int crateID, int crocID, int chanID, 
    int bank, int feb_no, int firmware, int hit, int length) 
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
   */
  frameheader.setPriority(log4cpp::Priority::DEBUG);

  unsigned short source_id = 0;
  source_id |= (crateID & 0x03) << 14; // 2 bits for the crate id number
  source_id |= (hit     & 0x08) << 13; // 1 bits for the hit number
  source_id |= (crocID  & 0x0F) <<  9; // 4 bits for the croc id number
  source_id |= (chanID  & 0x03) <<  7; // 2 bits for the channel id number
  source_id |= (feb_no  & 0x0F) <<  3; // 4 bits for the feb id number
  source_id |= (hit     & 0x07);       // 3 bits for the hit number

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

  // in addition to the channel status, CBCB will also be accepted
  unsigned short magic_pattern = 0xCBCB; 
  bank_header[0] = length; 
  bank_header[1] = magic_pattern; 
  bank_header[2] = ((firmware) << 0x08) | (bank&0xFF); 
  bank_header[3] = source_id; 
  frameheader.debug("\tHeader Words (32-bit format, [MSW][LSW]:");
  frameheader.debug("\t  [1]0x%04X [0]0x%04X",bank_header[1],bank_header[0]);
  frameheader.debug("\t  [3]0x%04X [2]0x%04X",bank_header[3],bank_header[2]);
}




#endif
