#ifndef FHWException_cpp
#define FHWException_cpp
/*! \file FHWException.cpp
*/

#include "FHWException.h"

FHWException::FHWException() 
{
  message = "Fermi Harware Exception!";
}

FHWException::FHWException( std::string theMessage )
{
  message = theMessage;
} 

const char * FHWException::what() 
{ 
  return message.c_str();
}

#endif
