#include "acquire.h"
#include <iostream>

int acquire::WriteCycle(int handle, int ml, unsigned char *send_message,  unsigned int address, 
                         CVAddressModifier AM, CVDataWidth DW) {

/*!
 * \fn int acquire::WriteCycle(int handle, int ml, unsigned char *send_message,  unsigned int address,
 *                          CVAddressModifier AM, CVDataWidth DW)
 *
 *  Performs a single write cycle of 2 bytes per write to the VME.
 *
 *  \param handle an integer file descriptor of the VME 
 *  \param ml an integer; the message length
 *  \param *send_message a pointer of unsigned chars with the data to be sent over the VME
 *  \param address unsigned int, the VME address 
 *  \param AM CVAddressModifier, the address length for each message
 *  \param DW CVDataWidth, the number of bits sent per write
 *
 *  Returns the error code for the VME cycle.
 */

  /* function to send a message  to the requested address using the WriteCycle 
 * function */
  unsigned short send_data;
  int error; //VME error status
  
  for (int k=0;k<ml;k+=2) {
    send_data = send_message[k];
    if ((k+1)==ml) {
      send_data |= 0<<0x08;
    } else { 
      send_data |= send_message[k+1]<<0x08;
    }
    do {
      boost::mutex::scoped_lock lock(mutex); //only one thread at a time!
      error = CAENVME_WriteCycle(handle, address, &send_data, AM, DW); 
      lock.unlock();
    } while ((error<0)&&((error!=-1)||(error!=-4))); //check to make sure the message was sent.
           //if the message wasn't sent but the error was not a bus error (-1) or a parameter error (-4)
           //keep trying until it's successful.  It either timed out, or had an unspecified error
  }
  return error;
}

int acquire::ReadCycle(int handle, unsigned char *received_message,  unsigned int address, 
                         CVAddressModifier AM, CVDataWidth DW) {
/*!
 * \fn int acquire::ReadCycle(int handle, unsigned char *received_message,  
 *                            unsigned int address, CVAddressModifier AM, CVDataWidth DW)
 *
 *  Performs a single read cycle from the VME.
 *
 *  \param handle an integer file descriptor of the VME 
 *  \param *receive_message a pointer of unsigned chars with the data to be sent over the VME
 *  \param address unsigned int, the VME address 
 *  \param AM CVAddressModifier, the address length for each message
 *  \param DW CVDataWidth, the number of bits sent per read
 *
 *  Returns the error code for the VME cycle.
 */

  /* function to read a from a register on the croc/crim */
  boost::mutex::scoped_lock lock(mutex);  //only one thread at a time!
  int error; //VME error status
  error = CAENVME_ReadCycle(handle, address, received_message, AM,DW);
  return error;
}

int acquire::ReadBLT(int handle, unsigned char *received_message,  int blocks, unsigned int address, 
                         CVAddressModifier AM, CVDataWidth DW) {
/*!
 * \fn int acquire::ReadBLT(int handle, unsigned char *received_message,  
 *                            unsigned int address, CVAddressModifier AM, CVDataWidth DW)
 *
 *  Performs a block read cycle from the VME.
 *
 *  \param handle an integer file descriptor of the VME 
 *  \param *receive_message a pointer of unsigned chars with the data to be sent over the VME
 *  \param blocks the length of the incoming message
 *  \param address unsigned int, the VME address 
 *  \param AM CVAddressModifier, the address length for each message
 *  \param DW CVDataWidth, the number of bits sent per read
 *
 *  Returns the error code for the VME cycle.
 */

  /* function to read from the DPM Memeor on croc */
  boost::mutex::scoped_lock lock(mutex); //only one thread at a time!
  int count=-1; //counter for number of blocks read off
  int error; //VME error status
  error = CAENVME_BLTReadCycle(handle,address, received_message,blocks, AM, DW, &count);
  return error;
}

