#include "TriggerExternalCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	TriggerExternalCommandGrammar::TriggerExternalCommandGrammar()
	{
		tokenTemplate = std::string("aQ");
		
		excludedCommands.insert(TRIGGER_INTERNAL_COMMAND);
		excludedCommands.insert(TRIGGER_RATE_HIGH_NUMBER_COMMAND);
		excludedCommands.insert(TRIGGER_RATE_LOW_NUMBER_COMMAND);
	}
};
