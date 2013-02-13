#ifndef DAQEventTemplates_hh
#define DAQEventTemplates_hh

/*! \fn
 *
 * Templated function for making up the MINERvA event model data block
 *
 * \param X *frame  a device frame containing data
 * \param MinervaHeader *header a MINERvA event block header
 */
template <class X> void DAQEvent::MakeDataBlock(X *frame, FrameHeader *header) 
{ 
	unsigned short *bank_header = header->GetBankHeader();
	int bankType = (int)(bank_header[2] & 0xFF); 
	int buffer_size = 8 + frame->message[0] + (frame->message[1]<<8) + 2; // MINERvA Header + Data + CRC   
	switch (bankType) {
		case 0: //ADC Buffer
			break;
		case 1: //DISC Buffer
			break;
		case 2: //FEB Buffer
			break;
		case 3: //DAQ Header
		case 4: //TRiPT Buffer
			exit (-1);
	}
	data_block = new unsigned char [buffer_size]; 
	int index = 0; 
	for (int i = 0; i < 4; i++) { 
		data_block[index] = bank_header[i] & 0xFF; 
		index++;
		data_block[index] = (bank_header[i] & 0xFF00) >> 0x08; 
		index++;
	}
	for (int i = 0; i < (buffer_size-8); i++) { 
		data_block[index] = frame->message[i];
		index++;
	} 
	delete [] frame->message;
}

#endif

