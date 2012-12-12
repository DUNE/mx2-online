#ifndef MinervaEvent_cxx
#define MinervaEvent_cxx

#include "MinervaEvent.h"
#include "MinervaEvent_templates.h"

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
log4cpp::Category& mnvevt = log4cpp::Category::getInstance(std::string("mnvevt"));

/**************************MinervaHeader Class*******************************************/

MinervaHeader::MinervaHeader(int crateID, int crocID, int chanID, 
	int bank, int feb_no, int firmware, int hit, int length, 
	log4cpp::Appender* appender) 
{
/*! \fn 
 *
 * The constructor which makes the MinervaHeader for a data block
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
	hdrAppender  = appender; // log4cpp appender
	if (hdrAppender!=0) mnvevt.setPriority(log4cpp::Priority::DEBUG);

	unsigned short source_id = (crateID&0x03)<<0x0E; //2 bits for the crate id number
	source_id |= (crocID&0x1F) << 0x09; //5 bits for the croc id number
	source_id |= (chanID&0x03) << 0x07; //2 bits for the channel id number
	source_id |= (feb_no&0x0F) << 0x03; //4 bits for the feb id number
	source_id |= hit&0x07; //the hit number

#if DEBUG_HEADERS
	if (hdrAppender!=0) {
		mnvevt.debugStream() << "->Entering MinervaHeader::Minervaheader for a Data Header...";
		mnvevt.debugStream() << " crateID:    " << crateID;
		mnvevt.debugStream() << " crocID:     " << crocID;
		mnvevt.debugStream() << " chanID:     " << chanID;
		mnvevt.debugStream() << " bank:       " << bank;
		mnvevt.debugStream() << " feb_number: " << feb_no;
		mnvevt.debugStream() << " firmware:   " << firmware;
		mnvevt.debugStream() << " hit:        " << hit;
		mnvevt.debugStream() << " length:     " << length;
	}
#endif

	unsigned short magic_pattern = 0xCBCB; 
	bank_header[0] =  magic_pattern; //put the magic pattern for this event into the header
	bank_header[1] = length; //put the buffer length into this event header
	bank_header[2] = ((firmware) << 0x08) | (bank&0xFF); //load up the firmware version for the feb
	bank_header[3] = source_id; //and the source information
	chan_number = (source_id & 0xFF8)>>0x07; //register the "feb number"
#if DEBUG_HEADERS
	if (hdrAppender!=0) {
		mnvevt.debug("\tHeader Words:");
		mnvevt.debug("\t  [1]0x%04X [0]0x%04X",bank_header[1],bank_header[0]);
		mnvevt.debug("\t  [3]0x%04X [2]0x%04X",bank_header[3],bank_header[2]);
	}
#endif
}


MinervaHeader::MinervaHeader(unsigned char crate, log4cpp::Appender* appender) 
{
/*! \fn 
 *
 * Makes data header for the End-of-Event Record (DAQ header).
 */
	hdrAppender  = appender; // log4cpp appender
	if (hdrAppender!=0) mnvevt.setPriority(log4cpp::Priority::DEBUG);
#if DEBUG_HEADERS
	if (hdrAppender!=0) {
		mnvevt.debugStream() << "->Entering MinervaHeader::Minervaheader for the DAQ Header...";
	}
#endif
	unsigned short source_id = crate; //2 bits for the crate id number? WinDAQ DAQHeader source ID?...
	unsigned short magic_pattern = 0xCBCB; 

	bank_header[0] = magic_pattern;    // add: the magic pattern to the header,
	bank_header[1] = 48;               // the length in bytes of the DAQ header,
	bank_header[2] = (3 & 0xFF);       // Bank Type (3 for DAQ Header),
	bank_header[2] |= (9 & 0xFF)<<0x8; // Header Version 9, and
	bank_header[3] = source_id;        // the source information.
#if DEBUG_HEADERS
	if (hdrAppender!=0) {
		mnvevt.debug("\tHeader Words:");
		mnvevt.debug("\t  [1]0x%04X [0]0x%04X",bank_header[1],bank_header[0]);
		mnvevt.debug("\t  [3]0x%04X [2]0x%04X",bank_header[3],bank_header[2]);
	}
#endif
}


/*****************MinervaEvent Class******************************************************/ 
MinervaEvent::MinervaEvent(unsigned char det, unsigned short int config, int run, int sub_run, 
	unsigned short int trig, unsigned char ledLevel, unsigned char ledGroup, 
	unsigned long long g_gate, unsigned int gate, unsigned long long trig_time, 
	unsigned short int error, unsigned int minos, unsigned int read_time, MinervaHeader *header, 
	unsigned short int nADCFrames, unsigned short int nDiscFrames,
	unsigned short int nFPGAFrames, log4cpp::Appender* appender)
{
/*! \fn 
 *
 * Constructor for MinervaEvent event model data block.  This is the "DAQ Header."
 *
 * \param unsigned char det, detector type
 * \param unsigned short config, detector configuration (number of FEBs)
 * \param int run, run number
 * \param int sub_run, sub-run number
 * \param unsigned short trig, trigger type
 * \param unsigned char ledLevel, (1 or Max PE)
 * \param unsigned char ledGroup, (All, A, B, C, or D)
 * \param unsigned long long g_gate, global gate number
 * \param unsigned int gate, current gate number
 * \param unsigned long long trig_time, trigger time
 * \param unsigned short error, error flag
 * \param unsigned int minos, minos trigger time
 * \param unsigned int read_time, the time required for readout in us (we will mask to use only 24 bits)
 * \param MinervaHeader *header, bank header
 * \param unsigned short nADCFrames, the number of ADC frames recorded in this gate
 * \param unsigned short nDiscFrames, the number of Discriminator frames recorded in this gate
 * \param unsigned short nFPGAFrames, the number of FPGA programming frames recorded in this gate
 * \param log4cpp::Appender* appender, the pointer to the log file
 */
	evtAppender  = appender; // log4cpp appender
	if (evtAppender!=0) mnvevt.setPriority(log4cpp::Priority::DEBUG);
#if DEBUG_HEADERS
	if (evtAppender!=0) {
		mnvevt.debugStream() << "->Entering MinervaEvent::MinervaEvent... Building a DAQ Header.";
	}
#endif
	unsigned int event_info_block[12]; //piece up the event information

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
#if DEBUG_HEADERS
	if (evtAppender!=0) {
		for (int i = 0; i < 12; i++) {
			mnvevt.debugStream() << "   DAQHeader Data Int [" << i << "] = " << event_info_block[i];
		}
	}
#endif	
	// We need to allow room for the event header we haven't added yet.
	int buffer_index = 4; // 4+4=8 bytes for the MINERvA Header.
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
	//InsertData(event_block);
#if DEBUG_HEADERS
	if (evtAppender!=0) {
		mnvevt.debugStream() << " DAQ Header Data...";
		for (int i = 0; i < 56; i++) {
			mnvevt.debugStream() << "   event_block[" << i << "] = " << (int)event_block[i];  
		}
	}
#endif
}

#endif