#include "TriggerSetupBlockGrammar.h"

#include "../Commands/CommandTypes.h"

#include <vector>
#include <map>

namespace Minerva
{
	TriggerSetupBlockGrammar::TriggerSetupBlockGrammar()
	{
		numAllowedCommands.insert( std::pair<CommandType, int>(TRIGGER_INTERNAL_COMMAND, 1) );
		numAllowedCommands.insert( std::pair<CommandType, int>(TRIGGER_EXTERNAL_COMMAND, 1) );
		numAllowedCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_HIGH_NUMBER_COMMAND, 1) );
		numAllowedCommands.insert( std::pair<CommandType, int>(TRIGGER_RATE_LOW_NUMBER_COMMAND, 1) );

		requiredCommands.insert( CommandType( TRIGGER_EXTERNAL_COMMAND | TRIGGER_INTERNAL_COMMAND ) );
	}
	
	bool TriggerSetupBlockGrammar::ValidCommand(Command * command)
	{
		switch (command->get_commandType())
		{
			case TRIGGER_INTERNAL_COMMAND:			// fall through
			case TRIGGER_EXTERNAL_COMMAND:			// fall through
			case TRIGGER_RATE_HIGH_NUMBER_COMMAND:	// fall through
			case TRIGGER_RATE_LOW_NUMBER_COMMAND:
				return true;
				break;
				
			default:
				return false;
		}
	}
};
