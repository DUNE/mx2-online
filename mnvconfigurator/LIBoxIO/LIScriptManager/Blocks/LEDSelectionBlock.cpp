#include "LEDSelectionBlock.h"
#include "../../Command.h"

#include <map>

namespace Minerva
{
	void LEDSelectionBlock::InitializeStatics()
	{
		if (initialized)
			return;
			
		numAllowedCommands.insert( std::pair<CommandType, int>(LED_SELECTION, 1) );
		requiredCommands.push_back(LED_SELECTION);
		
		initialized = true;
		return;
	}


};
