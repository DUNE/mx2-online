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

/**************************MinervaHeader Class*******************************************/

MinervaHeader::MinervaHeader(int crateID, int crocID, int chanID, 
	int bank, int feb_no, int firmware, int hit, int length) 
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
 */
	unsigned short source_id = (crateID&0x03)<<0x0E; //2 bits for the crate id number
	source_id |= (crocID&0x1F) << 0x09; //5 bits for the croc id number
	source_id |= (chanID&0x03) << 0x07; //2 bits for the channel id number
	source_id |= (feb_no&0x0F) << 0x03; //4 bits for the feb id number
	source_id |= hit&0x07; //the hit number

#if DEBUG_ME
	std::cout << "\n->Entering MinervaHeader::Minervaheader for a Data Header..." << std::endl;
	std::cout << " crateID:    " << crateID << std::endl;
	std::cout << " crocID:     " << crocID << std::endl;
	std::cout << " chanID:     " << chanID << std::endl;
	std::cout << " bank:       " << bank << std::endl;
	std::cout << " feb_number: " << feb_no << std::endl;
	std::cout << " firmware:   " << firmware << std::endl;
	std::cout << " hit:        " << hit << std::endl;
	std::cout << " length:     " << length << std::endl;
#endif

	unsigned short magic_pattern = 0xCBCB; 
	data_bank_header[0] =  magic_pattern; //put the magic pattern for this event into the header
	data_bank_header[1] = length; //put the buffer length into this event header
	data_bank_header[2] = ((firmware) << 0x08) | (bank&0xFF); //load up the firmware version for the feb
	data_bank_header[3] = source_id; //and the source information
	chan_number = (source_id & 0xFF8)>>0x07; //register the "feb number"
#if DEBUG_ME
	printf("\tHeader Words:\n");
	printf("\t  [1]0x%04X [0]0x%04X\n",data_bank_header[1],data_bank_header[0]);
	printf("\t  [3]0x%04X [2]0x%04X\n",data_bank_header[3],data_bank_header[2]);
#endif
}


MinervaHeader::MinervaHeader(unsigned char crate) 
{
/*! \fn 
 *
 * Makes data header for the End-of-Event Record (DAQ header).
 */
#if DEBUG_ME
	std::cout << "\n->Entering MinervaHeader::Minervaheader for the DAQ Header..." << std::endl;
#endif
	unsigned short source_id = crate; //2 bits for the crate id number? WinDAQ DAQHeader source ID?...
	unsigned short magic_pattern = 0xCBCB; 

	DAQ_event_header[0] = magic_pattern;    // add: the magic pattern to the header,
	DAQ_event_header[1] = 48;               // the length in bytes of the DAQ header,
	DAQ_event_header[2] = (3 & 0xFF);       // Bank Type (3 for DAQ Header),
	DAQ_event_header[2] |= (4 & 0xFF)<<0x8; // Version (4 as of 2009.Dec.05), and
	DAQ_event_header[3] = source_id;        // the source information.
#if DEBUG_ME
	printf("\tHeader Words:\n");
	printf("\t  [1]0x%04X [0]0x%04X\n",DAQ_event_header[1],DAQ_event_header[0]);
	printf("\t  [3]0x%04X [2]0x%04X\n",DAQ_event_header[3],DAQ_event_header[2]);
#endif
}


/*****************MinervaEvent Class******************************************************/ 

MinervaEvent::MinervaEvent(int det, int config, int run, int sub_run, int trig, 
	unsigned int g_gate,unsigned int gate,unsigned long trig_time, 
	unsigned short error, unsigned int minos, MinervaHeader *header) 
{
/*! \fn 
 *
 * Constructor for MinervaEvent event model data block.  This is the "DAQ Header."
 *
 * \param int det detector type
 * \param int config detector configuration
 * \param int run run number
 * \param int sub_run sub-run number
 * \param int trig trigger type
 * \param unsigned int g_gate global gate number
 * \param unsigned int gate current gate number
 * \param unsigned long trig_time trigger time
 * \param unsigned short error error flag
 * \param unsigned int minos minos trigger time
 * \param MinervaHeader *header data bank header
 */
#if DEBUG_ME
	std::cout << "Entering MinervaEvent::MinervaEvent..." << std::endl;
#endif
	unsigned int event_info_block[12]; //piece up the event information

	event_info_block[0] = det & 0xFF;
	event_info_block[0] |= 0 <<0x08; //a reserved byte
	event_info_block[0] |= (config & 0xFFFF)<<0x10;
	event_info_block[1] = run & 0xFFFFFFFF;
	event_info_block[2] = sub_run & 0xFFFFFFFF;
	event_info_block[3] = trig & 0xFFFFFFFF;
	event_info_block[4] = g_gate & 0xFFFFFFFF; // the "global gate"; TODO - fix this!... doesn't incrememnt!
	event_info_block[5] = 0; // TODO, Fix this!  Global gate is 64 bits!
	event_info_block[6] = gate & 0xFFFFFFFF; //the gate number
	event_info_block[7] = 0; // TODO, Fix this!  Gate is also 64 bits! 
	event_info_block[8] = trig_time & 0xFFFFFFFF; //the gate time, TODO - fill trig_time!
	event_info_block[9] = 0; // TODO, Fix this!  GPS Time Stamp is 64 bits!
	event_info_block[10] =  error & 0xFFFF; //the error bytes
	event_info_block[10] |= 0<<0x10; //2 reserved bytes
	event_info_block[11] = minos & 0xFFFFFFFF; //the minos gate
	
	// We need to allow room for the event header we haven't added yet.
	int buffer_index = 4; // 4+4=8 bytes for the MINERvA Header.
	for (int i = 0; i < 12; i++) {
		buffer_index += 4;   
		event_block[buffer_index]   = event_info_block[i] & 0xFF;
		event_block[buffer_index+1] = event_info_block[i] & 0xFF00;
		event_block[buffer_index+2] = event_info_block[i] & 0xFF0000;
		event_block[buffer_index+3] = event_info_block[i] & 0xFF000000;
	}

	unsigned short *tmpDAQHeader = header->GetDAQEvtHeader();
	buffer_index = 0; 
	for (int i = 0; i < 4 ;i++) {
		event_block[buffer_index] = tmpDAQHeader[i]&0xFF;
		buffer_index++;
		event_block[buffer_index] = (tmpDAQHeader[i]&0xFF00)>>0x08;
		buffer_index++;
	}
	//InsertData(event_block);
// #if DEBUG_ME
//	std::cout << " DAQ Header Data..." << std::endl;
//	for (int i = 0; i < 12; i++) {
//		std::cout << "   event_block[" << i << "] = " << (int)event_block[i] << std::endl;  
//	}
// #endif
}

#endif
