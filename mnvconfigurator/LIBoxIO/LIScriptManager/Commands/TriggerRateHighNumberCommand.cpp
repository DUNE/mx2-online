#include "TriggerRateHighNumberCommand.h"

#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

namespace Minerva
{

	TriggerRateHighNumberCommand::TriggerRateHighNumberCommand()
	  : digit1(-1), digit2(-1)
	{}
	
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

	void TriggerRateHighNumberCommand::InitializeStatics()
	{
		if (initialized)
			return;
		
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_INTERNAL, 0) );
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_LOW_NUMBER, 0) );
		
		excludedCommands.push_back(TRIGGER_EXTERNAL);

		initialized = true;
		return;
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
