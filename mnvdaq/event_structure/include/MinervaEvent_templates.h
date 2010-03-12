#ifndef MinervaEvent_templates_hh
#define MinervaEvent_templates_hh

/*! \fn
 *
 * Templated function for making up the MINERvA event model data block
 *
 * \param X *frame  a device frame containing data
 * \param MinervaHeader *header a MINERvA event block header
 *
 */
template <class X> void MinervaEvent::MakeDataBlock(X *frame, MinervaHeader *header) 
{ 
	//build the event block
#if DEBUG_ME
	std::cout<<"Preparing to make DataBlock"<<std::endl;
#endif
	unsigned short *bank_header = header->GetDataBankHeader();
#if DEBUG_ME
	std::cout<<"Extracting Data Bank Header Complete"<<std::endl;
#endif
	int bank = (int)(bank_header[2] & 0xFF); //get the data bank type from the header
#if DEBUG_ME
	std::cout<<"bank: "<<bank<<std::endl;
#endif
	int buffer_size = -1;
	switch (bank) {
		case 0: //ADC Buffer
#if DEBUG_ME
			std::cout<<"Making ADC buffer"<<std::endl;
#endif
			buffer_size = FEB_HITS_SIZE;
			break;
		case 1: //DISC Buffer
#if DEBUG_ME
			std::cout<<"Making DISC buffer"<<std::endl;
#endif
			buffer_size = FEB_DISC_SIZE;
			break;
		case 2: //FEB Buffer
#if DEBUG_ME
			std::cout<<"Making FEB buffer"<<std::endl;
#endif
			buffer_size = FEB_INFO_SIZE;
			break;
		case 3:
			std::cout<<"Should not have sent a DAQ bank here!"<<std::endl;
			exit (-1);
	}

#if DEBUG_ME
	std::cout<<"buffer_size: "<<buffer_size<<std::endl;
#endif
	data_block = new unsigned char [buffer_size]; //make up the temp buffer to hold the header & data in
													//preparation for insertion
	int index = 0; //an internal indexing value
	for (int i=0;i<4;i++) { //place the header at the top of the bank
		data_block[index]=bank_header[i] & 0xFF; //the first byte
		index++;
		data_block[index] = (bank_header[i] & 0xFF00) >> 0x08; //the second byte
		index++;
	}
	for (int i=0;i<(buffer_size-8);i++) { //then put the data message in the data block
		data_block[index] = frame->message[i];
		index++;
	} 
	//   InsertData(data_block); //insert the data into the event buffer   
#if DEBUG_ME
	std::cout<<"Returning from MakeDataBlock"<<std::endl;
#endif
}

#endif

