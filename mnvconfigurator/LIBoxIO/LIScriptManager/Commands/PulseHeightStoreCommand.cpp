#include "PulseHeightStoreCommand.h"

#include <map>

namespace Minerva
{
	void PulseHeightStoreCommand::InitializeStatics()
	{
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_HIGH_BIT, -2) );
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_LOW_BITS, -1) );
		
		initialized = true;
		
		return;
	}
};
