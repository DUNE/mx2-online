#include "TriggerRateHighNumberCommand.h"
#include "TriggerRateHighNumberCommandGrammar.h"

#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{
	TriggerRateHighNumberCommandGrammar * TriggerRateHighNumberCommand::class_grammar = NULL;

	TriggerRateHighNumberCommand::TriggerRateHighNumberCommand(int d1, int d2)
	   : digit1(d1), digit2(d2)
	{
		commandType = TRIGGER_RATE_HIGH_NUMBER_COMMAND;
		
		if (TriggerRateHighNumberCommand::class_grammar == NULL)
			TriggerRateHighNumberCommand::class_grammar = new TriggerRateHighNumberCommandGrammar;
		
		grammar = TriggerRateHighNumberCommand::class_grammar;
	}

	void TriggerRateHighNumberCommand::set_digit1(int newDigit1)
	{
		if (newDigit1 >= 0 && newDigit1 <= 15)
			digit1 = newDigit1;
		else
			throw std::out_of_range("Both high number digits must be between 0 and 15 (inclusive).");
	}

	void TriggerRateHighNumberCommand::set_digit2(int newDigit2)
	{
		if (newDigit2 >= 0 && newDigit2 <= 15)
			digit2 = newDigit2;
		else
			throw std::out_of_range("Both low bits must be between 0 and 15 (inclusive).");
	}

	std::string TriggerRateHighNumberCommand::ToString()
	{
		if ( ! Validate() )
			throw std::invalid_argument("Both low bits must be set before converting the command to a string.");
			
          std::stringstream stream;
          stream << "aH" << std::hex << digit1 << digit2;
          
          return stream.str();
	}

};
