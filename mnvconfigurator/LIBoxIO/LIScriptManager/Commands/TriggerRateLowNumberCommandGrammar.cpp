#include "TriggerRateLowNumberCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	TriggerRateLowNumberCommandGrammar::TriggerRateLowNumberCommandGrammar()
	{
		tokenTemplate = std::string("aI??");
		
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_INTERNAL_COMMAND, 0) );
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_LOW_NUMBER_COMMAND, 0) );
		
		excludedCommands.insert(TRIGGER_EXTERNAL_COMMAND);
	}
};
