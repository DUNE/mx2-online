#include "TriggerExternalCommand.h"

#include <vector>

namespace Minerva
{
	void TriggerExternalCommand::InitializeStatics()
	{
		if (initialized)
			return;
			
		excludedCommands.insert(TRIGGER_INTERNAL);
		excludedCommands.insert(TRIGGER_RATE_HIGH_NUMBER);
		excludedCommands.insert(TRIGGER_RATE_LOW_NUMBER);
	
		initialized = true;
		return;
	}
};
