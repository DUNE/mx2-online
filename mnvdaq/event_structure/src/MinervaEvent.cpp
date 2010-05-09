#ifndef MinervaEvent_cxx
#define MinervaEvent_cxx

#include "MinervaEvent.h"
#include "MinervaEvent_templates.h"

/**************************MinervaHeader Class*******************************************/

MinervaHeader::MinervaHeader(int crateID, int crocID, int chanID, 
                             int bank, int feb_no, int firmware, int hit, int length) {
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
    std::cout<<"crateID: "<<crateID<<std::endl;
    std::cout<<"crocID: "<<crocID<<std::endl;
    std::cout<<"chanID: "<<chanID<<std::endl;
    std::cout<<"bank: "<<bank<<std::endl;
    std::cout<<"feb_number: "<<feb_no<<std::endl;
    std::cout<<"firmware: "<<firmware<<std::endl;
    std::cout<<"hit: "<<hit<<std::endl;
    std::cout<<"length: "<<length<<std::endl;
  #endif

  int magic_pattern = 0;
  //whatever it is we need to do to get the magic pattern
  data_bank_header[0] =  magic_pattern; //put the magic pattern for this event into the header
  data_bank_header[1] = length; //put the buffer length into this event header
  data_bank_header[2] = ((firmware) << 0x08) | (bank&0xFF); //load up the firmware version for the feb
  data_bank_header[3] = source_id; //and the source information

  chan_number = (source_id & 0xFF8)>>0x07; //register the "feb number"
}

MinervaHeader::MinervaHeader(unsigned char crate) {
  /*! \fn 
 *
 * Makes data header for the End-of-Event Record (DAQ header)
 *
 */
  unsigned short source_id = crate; //2 bits for the crate id number
  unsigned int magic_pattern = 0xCDCD; //right?
  //whatever it is we need to do to get the magic pattern

  DAQ_event_header[0] =  magic_pattern; //put the magic pattern for this event into the header
  DAQ_event_header[1] = 48; //the length in bytes of the DAQ event header
  DAQ_event_header[2] = 0xFFFF; //load up the firmware version for the feb
  DAQ_event_header[2] |= (3 & 0xFF)<<0x10; //put in the bank type 
  DAQ_event_header[3] = source_id; //and the source information
}


/*****************MinervaEvent Class******************************************************/ 

MinervaEvent::MinervaEvent(int det, int config, int run, int sub_run, int trig, 
                           unsigned int g_gate,unsigned int gate,unsigned long trig_time, 
                           unsigned short error, unsigned int minos, MinervaHeader *header) {


  /*! \fn 
 *
 * Constructor for MinervaEvent event model data block
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
 *
 */

  int buffer_index = 0;
  unsigned int event_info_block[12]; //piece up the event information

  event_info_block[0] = det & 0xFF;
  event_info_block[0] |= 0 <<0x08; //a reserved byte
  event_info_block[0] |= (config & 0xFFFF)<<0x10;

  event_info_block[1] = run & 0xFFFFFFFF;
  event_info_block[2] = sub_run & 0xFFFFFFFF;
  event_info_block[3] = trig & 0xFFFFFFFF;
  event_info_block[4] = g_gate & 0xFFFFFFFF; //the "global gate"
  event_info_block[5] = 0xFFFFFFFF; //This is the extra, unused 4 bytes of the global gate number
  event_info_block[6] = gate & 0xFFFFFFFF; //the gate number
  event_info_block[7] = 0xFFFFFFFF; //the extra 4 bytes we don't use
  event_info_block[8] = trig_time & 0xFFFFFFFF; //the gate time
  event_info_block[9] = 0xFFFFFFFF; //the extra 4 bytes
  event_info_block[10] =  error & 0xFFFF; //the error bytes
  event_info_block[10] |= 0<<0x10; //2 reserved bytes
  event_info_block[11] = minos & 0xFFFFFFFF; //the minos gate

                                           //
  
  for (int i=0;i<12;i++) {
    buffer_index=i+8; //where should we store this data?  We need to allow room for the event 
                          //header we haven't added yet
    event_block[buffer_index]=event_info_block[i]&0xFF;
    event_block[buffer_index+1]=event_info_block[i]&0xFF00;
    event_block[buffer_index+2]=event_info_block[i]&0xFF0000;
    event_block[buffer_index+3]=event_info_block[i]&0xFF000000;
  }

  unsigned short *tmpDAQHeader = header->GetDAQEvtHeader();
  buffer_index=0; 
  for (int i=0;i<4;i++) {
    event_block[buffer_index]=tmpDAQHeader[i]&0xFF;
    buffer_index++;
    event_block[buffer_index]=(tmpDAQHeader[i]&0xFF00)>>0x08;
    buffer_index++;
  }
  //InsertData(event_block);
}

/*template <class X> void MinervaEvent::MakeDataBlock(X *frame, MinervaHeader *header) { //build the event block
   unsigned short *bank_header = header->GetDataBankHeader();
   int bank = (int)(bank_header[3] & 0xFF); //get the data bank type from the header
   int buffer_size = -1;
   switch (bank) {
     case 0: //ADC Buffer
       buffer_size = FEB_HITS_SIZE; 
       break;
     case 1: //DISC Buffer
       buffer_size = FEB_DISC_SIZE; 
       break;
     case 2: //FEB Buffer
       buffer_size = FEB_INFO_SIZE; 
       break;
     case 3: 
       std::cout<<"Should not have sent a DAQ bank here!"<<std::endl;
       exit (-1);
   }

   unsigned char *data_block = new unsigned char [buffer_size]; //make up the temp buffer to hold the header & data in 
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
   }
   InsertData(data_block); //insert the data into the event buffer
} */

/*void MinervaEvent::InsertData(unsigned char *insertBuffer) {
  boost::mutex::scoped_lock lock(mutex);
  int bank = -1;
  int bytes = -1;
  int hits = -1;
  bank = (int)insertBuffer[4]&0xFF; //get the bank type from the buffer
  bytes = (int)((insertBuffer[2]&0xFF) | (insertBuffer[3]&0xFF)) + 8; //get the length of the buffer (8 is the number of bytes

  //figure out which FEB this data is from

  int chan_id = (int) ((insertBuffer[5] | (insertBuffer[6]<<0x08))&&0xFF8)>>0x07;
  int feb_number = (int) ((insertBuffer[6] &0x78)>>0x03);

  //which hit is this
  hits = (int)(insertBuffer[6]&0x07);


#if DEBUG_ME
  std::cout<<"----------InsertData--------"<<std::endl;
  std::cout<<"chan_id: "<<chan_id<<std::endl;
  std::cout<<"bank: "<<bank<<std::endl;
  std::cout<<"bytes: "<<bytes<<std::endl;
  std::cout<<"feb_number: "<<feb_number<<std::endl;
#endif

  //where, oh were do we put all this data!
  int start_byte = (chan_id - MIN_CHAN_ID)*CHAIN_OFFSET; //where do we start
  start_byte *= (feb_number - FEB_MIN_NUMBER); //locate the FEB block
  switch (bank) {
    case 0: //the ADC data
      if (hits) { //with DISC info
        start_byte += FEB_INFO_SIZE+FEB_DISC_SIZE+(hits-1)*FEB_HITS_SIZE;
      } else { //without DISC info
        start_byte += FEB_INFO_SIZE+FEB_DISC_SIZE;
      }
      for (int i=start_byte;i<(start_byte+FEB_HITS_SIZE);i++) {
        buffer[i]=insertBuffer[i-start_byte];
      } 
      break;
    case 1: //the discriminator data
      start_byte += FEB_INFO_SIZE;
      for (int i=start_byte;i<(start_byte+FEB_DISC_SIZE);i++) {
        buffer[i]=insertBuffer[i-start_byte];
      } 
      break;
    case 2: //the FEB info 
      for (int i=start_byte;i<(start_byte+FEB_INFO_SIZE);i++) {
        buffer[i]=insertBuffer[i-start_byte];
      } 
      break;
    case 3: //the DAQ-Run information per event
      //put in the DAQ Run header at the end of the event
      //This should start at MAX_BUFFER_SIZE-bytes
      {int buffer_index = MAX_BUFFER_SIZE-DAQ_HEADER-1; //minus 1 for count start at zero
      for (int i=buffer_index;i<MAX_BUFFER_SIZE;i++) {
        buffer[i]=insertBuffer[i-buffer_index]; //put the bytes into the buffer
      } }
      break;
    default:
      std::cout<<"Really, Now what!?"<<std::endl;
      std::cout<<"We were unable to write data to the event buffer."<<std::endl;
      std::cout<<"The BANK TYPE is: "<<bank<<std::endl;
      std::cout<<"You really need to call someone to help you..."<<std::endl;
      exit(-500); //this really shouldn't happen and we need to stop & get someone's attention if it did
  }
  delete [] insertBuffer; //clean up memory
} */

/*void MinervaEvent::ResetEvent() {
  for (int i=0;i<MAX_BUFFER_SIZE;i++) {
    buffer[i]=0;
  }
}  */

#endif
