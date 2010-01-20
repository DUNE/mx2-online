#include "LEDSelectionBlockGrammar.h"

#include "../Commands/Command.h"

#include <vector>
#include <map>

namespace Minerva
{
	LEDSelectionBlockGrammar::LEDSelectionBlockGrammar()
	{
		numAllowedCommands.insert( std::pair<CommandType, int>(LED_SELECTION_COMMAND, 1) );
		requiredCommands.insert(LED_SELECTION_COMMAND);
	}
	
	bool LEDSelectionBlockGrammar::ValidCommand(Command * command)
	{
		switch (command->get_commandType())
		{
			case LED_SELECTION_COMMAND:
				return true;
				break;
				
			default:
				return false;
		}
	}
};
