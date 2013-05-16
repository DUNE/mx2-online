#ifndef EventHandler_cpp
#define EventHandler_cpp
/*! \file EventHandler.cpp
*/

#include <string>
#include <sstream>
#include <iomanip>

#include "EventHandler.h"

unsigned char EventHandler::leadBankType() const
{
	// Return the bank type of the first frame in the data blob.
	// Note: there is no array bounds checking here. If this 
	// method is called on an empty EventHandler, gibberish is 
	// the best case scenario.
	return data[5];
}

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
