#include "TriggerRateHighNumberCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	TriggerRateHighNumberCommandGrammar::TriggerRateHighNumberCommandGrammar()
	{
		tokenTemplate = std::string("aH??");
		
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_INTERNAL_COMMAND, 0) );
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_LOW_NUMBER_COMMAND, 0) );
		
		excludedCommands.insert(TRIGGER_EXTERNAL_COMMAND);
	}
};
