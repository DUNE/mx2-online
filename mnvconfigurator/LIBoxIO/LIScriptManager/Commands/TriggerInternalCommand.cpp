#include "TriggerInternalCommand.h"

#include <map>

namespace Minerva
{
	void TriggerInternalCommand::InitializeStatics()
	{
		if (initialized)
			return;
			
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_HIGH_NUMBER, 0) );
		requiredCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_LOW_NUMBER, 0) );
		
		excludedCommands.insert(TRIGGER_EXTERNAL);
		
		initialized = true;
		return;
	}
};
