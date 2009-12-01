#ifndef channels_cpp
#define channels_cpp

#include "channels.h"

/*********************************************************************************
 * Class for creating Chain Read-Out Controller channel objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * April 22, 2009
 *
 **********************************************************************************/

channels::channels(unsigned int a, int b) {
  /*! \fn ********************************************************************************
 * constructor takes the following arguments:
 * \param a:  The channel base address 
 * \param b:  The channel number
 *********************************************************************************/
  channelBaseAddress = a; //the address for the croc which contains this channel
  channelNumber = b; //the channel number (0-3) there are 4 and only 4 channels
                     //per croc board in the current configuration
  channelDirectAddress = channelBaseAddress + 
     0x4000 * (unsigned int)(channelNumber);
     //Set the channel's address; 
     //    I'm not entirely sure where 0x4000 comes from, but there you have it!
  FIFOMaxSize = 2048; // bytes; largest number of bytes the FIFO buffer can hold
  MemoryMaxSize = 6144; // bytes;  largest number of bytes the DPM Memory can hold
  crocRegisters registerOffset = crocInput;
  fifoAddress = channelDirectAddress + (unsigned int)registerOffset; //FIFO address
  registerOffset = crocMemory;
  dpmAddress = channelDirectAddress + (unsigned int)registerOffset; //DPM Address
  registerOffset = crocSendMessage;
  sendMessageAddress = channelDirectAddress + (unsigned int)registerOffset; //Send message register
  registerOffset = crocStatus;
  statusAddress = channelDirectAddress + (unsigned int)registerOffset; //status register
  registerOffset = crocDPMPointer;
  dpmPointerAddress = channelDirectAddress + (unsigned int)registerOffset; //DPM Pointer register
  registerOffset = crocClearStatus;
  clearStatusAddress = channelDirectAddress + (unsigned int)registerOffset; //clear status register

  bltAddressModifier = cvA24_U_BLT; //the Block Transfer Reads (BLT's) require a special address modifier

  channelStatus = 0; //the channel starts out with no status information kept
  has_febs=false; //and no feb's loaded
  std::string filename;
  std::stringstream channel_no;
  channel_no<<channelDirectAddress;
  filename = "channel_"+channel_no.str();
  log_file.open(filename.c_str());

}

void channels::SetFEBs(int a) {
  /*! \fn********************************************************************************
 * This function loads FEB's belonging to this channel into a vector of febs once
 * the feb has been found
 * \param a the FEB number
 *********************************************************************************/
  //if we found this feb on this channel, put it into the list 
  febs.push_back(new feb(1,false,(febAddresses)a,54,log_file)); 
  //febs.push_back(new feb(1,false,(febAddresses)a,54)); 
  return;
}

feb *channels::MakeTrialFEB(int a) {
  /*! \fn ********************************************************************************
 * This function makes up an feb to try to load into this channel's list
 * The feb has address a, passed as an integer
 * Additionally, the number of 1-byte registers in the FPGA firmware is required.
 * \param a the FEB number
 *********************************************************************************/
  febAddresses f = (febAddresses)a; //store the trial feb address
  #if v65
    // feb *trialFeb = new feb(1, false, f, 42, log_file); //make up the trial feb
    feb *trialFeb = new feb(1, false, f, 42); //make up the trial feb
  #else
     feb *trialFeb = new feb(1, false, f, 54, log_file); //make up the trial feb
    //feb *trialFeb = new feb(1, false, f, 54); //make up the trial feb
  #endif
  trialFeb->SetFEBDefaultValues(); //set up the default values
  return trialFeb;
}

int channels::DecodeStatusMessage() {
  /*! \fn ********************************************************************************
 * This function decodes the status message for this channel.
 *********************************************************************************/
  StatusBits checkValue = MessageSent; //a mask to check if the message was send
  bool error = (channelStatus & checkValue)!=0; //bit should be high
  try {
  #if DEBUG_FEB
    log_file<<"Message Sent? "<<error<<std::endl; //success!
  #endif
    if (!error) throw error;
  } catch (bool e) {
    log_file<<"Message was not sent."<<std::endl;
    return -103; //if the message was not send, stop execution
  }
  checkValue = MessageReceived;
  error = (channelStatus & checkValue)!=0; //bit should be high
  try {
  #if DEBUG_FEB
    log_file<<"Message Received? "<<error<<std::endl; //success!
  #endif
    if (!error) throw error;
  } catch (bool e) {
    log_file<<"Message was not received."<<std::endl;
    return -104; //if the message was not received, stop execution
  }
  checkValue = CRCError;
  error = (channelStatus & checkValue)==0; //bit should be low
  try  {
  #if DEBUG_FEB
    log_file<<"CRC Error? "<<error<<std::endl; //success!
  #endif
    if (!error) throw error;
  } catch (bool e) {
    log_file<<"CRC Error."<<std::endl;
    exit(-105); //if the CRC error bit was set, the there's a hardware/message fault and the 
                //execution should be stopped
  }
  checkValue = TimeoutError;
  error = (channelStatus & checkValue)==0; //bit should be low
  try  {
  #if DEBUG_FEB
    log_file<<"Timeout Error? "<<error<<std::endl; //success!
  #endif
    if (!error) throw error;
  } catch (bool e) {
    log_file<<"Timeout Error."<<std::endl;
    exit(-106); //stop execution if a timeout occured in passing messages
  }
  checkValue = FIFONotEmpty;
  error = (channelStatus & checkValue)==0; //Check FIFO buffer status; bit should be low
  #if DEBUG_FEB
    log_file<<"FIFO Empty? "<<!error<<std::endl;
  #endif
  checkValue = FIFOFull;
  error = (channelStatus & checkValue)==0; //Check FIFO buffer status; bit should be low
  #if DEBUG_FEB
    log_file<<"FIFO Full? "<<error<<std::endl;
  #endif
  checkValue = DPMFull;
  error = (channelStatus & checkValue)==0; //Check DPM status; bit should be low
  #if DEBUG_FEB
    log_file<<"DPM Full? "<<!error<<std::endl;
  #endif
  return 0;
}

void channels::SetBuffer(unsigned char *b) {
  /*! \fn 
 * Puts data into the data buffer assigned to this channel.
 * \param b the data buffer
 */

  #if DEBUG_FEB
    log_file<<"Setting Buffer"<<std::endl;
  #endif
  buffer = new unsigned char [(int)dpmPointer];
  for (int i=0;i<(int)dpmPointer;i++) {
    buffer[i]=b[i];
  #if DEBUG_FEB
    log_file<<"SetBuffer: "<<buffer[i]<<" i: "<<i<<std::endl;
  #endif
  }
  #if DEBUG_FEB
    log_file<<"Done with SetBuffer...Returning"<<std::endl;
  #endif
  return; 
}
#endif
