#include "ResetBlockGrammar.h"

#include "../Commands/Command.h"

#include <vector>
#include <map>

namespace Minerva
{
	ResetBlockGrammar::ResetBlockGrammar()
	{
		numAllowedCommands.insert( std::pair<CommandType, int>(RESET_COMMAND, 1) );
		requiredCommands.insert(RESET_COMMAND);
	}
	
	bool ResetBlockGrammar::ValidCommand(Command * command)
	{
		switch (command->get_commandType())
		{
			case RESET_COMMAND:
				return true;
				break;
				
			default:
				return false;
		}
	}
};
