#include "PulseWidthCommand.h"

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{
	PulseWidthCommand::PulseWidthCommand()
	  : width(-1)
	{}
	
	void PulseWidthCommand::set_width(int newWidth)
	{
		if (newWidth >= 0 && newWidth <= 7)
			highBit = newHighBit;
		else
			throw std::out_of_range("Pulse width must be between 0 and 7 (inclusive).");
	}

	void PulseWidthCommand::InitializeStatics()
	{
		return;
	}

	std::string PulseWidthCommand::ToString()
	{
		if ( ! Validate() )
			throw std::invalid_argument("Width must be set before converting to a string.");
			
          std::stringstream stream;
          stream << "aD" << width;
          
          return stream.str();
	}

};
