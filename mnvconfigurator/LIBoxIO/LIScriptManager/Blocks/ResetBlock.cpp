#include "ResetBlock.h"
#include "../../Command.h"

#include <map>

namespace Minerva
{
	void ResetBlock::InitializeStatics()
	{
		if (initialized)
			return;
			
		numAllowedCommands.insert( std::pair<CommandType, int>(RESET, 1) );
		requiredCommands.push_back(RESET);
		
		initialized = true;
		return;
	}


};
