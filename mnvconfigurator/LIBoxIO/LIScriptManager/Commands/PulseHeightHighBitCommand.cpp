#include "PulseHeightHighBitCommand.h"

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{
	PulseHeightHighBitCommand::PulseHeightHighBitCommand()
	  : highBit(-1)
	{}
	
	void PulseHeightHighBitCommand::set_highBit(int newHighBit)
	{
		if (newHighBit >= 0 && newHighBit <= 16)
			highBit = newHighBit;
		else
			throw std::out_of_range("High bit must be between 0 and 16 (inclusive).");
	}

	void PulseHeightHighBitCommand::InitializeStatics()
	{
		if (initialized)
			return;
		
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_LOW_BITS, 1) );
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_STORE, 2) );

		initialized = true;
		return;
	}

	std::string PulseHeightHighBitCommand::ToString()
	{
		if ( ! Validate() )
			throw std::invalid_argument("High bit must be set before converting to a string.");
			
          std::stringstream stream;
          stream << "aB" << highBit;
          
          return stream.str();
	}

};
