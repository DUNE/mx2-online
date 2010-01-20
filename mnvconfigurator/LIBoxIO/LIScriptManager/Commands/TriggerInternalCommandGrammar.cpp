#include "TriggerInternalCommandGrammar.h"
#include "CommandTypes.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	TriggerInternalCommandGrammar::TriggerInternalCommandGrammar()
	{
		tokenTemplate = std::string("aK");

		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_HIGH_NUMBER_COMMAND, 0) );
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_LOW_NUMBER_COMMAND, 0) );
		
		excludedCommands.insert(TRIGGER_EXTERNAL_COMMAND);
	}
};
