#include "PulseHeightLowBitsCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	PulseHeightLowBitsCommandGrammar::PulseHeightLowBitsCommandGrammar()
	{
		tokenTemplate = std::string("aC?_?");
		
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_HIGH_BIT_COMMAND, -1) );
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_STORE_COMMAND, 1) );
	}
};
