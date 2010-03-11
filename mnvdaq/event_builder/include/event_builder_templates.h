#ifndef event_builder_templates_hh
#define event_builder_templates_hh

#include <iostream>
#include <fstream>

template <class X> MinervaHeader* BuildBankHeader(event_handler *evt, X *frame,std::ofstream &log_file) {
  /*! \fn 
 *
 * Templated function for building up the bank headers.
 *
 * \param event_handler *evt a copy of the event handler structure
 * \param X *frame the data frame
 * \param std::ofstream &log_file a logfile for debuggin output 
 *
 */
  int feb_number = frame->GetFEBNumber(); //get the feb number from which this frame came


  int index = -1; //the index which holds this feb's firmware
  int length = 0;

  //now we've got everything we need to make up the event headers
  MinervaHeader *tmp_header; //declare a new data bank header
  if (evt->feb_info[4]==3) {
    std::cout<<"Should not have passed DAQ block to BuildBlockHeader"<<std::endl;
    exit (-1);
  } else {
    switch (evt->feb_info[4]) {
      case 0:
        length = FEB_HITS_SIZE-8;
        break;
      case 1:
        length = FEB_DISC_SIZE-8;
        break;
      case 2:
        length = FEB_INFO_SIZE-8;
        break;
      default:
        std::cout<<"Something went desirately wrong in BuildBankHeader"<<std::endl;
        exit(-1);
    }

    #if DEBUG_ME
      log_file<<"--------Event Builder--------"<<std::endl;
      log_file<<"crateID: "<<evt->feb_info[1]<<std::endl;
      log_file<<"crocID: "<<evt->feb_info[2]<<std::endl;
      log_file<<"chanID: "<<evt->feb_info[3]<<std::endl;
      log_file<<"bank: "<<evt->feb_info[4]<<std::endl;
      log_file<<"feb_number (from frame header): "<<feb_number<<std::endl;
      log_file<<"firmware: "<<evt->feb_info[7]<<std::endl;
      log_file<<"hit: "<<evt->feb_info[h]<<std::endl;
      log_file<<"length: "<<length<<std::endl;
    #endif
    tmp_header = new MinervaHeader(evt->feb_info[1], evt->feb_info[2], evt->feb_info[3],
                                   evt->feb_info[4], feb_number, evt->feb_info[7],
                                   evt->feb_info[8],length); //make up a regular data
                                                             //block header
    /*if (evt->feb_info[4]==1) {
        evt->hits_per_feb[index]=frame->DecodeDisc(); //return the number of hits to the client
    } */
  }
  return tmp_header; //return the header
};


template <class X> void DecodeBuffer(event_handler *evt, X *frame, int i, int length,std::ofstream &log_file) {

  /*! \fn
 *
 * A templated function for decoding a data buffer
 *
 * \param event_handler *evt a pointer to the event handler structure
 * \param X *frame the data frame
 * \param int i byte offset
 * \param int length the message length 
 * \param std::ofstream &log_file debugging log file
 */

   #if DEBUG_ME
      log_file<<"DecodeBuffer Parameters: "<<std::endl;
      log_file<<"i: "<<i<<std::endl;
      log_file<<"length: "<<length<<std::endl;
   #endif
  frame->message = new unsigned char [length];
  for (int j=0;j<length;j++) {
   frame->message[j]=0;
  }
  for (int j=0;j<length;j++) {
    #if DEBUG_ME
      log_file<<"byte: "<<j+i<<std::endl;
    #endif
    unsigned char tmp = evt->event_data[(j+i)];
    frame->message[j]=tmp; //copy to a local buffer for processing */
    #if DEBUG_ME
        log_file<<"frame->message: "<<(int)frame->message[j]<<std::endl;
        log_file<<"data? "<<(int)tmp<<std::endl;
    #endif 
  }
  #if DEBUG_ME
    log_file<<"Loaded Message"<<std::endl;
  #endif
  frame->CheckForErrors(); //check for header errors
  #if DEBUG_ME
    log_file<<"Checked for Errors, going to DecodeHeader"<<std::endl;
  #endif
  frame->DecodeHeader(); //find feb number in header
  #if DEBUG_ME
    log_file<<"Done Decoding the Buffer"<<std::endl;
    frame->DecodeRegisterValues(length);
  #endif
};

#endif
