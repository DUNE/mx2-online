#include "PulseHeightLowBitsCommand.h"
#include "PulseHeightLowBitsCommandGrammar.h"

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

#include <iostream>

namespace Minerva
{
	// have to initialize static members outside class declaration
	PulseHeightLowBitsCommandGrammar * PulseHeightLowBitsCommand::class_grammar = NULL;

	PulseHeightLowBitsCommand::PulseHeightLowBitsCommand(int lb1, int lb2)
	   : lowBit1(lb1), lowBit2(lb2)
	{
		commandType = PULSE_HEIGHT_LOW_BITS_COMMAND;
		
		if (PulseHeightLowBitsCommand::class_grammar == NULL)
			PulseHeightLowBitsCommand::class_grammar = new PulseHeightLowBitsCommandGrammar;
		
		grammar = PulseHeightLowBitsCommand::class_grammar;
	}
	
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
