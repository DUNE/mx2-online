#ifndef DAQHeader_cxx
#define DAQHeader_cxx

#include "DAQHeader.h"

log4cpp::Category& daqevt = log4cpp::Category::getInstance(std::string("daqevt"));

DAQHeader::DAQHeader(FrameHeader *header)
{
  daqevt.setPriority(log4cpp::Priority::DEBUG);
  daqevt.debugStream() << "->Entering DAQHeader::DAQHeader... Building a Sentinel Frame.";
  for (int i = 0; i < daqHeaderSize; i++) {
    event_block[i] = 0;
    /* daqevt.debugStream() << "   event_block[" << i << "] = " << (int)event_block[i]; */  
  }
  unsigned short *tmpDAQHeader = header->GetBankHeader();
  int buffer_index = 0; 
  for (int i = 0; i < 4 ;i++) {
    event_block[buffer_index] = tmpDAQHeader[i]&0xFF;
    buffer_index++;
    event_block[buffer_index] = (tmpDAQHeader[i]&0xFF00)>>0x08;
    buffer_index++;
  }
}

DAQHeader::DAQHeader(unsigned char det, unsigned short int config, int run, int sub_run, 
    unsigned short int trig, unsigned char ledLevel, unsigned char ledGroup, 
    unsigned long long g_gate, unsigned int gate, unsigned long long trig_time, 
    unsigned short int error, unsigned int minos, unsigned int read_time, FrameHeader *header, 
    unsigned short int nADCFrames, unsigned short int nDiscFrames,
    unsigned short int nFPGAFrames)
{
  daqevt.setPriority(log4cpp::Priority::DEBUG);
  daqevt.debugStream() << "->Entering DAQHeader::DAQHeader... Building a DAQ Header.";
  unsigned int event_info_block[12]; 

  event_info_block[0] = det & 0xFF;
  event_info_block[0] |= 0 <<0x08; //a reserved byte
  event_info_block[0] |= (config & 0xFFFF)<<0x10;
  event_info_block[1] = run & 0xFFFFFFFF;
  event_info_block[2] = sub_run & 0xFFFFFFFF;
  event_info_block[3] = trig & 0xFF;
  event_info_block[3] |= ( (ledLevel & 0x3) << 8 );
  event_info_block[3] |= ( (ledGroup & 0xF8) << 8 );
  event_info_block[3] |= ( (nFPGAFrames & 0xFFFF) << 16 );
  event_info_block[4] = g_gate & 0xFFFFFFFF;            // the "global gate" least sig int 
  event_info_block[5] = (g_gate>>32) & 0xFFFFFFFF;      // the "global gate" most sig int
  event_info_block[6] = gate & 0xFFFFFFFF;              // the gate number least sig int 
  event_info_block[7] = (nDiscFrames << 16) | (nADCFrames);
  event_info_block[8] = trig_time & 0xFFFFFFFF;         // the gate time least sig int
  event_info_block[9] = (trig_time>>32) & 0xFFFFFFFF;   // the gate time most sig int
  event_info_block[10] = ( (error & 0x7) << 4 ) & 0xFF; // the error bits 4-7
  event_info_block[10] |= ( (read_time & 0xFFFFFF) << 8 ) & 0xFFFFFF00;  
  event_info_block[11] = minos & 0x3FFFFFFF;           // the minos gate (only 28 bits of data)
  for (int i = 0; i < 12; i++) {
    daqevt.debugStream() << "   DAQHeader Data Int [" << i << "] = " << event_info_block[i];
  }
  // We need to allow room for the Minerva Frame Header we haven't added yet.
  int buffer_index = 4; // 4+4=8 bytes for the MINERvA Frame Header.
  for (int i = 0; i < 12; i++) {
    buffer_index += 4;   
    event_block[buffer_index]   = event_info_block[i] & 0xFF;
    event_block[buffer_index+1] = (event_info_block[i]>>8) & 0xFF;
    event_block[buffer_index+2] = (event_info_block[i]>>16) & 0xFF;
    event_block[buffer_index+3] = (event_info_block[i]>>24) & 0xFF;
  }

  unsigned short *tmpDAQHeader = header->GetBankHeader();
  buffer_index = 0; 
  for (int i = 0; i < 4 ;i++) {
    event_block[buffer_index] = tmpDAQHeader[i]&0xFF;
    buffer_index++;
    event_block[buffer_index] = (tmpDAQHeader[i]&0xFF00)>>0x08;
    buffer_index++;
  }
  daqevt.debugStream() << " DAQ Header Data...";
  for (int i = 0; i < daqHeaderSize; i++) {
    daqevt.debugStream() << "   event_block[" << i << "] = " << (int)event_block[i];  
  }
}

#endif
