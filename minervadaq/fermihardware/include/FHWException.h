#ifndef FHWException_h
#define FHWException_h
/*! \file FHWException.h 
*/

#include <exception>
#include <string>

#include "FrameTypes.h"
#include "VMEModuleTypes.h"

/*! 
  \class FHWException
  \brief Fermi Hardware Exception is a Minerva DAQ specific exception.
  \author Gabriel Perdue
  */

class FHWException : public std::exception
{
  public:
    FHWException();
    FHWException( std::string theMessage );
    FHWException( 
        int theCrateNumber, 
        FrameTypes::FEBAddresses theFebAddress, 
        unsigned int channelAddress, 
        std::string theMessage );

    FHWException( 
        int theCrateNumber, 
        VMEModuleTypes::VMECommunicatorType theVmeType,
        unsigned int vmeAddress, 
        std::string theMessage );

    virtual ~FHWException() throw() {};

    const char * what();

    int getCrate() const;
    FrameTypes::FEBAddresses getFEBAddress() const;
    VMEModuleTypes::VMECommunicatorType getVMECommunicatorType() const;
    unsigned int getVMEAddress() const;

  private:
    void constructorHelper();
    std::string message;
    int crateNumber;
    FrameTypes::FEBAddresses febAddress;
    VMEModuleTypes::VMECommunicatorType vmeType;
    unsigned int address;
};

#endif
