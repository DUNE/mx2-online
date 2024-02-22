#ifndef VMECommunicator_cpp
#define VMECommunicator_cpp
/*! \file VMECommunicator.cpp
*/

#include "FHWException.h"
#include "VMECommunicator.h"
#include "exit_codes.h"

log4cpp::Category& commLog = log4cpp::Category::getInstance(std::string("comm"));

//-----------------------------
VMECommunicator::VMECommunicator( unsigned int theAddress, 
    const Controller* theController ) : 
  controller(theController),
  commType(VMEModuleTypes::UnknownCommunicator),
  address(theAddress)
{
  if( NULL == this->controller ) {
    std::cout << "Crate Controller is NULL in VMECommunicator::VMECommunicator!" << std::endl;
    exit(EXIT_CROC_UNSPECIFIED_ERROR);
  }
  controllerHandle = this->controller->GetHandle();

	this->addressModifier     = cvA32_U_DATA;
	this->bltAddressModifier  = cvA32_U_BLT;
	this->dataWidth           = cvD32;  
	this->dataWidthSwapped    = cvD32_swapped;
	this->dataWidthReg        = cvD16;  
	this->dataWidthSwappedReg = cvD16_swapped;
/*  commLog.setPriority(log4cpp::Priority::NOTICE);  */
#ifdef GOFAST
  commLog.setPriority(log4cpp::Priority::INFO);
#else
  commLog.setPriority(log4cpp::Priority::DEBUG);
#endif

}

//-----------------------------
VMECommunicator::~VMECommunicator()
{
  this->controller = NULL;
}

//-----------------------------
unsigned int VMECommunicator::GetAddress() const
{
  return this->address;
}

//-----------------------------
const Controller* VMECommunicator::GetController() const
{
  return this->controller;
}

//-----------------------------
//! Performs a single write cycle of 2 bytes per write to the VME.
/*!
  \param ml           the message length
  \param send_message pointer of unsigned chars to the data to be sent over the VME
  \param address      the VME address 
  \param AM           the address length for each message
  \param DW           the number of bits sent per write
  */
int VMECommunicator::WriteCycle(int ml, unsigned char *send_message, unsigned int address, 
    CVAddressModifier AM, CVDataWidth DW) const
{
  unsigned short send_data;
  int error(0); 

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
        ); 
    // If the message wasn't sent but the error was not a bus error (-1) or a parameter error (-4)
    // keep trying until it's successful.  It either timed out, or had an unspecified error
  }
  return error;
}


//-----------------------------
//! Performs a single read cycle from the VME.
/*!
  \param received_message a pointer of unsigned chars to the data to be sent over the VME
  \param address          the VME address 
  \param AM               the address length for each message
  \param DW               the number of bits sent per read
  */
int VMECommunicator::ReadCycle(unsigned char *received_message, unsigned int address, 
    CVAddressModifier AM, CVDataWidth DW) const
{
  int error; 
  error = CAENVME_ReadCycle(controllerHandle, address, received_message, AM, DW);
  return error;
}


//-----------------------------
//! Performs a block read cycle from the VME.
/*!
  \param received_message a pointer of unsigned chars to the data to be sent over the VME
  \param blocks           the length of the incoming message
  \param address          the VME address 
  \param AM               the address length for each message
  \param DW               the number of bits sent per read

  The data width must be 32. Therfore, we must read a number of bytes such that n%4=0.
  */
int VMECommunicator::ReadBLT(unsigned char *received_message, int blocks, unsigned int address, 
    CVAddressModifier AM, CVDataWidth DW) const 
{
  int count(-1); 
  int error(0); 
  int offset = (blocks % 4);
  if (0 != offset) {
    blocks += (4 - offset);
  }
  commLog.debugStream() << "Execute BLT Read: bytes requested = " << blocks;
  error = CAENVME_BLTReadCycle(controllerHandle,address, received_message, blocks, AM, DW, &count);
  commLog.debugStream() << "bytes received = " << count << ": error status =" << error;
  return error;
}


//-----------------------------
//! Performs a FIFO block write cycle to the VME.
/*!
  \param ml           the message length
  \param send_message a pointer of unsigned chars to the data to be sent over the VME
  \param address      the VME address 
  \param AM           the address length for each message
  \param DW           the number of bits sent per write
  */
int VMECommunicator::WriteFIFOBLT(int ml, unsigned char *send_message, unsigned int address, 
    CVAddressModifier AM, CVDataWidth DW) const
{
  int count(-1);
  int error(0); //VME error status
  do {
    error = CAENVME_FIFOBLTWriteCycle(controllerHandle, address, send_message, ml,  
        AM, DW, &count);   
  } while (
      (error<0) && ((error!=-1)||(error!=-4))
      ); 
  // If the message wasn't sent but the error was not a bus error (-1) or a parameter error (-4)
  // keep trying until it's successful.  It either timed out, or had an unspecified error.
  return error;
}

//-----------------------------
VMEModuleTypes::VMECommunicatorType VMECommunicator::GetCommType() const
{
  return this->commType;
}

//-----------------------------
int VMECommunicator::GetCrateNumber() const
{
  return this->GetController()->GetCrateNumber();
}

//-----------------------------
void VMECommunicator::VMEThrow( std::string msg ) const
{
  throw FHWException( 
      this->GetCrateNumber(), 
      this->GetCommType(), 
      this->GetAddress(),
      msg );
}

//-----------------------------
void VMECommunicator::throwIfError( int error, const std::string& msg ) const
{
  if (error) {
    std::stringstream ss;
    ss << "Fatal error for device " << this;
    ss << "; ";
    ss << msg;
    ss << this->GetController()->ReportError(error);
    commLog.fatalStream() << ss.str(); 
    VMEThrow( ss.str() );
  }
}

//-----------------------------
std::ostream& operator<<(std::ostream & s, VMEModuleTypes::VMECommunicatorType t) {
  switch (t) {
    case VMEModuleTypes::UnknownCommunicator : return s << "UnknownCommunicator";
    case VMEModuleTypes::CRIM                : return s << "CRIM";
    case VMEModuleTypes::CROC                : return s << "CROC";
    case VMEModuleTypes::Channels            : return s << "Channels";
    case VMEModuleTypes::ECROC               : return s << "ECROC";
    case VMEModuleTypes::EChannels           : return s << "EChannels";
    default : return s << "ERROR Invalid VMECommunicatorType : " << int(t);
  }
}

//-----------------------------
std::ostream& operator<<(std::ostream& out, const VMECommunicator& s)
{
  out << s.commType << "; Address = 0x" << std::hex << s.GetAddress();
  return out;
}



#endif
