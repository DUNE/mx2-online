#include "TriggerRateLowNumberCommand.h"
#include "TriggerRateLowNumberCommandGrammar.h"

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{
	// have to initialize static members outside class declaration
	TriggerRateLowNumberCommandGrammar * TriggerRateLowNumberCommand::class_grammar = NULL;

	TriggerRateLowNumberCommand::TriggerRateLowNumberCommand(int d1, int d2)
	   : digit1(d1), digit2(d2)
	{
		commandType = TRIGGER_RATE_LOW_NUMBER_COMMAND;
		
		if (TriggerRateLowNumberCommand::class_grammar == NULL)
			TriggerRateLowNumberCommand::class_grammar = new TriggerRateLowNumberCommandGrammar;
		
		grammar = TriggerRateLowNumberCommand::class_grammar;
	}

	void TriggerRateLowNumberCommand::set_digit1(int newDigit1)
	{
		if (newDigit1 >= 0 && newDigit1 <= 15)
			digit1 = newDigit1;
		else
			throw std::out_of_range("Both low number digits must be between 0 and 15 (inclusive).");
	}

	void TriggerRateLowNumberCommand::set_digit2(int newDigit2)
	{
		if (newDigit2 >= 0 && newDigit2 <= 15)
			digit2 = newDigit2;
		else
			throw std::out_of_range("Both low number digits must be between 0 and 15 (inclusive).");
	}

	std::string TriggerRateLowNumberCommand::ToString()
	{
		if ( ! Validate() )
			throw std::invalid_argument("Both low digits must be set before converting the command to a string.");
			
          std::stringstream stream;
          stream << "aI" << std::hex << digit1 << digit2;
          
          return stream.str();
	}

};
