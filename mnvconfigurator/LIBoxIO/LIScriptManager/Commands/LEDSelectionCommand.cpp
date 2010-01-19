#include "LEDSelectionCommand.h"

#include <map>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{
	LEDSelectionCommand::LEDSelectionCommand()
	  : LEDgroup('\0')
	{}
	
	void LEDSelectionCommand::set_LEDgroup(char newLEDgroup)
	{
		std::string possibleGroups = "0abcdefghinklmnopqrstuv";
		if (possibleGroups.find(newLEDgroup) != std::npos)
			LEDgroup = newLEDgroup;
		else
			throw std::out_of_range("LED group must be either '0' or between 'a' and 'v' (inclusive).");
	}

	void LEDSelectionCommand::InitializeStatics()
	{
		return;
	}

	std::string LEDSelectionCommand::ToString()
	{
		if ( ! Validate() )
			throw std::invalid_argument("LED group must be set before converting to a string.");
			
          std::stringstream stream;
          stream << "aE" << LEDgroup;
          
          return stream.str();
	}

};
