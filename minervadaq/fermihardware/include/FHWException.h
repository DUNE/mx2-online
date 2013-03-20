#ifndef FHWException_h
#define FHWException_h
/*! \file FHWException.h 
*/

#include <exception>
#include <string>
#include <sstream>

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

    ~FHWException() throw() {};

    const char * what();

  private:
    std::string message;
};

#endif
