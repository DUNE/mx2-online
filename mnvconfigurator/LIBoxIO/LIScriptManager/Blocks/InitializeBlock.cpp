#include "InitializeBlock.h"
#include "../../Command.h"

#include <map>

namespace Minerva
{
	void InitializeBlock::InitializeStatics()
	{
		if (initialized)
			return;
			
		numAllowedCommands.insert( std::pair<CommandType, int>(INITIALIZE, 1) );
		requiredCommands.push_back(INITIALIZE);
		
		initialized = true;
		return;
	}


};
