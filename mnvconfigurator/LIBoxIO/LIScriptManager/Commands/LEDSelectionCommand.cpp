#include "LEDSelectionCommand.h"
#include "LEDSelectionCommandGrammar.h"

#include <map>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{
	// have to initialize static members outside class declaration
	LEDSelectionCommandGrammar * LEDSelectionCommand::class_grammar = NULL;

	LEDSelectionCommand::LEDSelectionCommand()
	  : LEDgroup('\0')
	{
		commandType = LED_SELECTION_COMMAND;
		
		if (LEDSelectionCommand::class_grammar == NULL)
			LEDSelectionCommand::class_grammar = new LEDSelectionCommandGrammar;
		
		grammar = LEDSelectionCommand::class_grammar;
	}
	
	void LEDSelectionCommand::set_LEDgroup(char newLEDgroup)
	{
		std::string possibleGroups = "0abcdefghinklmnopqrstuv";
		if (possibleGroups.find(newLEDgroup) != std::string::npos)
			LEDgroup = newLEDgroup;
		else
			throw std::out_of_range("LED group must be either '0' or between 'a' and 'v' (inclusive).");
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
