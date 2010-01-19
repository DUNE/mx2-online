#include "PulseHeightLowBitsCommand.h"

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{

	PulseHeightLowBitsCommand::PulseHeightLowBitsCommand()
	  : lowBit1(-1), lowBit2(-1)
	{}
	
	void PulseHeightLowBitsCommand::set_lowBit1(int newLowBit1)
	{
		if (newLowBit1 >= 0 && newLowBit1 <= 15)
			lowBit1 = newLowBit1;
		else
			throw std::out_of_range("Both low bits must be between 0 and 15 (inclusive).");
	}

	void PulseHeightLowBitsCommand::set_lowBit2(int newLowBit2)
	{
		if (newLowBit2 >= 0 && newLowBit2 <= 15)
			lowBit2 = newLowBit2;
		else
			throw std::out_of_range("Both low bits must be between 0 and 15 (inclusive).");
	}

	void PulseHeightLowBitsCommand::InitializeStatics()
	{
		if (initialized)
			return;
		
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_HIGH_BIT, -1) );
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_STORE, 1) );

		initialized = true;
		return;
	}

	std::string PulseHeightLowBitsCommand::ToString()
	{
		if ( ! Validate() )
			throw std::invalid_argument("Both low bits must be set before converting the command to a string.");
			
          std::stringstream stream;
          stream << "aC" << std::hex << lowBit1;
          stream << "_";
          stream << std::hex << lowBit2;
          
          return stream.str();
	}

};
