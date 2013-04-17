#ifndef EventHandler_cpp
#define EventHandler_cpp
/*! \file EventHandler.cpp
*/

#include <string>
#include <sstream>
#include <iomanip>

#include "EventHandler.h"

const char* EventHandler::dataAsCString() const
{
  std::stringstream ss;
  ss << std::endl;
  ss << "Total Data Length = " << this->dataLength << std::endl;
  for (unsigned short i = 0; i < this->dataLength; i+=2) {
    unsigned short j = i + 1;
    ss
      << std::setfill('0') << std::setw( 2 ) << std::hex << (int)this->data[i] << " " 
      << std::setfill('0') << std::setw( 2 ) << std::hex << (int)this->data[j] << " " 
      << "\t" 
      << std::setfill('0') << std::setw( 4 ) << std::dec << i << " " 
      << std::setfill('0') << std::setw( 4 ) << std::dec << j
      << std::endl;
  }
  std::string result = ss.str();
  return result.c_str();
}

#endif
