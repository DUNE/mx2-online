#include "InitializeBlockGrammar.h"

#include "../Commands/CommandTypes.h"

#include <vector>
#include <map>

namespace Minerva
{
	InitializeBlockGrammar::InitializeBlockGrammar()
	{
		numAllowedCommands.insert( std::pair<CommandType, int>(INITIALIZE_COMMAND, 1) );
		requiredCommands.insert(INITIALIZE_COMMAND);
	}
	
	bool InitializeBlockGrammar::ValidCommand(Command * command)
	{
		switch (command->get_commandType())
		{
			case INITIALIZE_BLOCK:
				return true;
				break;
				
			default:
				return false;
		}
	}
};
