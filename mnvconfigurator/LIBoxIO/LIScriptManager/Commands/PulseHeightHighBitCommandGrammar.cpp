#include "PulseHeightHighBitCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	PulseHeightHighBitCommandGrammar::PulseHeightHighBitCommandGrammar()
	{
		tokenTemplate = std::string("aB?");
		
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_LOW_BITS_COMMAND, 1) );
		requiredCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_STORE_COMMAND, 2) );
	}
};
