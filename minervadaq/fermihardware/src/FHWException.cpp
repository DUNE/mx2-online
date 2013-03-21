#ifndef FHWException_cpp
#define FHWException_cpp
/*! \file FHWException.cpp
*/

#include <sstream>

#include "log4cppHeaders.h"
#include "FHWException.h"

log4cpp::Category& excpLog = log4cpp::Category::getInstance(std::string("excp"));

//-----------------------------
FHWException::FHWException() : 
  message("Fermi Harware Exception!")
{
  constructorHelper();
}

//-----------------------------
FHWException::FHWException( std::string theMessage ) : 
  message(theMessage)
{
  constructorHelper();
} 

//-----------------------------
FHWException::FHWException( 
    int crateNumber, 
    FrameTypes::FEBAddresses febAddress, 
    unsigned int channelAddress, 
    std::string theMessage ) :
  message(theMessage)
{
  constructorHelper();
  excpLog.infoStream() << "FHWException for crate " << crateNumber << 
    "; FEB Address = " << febAddress << "; channel Address = 0x" << std::hex <<
    channelAddress;
}

//-----------------------------
FHWException::FHWException( 
    int crateNumber, 
    VMEModuleTypes::VMECommunicatorType vmeType,
    unsigned int vmeAddress, 
    std::string theMessage ) :
  message(theMessage)
{
  constructorHelper();
  excpLog.infoStream() << "FHWException for crate " << crateNumber << 
    "; VME Module Type = " << vmeType << "; VME Address = 0x" << std::hex <<
    vmeAddress;
}

//-----------------------------
void FHWException::constructorHelper()
{
  excpLog.setPriority(log4cpp::Priority::INFO);  
  excpLog.infoStream() << "Exception Message: " << message;
}

//-----------------------------
const char * FHWException::what() 
{ 
  return message.c_str();
}

#endif
