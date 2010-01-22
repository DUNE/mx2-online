#include "PulseWidthCommand.h"
#include "PulseWidthCommandGrammar.h"

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{
	// have to initialize static members outside class declaration
	PulseWidthCommandGrammar * PulseWidthCommand::class_grammar = NULL;

	PulseWidthCommand::PulseWidthCommand(int newWidth)
	   : width(newWidth)
	{
		commandType = PULSE_WIDTH_COMMAND;
		
		if (PulseWidthCommand::class_grammar == NULL)
			PulseWidthCommand::class_grammar = new PulseWidthCommandGrammar;
		
		grammar = PulseWidthCommand::class_grammar;
	}
	
	void PulseWidthCommand::set_width(int newWidth)
	{
		if (newWidth >= 0 && newWidth <= 7)
			width = newWidth;
		else
			throw std::out_of_range("Pulse width must be between 0 and 7 (inclusive).");
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
