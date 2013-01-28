#ifndef VMECommunicator_cpp
#define VMECommunicator_cpp

#include "VMECommunicator.h"
#include "exit_codes.h"

log4cpp::Category& commLog = log4cpp::Category::getInstance(std::string("comm"));

VMECommunicator::VMECommunicator( unsigned int address, log4cpp::Appender* appender, const Controller* controller )
{
  this->controller = controller;
  if( NULL == this->controller ) {
    std::cout << "Crate Controller is NULL in VMECommunicator::VMECommunicator!" << std::endl;
    exit(EXIT_CROC_UNSPECIFIED_ERROR);
  }
  controllerHandle = this->controller->GetHandle();
  this->address    = address;
  commAppender     = appender;
  if ( commAppender == 0 ) {
    std::cout << "VMECommunicator Log Appender is NULL in VMECommunicator::VMECommunicator!" << std::endl;
    exit(EXIT_CROC_UNSPECIFIED_ERROR);
  }

	this->addressModifier     = cvA32_U_DATA;
	this->bltAddressModifier  = cvA32_U_BLT;
	this->dataWidth           = cvD32;  
	this->dataWidthSwapped    = cvD32_swapped;
	this->dataWidthReg        = cvD16;  
	this->dataWidthSwappedReg = cvD16_swapped;
}

VMECommunicator::~VMECommunicator()
{
  this->controller = NULL;
}

const Controller* VMECommunicator::GetController() const
{
  return this->controller;
}

int VMECommunicator::WriteCycle(int ml, unsigned char *send_message, unsigned int address, 
    CVAddressModifier AM, CVDataWidth DW) 
{
  /*!
   * \fn int VMECommunicator::WriteCycle(int ml, unsigned char *send_message,  unsigned int address,
   *                          CVAddressModifier AM, CVDataWidth DW)
   *
   *  Performs a single write cycle of 2 bytes per write to the VME.
   *
   *  \param ml an integer; the message length
   *  \param *send_message a pointer of unsigned chars with the data to be sent over the VME
   *  \param address unsigned int, the VME address 
   *  \param AM CVAddressModifier, the address length for each message
   *  \param DW CVDataWidth, the number of bits sent per write
   *
   *  Returns the error code for the VME cycle.
   */
  unsigned short send_data;
  int error; 

  for (int k=0;k<ml;k+=2) {
    send_data = send_message[k];
    if ((k+1)==ml) {
      send_data |= 0<<0x08;
    } else { 
      send_data |= send_message[k+1]<<0x08;
    }
    do {
      error = CAENVME_WriteCycle(controllerHandle, address, &send_data, AM, DW); 
    } while (
        (error<0) && ((error!=-1)||(error!=-4))
        ); //check to make sure the message was sent.
    //if the message wasn't sent but the error was not a bus error (-1) or a parameter error (-4)
    //keep trying until it's successful.  It either timed out, or had an unspecified error
  }
  return error;
}


int VMECommunicator::ReadCycle(unsigned char *received_message, unsigned int address, 
    CVAddressModifier AM, CVDataWidth DW) 
{
  /*!
   * \fn int VMECommunicator::ReadCycle(unsigned char *received_message,  
   *                            unsigned int address, CVAddressModifier AM, CVDataWidth DW)
   *
   *  Performs a single read cycle from the VME.
   *
   *  \param *receive_message a pointer of unsigned chars with the data to be sent over the VME
   *  \param address unsigned int, the VME address 
   *  \param AM CVAddressModifier, the address length for each message
   *  \param DW CVDataWidth, the number of bits sent per read
   *
   *  Returns the error code for the VME cycle.
   */
  int error; //VME error status
  error = CAENVME_ReadCycle(controllerHandle, address, received_message, AM,DW);
  return error;
}


int VMECommunicator::ReadBLT(unsigned char *received_message, int blocks, unsigned int address, 
    CVAddressModifier AM, CVDataWidth DW) {
  /*!
   * \fn int VMECommunicator::ReadBLT(unsigned char *received_message,  
   *                            unsigned int address, CVAddressModifier AM, CVDataWidth DW)
   *
   *  Performs a block read cycle from the VME.
   *
   *  \param *receive_message a pointer of unsigned chars with the data to be sent over the VME
   *  \param blocks the length of the incoming message
   *  \param address unsigned int, the VME address 
   *  \param AM CVAddressModifier, the address length for each message
   *  \param DW CVDataWidth, the number of bits sent per read
   *
   *  Returns the error code for the VME cycle.
   */
  int count=-1; //counter for number of blocks read off
  int error; 
  error = CAENVME_BLTReadCycle(controllerHandle,address, received_message, blocks, AM, DW, &count);
  return error;
}


int VMECommunicator::WriteFIFOBLT(int ml, unsigned char *send_message, unsigned int address, 
    CVAddressModifier AM, CVDataWidth DW) 
{
  /*!
   * \fn int VMECommunicator::WriteFIFOBLT(int ml, unsigned char *send_message,  unsigned int address,
   *                          CVAddressModifier AM, CVDataWidth DW)
   *
   *  Performs a FIFO block write cycle to the VME.
   *
   *  \param ml an integer; the message length
   *  \param *send_message a pointer of unsigned chars with the data to be sent over the VME
   *  \param address unsigned int, the VME address 
   *  \param AM CVAddressModifier, the address length for each message
   *  \param DW CVDataWidth, the number of bits sent per write
   *
   *  Returns the error code for the VME cycle.
   */
  int count=-1;
  int error; //VME error status
  do {
    error = CAENVME_FIFOBLTWriteCycle(controllerHandle, address, send_message, ml,  
        AM, DW, &count);   
  } while (
      (error<0) && ((error!=-1)||(error!=-4))
      ); //check to make sure the message was sent.
  //if the message wasn't sent but the error was not a bus error (-1) or a parameter error (-4)
  //keep trying until it's successful.  It either timed out, or had an unspecified error
  return error;
}

void  VMECommunicator::exitIfError( int error, const std::string& msg ) 
{
  if (error) {
    commLog.fatalStream() << msg;
    this->GetController()->ReportError(error);
    exit(error);
  }
}

#endif
