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
    int theCrateNumber, 
    FrameTypes::FEBAddresses theFebAddress, 
    unsigned int channelAddress, 
    std::string theMessage ) :
  message(theMessage),
  crateNumber(theCrateNumber),
  febAddress(theFebAddress),
  vmeType(VMEModuleTypes::UnknownCommunicator),
  address(channelAddress)
{
  constructorHelper();
  excpLog.errorStream() << "FHWException for crate " << crateNumber << 
    "; FEB Address = " << febAddress << "; channel Address = 0x" << std::hex <<
    address;
}

//-----------------------------
FHWException::FHWException( 
    int theCrateNumber, 
    VMEModuleTypes::VMECommunicatorType theVmeType,
    unsigned int vmeAddress, 
    std::string theMessage ) :
  message(theMessage),
  crateNumber(theCrateNumber),
  febAddress(FrameTypes::febAll),
  vmeType(theVmeType),
  address(vmeAddress)
{
  constructorHelper();
  excpLog.errorStream() << "FHWException for crate " << crateNumber << 
    "; VME Module Type = " << vmeType << "; VME Address = 0x" << std::hex <<
    address;
}

//-----------------------------
void FHWException::constructorHelper()
{
  excpLog.setPriority(log4cpp::Priority::INFO);  
  excpLog.errorStream() << "Exception Message: " << message;
}

//-----------------------------
const char * FHWException::what()
{ 
  return message.c_str();
}

//-----------------------------
int FHWException::getCrate() const
{
  return crateNumber;
}

//-----------------------------
FrameTypes::FEBAddresses FHWException::getFEBAddress() const
{
  return febAddress;
}

//-----------------------------
VMEModuleTypes::VMECommunicatorType FHWException::getVMECommunicatorType() const
{
  return vmeType;
}

//-----------------------------
unsigned int FHWException::getVMEAddress() const
{
  return address;
}

#endif
