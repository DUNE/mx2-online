#ifndef event_builder_templates_hh
#define event_builder_templates_hh

#include <iostream>
#include <fstream>

template <class X> MinervaHeader* BuildBankHeader(event_handler *evt, X *frame) 
{
/*! \fn 
 *
 * Templated function for building up the bank headers.
 *
 * \param event_handler *evt a copy of the event handler structure
 * \param X *frame the data frame
 */
	int feb_number = frame->GetFEBNumber(); //get the feb number from which this frame came
	int index      = -1; //the index which holds this feb's firmware
	int length     = evt->event_data[0] + (evt->event_data[1]<<8);

	//now we've got everything we need to make up the event headers
	MinervaHeader *tmp_header; //declare a new data bank header
	if (evt->feb_info[4]==3) {
		std::cout << "Should not have passed DAQ block to BuildBlockHeader!" << std::endl;
		exit (-1);
	} else {
#if DEBUG_ME
		std::cout << "--------BuildBankHeader--------" << std::endl;
		std::cout << "  crateID                       : " << evt->feb_info[1] << std::endl;
		std::cout << "  crocID                        : " << evt->feb_info[2] << std::endl;
		std::cout << "  chanID                        : " << evt->feb_info[3] << std::endl;
		std::cout << "  bank                          : " << evt->feb_info[4] << std::endl;
		std::cout << "  feb_number (from frame header): " << feb_number << std::endl;
		std::cout << "  firmware                      : " << evt->feb_info[7] << std::endl;
		std::cout << "  hit                           : " << evt->feb_info[8] << std::endl;
		std::cout << "  length                        : " << length << std::endl;
#endif
		tmp_header = new MinervaHeader(evt->feb_info[1], evt->feb_info[2], evt->feb_info[3],
			evt->feb_info[4], feb_number, evt->feb_info[7],
			evt->feb_info[8], length); // Compose a regular data block header.
	}
	return tmp_header; //return the header
};


template <class X> void DecodeBuffer(event_handler *evt, X *frame, int i, int length) 
{
/*! \fn
 *
 * A templated function for decoding a data buffer
 *
 * \param event_handler *evt a pointer to the event handler structure
 * \param X *frame the data frame
 * \param int i byte offset
 * \param int length the message length 
 */
#if DEBUG_ME
	std::cout << "  DecodeBuffer Parameters: " << std::endl;
	std::cout << "   byte offset: " << i << std::endl;
	std::cout << "   msg length:  " << length << std::endl;
#endif
	frame->message = new unsigned char [length];
	for (int j = 0; j < length;j ++) {
		frame->message[j] = 0;
	}
	for (int j = 0; j < length; j++) {
#if DEBUG_ME
		std::cout << "    byte: " << j+i << std::endl;
#endif
		unsigned char tmp = evt->event_data[(j+i)];
		frame->message[j]=tmp; //copy to a local buffer for processing */
#if DEBUG_ME
		std::cout << "    frame->message: " << (int)frame->message[j] << std::endl;
		std::cout << "              data? " << (int)tmp << std::endl;
#endif 
	}
#if DEBUG_ME
	std::cout << "    Loaded Message" << std::endl;
#endif
	frame->CheckForErrors(); //check for header errors
#if DEBUG_ME
	std::cout << "    Checked for Errors, going to DecodeHeader" << std::endl;
#endif
	frame->DecodeHeader(); //find feb number in header
#if DEBUG_ME
	std::cout << "  Done Decoding the Buffer" << std::endl;
	//Need to set initialized for FPGA's...//frame->DecodeRegisterValues(length);
#endif
};

#endif
