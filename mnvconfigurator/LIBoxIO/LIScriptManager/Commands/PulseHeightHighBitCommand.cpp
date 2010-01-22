#include "PulseHeightHighBitCommand.h"
#include "PulseHeightHighBitCommandGrammar.h"

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{
	// have to initialize static members outside class declaration
	PulseHeightHighBitCommandGrammar * PulseHeightHighBitCommand::class_grammar = NULL;

	PulseHeightHighBitCommand::PulseHeightHighBitCommand(int hb)
	  : highBit(hb)
	{
		commandType = PULSE_HEIGHT_HIGH_BIT_COMMAND;
		
		if (PulseHeightHighBitCommand::class_grammar == NULL)
			PulseHeightHighBitCommand::class_grammar = new PulseHeightHighBitCommandGrammar;
		
		grammar = PulseHeightHighBitCommand::class_grammar;
	}
	
	void PulseHeightHighBitCommand::set_highBit(int newHighBit)
	{
		if (newHighBit >= 0 && newHighBit <= 16)
			highBit = newHighBit;
		else
			throw std::out_of_range("High bit must be between 0 and 16 (inclusive).");
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
