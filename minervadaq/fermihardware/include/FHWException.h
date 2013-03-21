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
        int crateNumber, 
        FrameTypes::FEBAddresses febAddress, 
        unsigned int channelAddress, 
        std::string theMessage );

    FHWException( 
        int crateNumber, 
        VMEModuleTypes::VMECommunicatorType vmeType,
        unsigned int vmeAddress, 
        std::string theMessage );

    virtual ~FHWException() throw() {};

    const char * what();

  private:
    void constructorHelper();
    std::string message;
};

#endif
