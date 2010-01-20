#include "PulseHeightStoreCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	PulseHeightStoreCommandGrammar::PulseHeightStoreCommandGrammar()
	{
		tokenTemplate = std::string("aO");
		
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_HIGH_BIT_COMMAND, -2) );
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_LOW_BITS_COMMAND, -1) );
	}
};
