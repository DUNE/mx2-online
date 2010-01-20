#include "PulseSetupBlockGrammar.h"

#include "../Commands/CommandTypes.h"

#include <vector>
#include <map>

namespace Minerva
{
	PulseSetupBlockGrammar::PulseSetupBlockGrammar()
	{
		numAllowedCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_HIGH_BIT_COMMAND, 1) );
		numAllowedCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_LOW_BITS_COMMAND, 1) );
		numAllowedCommands.insert( std::pair<CommandType, int>(PULSE_HEIGHT_STORE_COMMAND, 1) );
		numAllowedCommands.insert( std::pair<CommandType, int>(PULSE_WIDTH_COMMAND, 1) );

		requiredCommands.insert( CommandType(PULSE_HEIGHT_STORE_COMMAND | PULSE_WIDTH_COMMAND) );
	}
	
	bool PulseSetupBlockGrammar::ValidCommand(Command * command)
	{
		switch (command->get_commandType())
		{
			case PULSE_HEIGHT_HIGH_BIT_COMMAND:	// fall through
			case PULSE_HEIGHT_LOW_BITS_COMMAND:	     // fall through
			case PULSE_HEIGHT_STORE_COMMAND:		// fall through
			case PULSE_WIDTH_COMMAND:	
				return true;
				break;
				
			default:
				return false;
		}
	}
};
