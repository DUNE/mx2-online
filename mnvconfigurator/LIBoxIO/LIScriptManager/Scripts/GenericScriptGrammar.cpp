#include "GenericScriptGrammar.h"

#include "../Blocks/CommandBlock.h"

namespace Minerva
{
	GenericScriptGrammar::GenericScriptGrammar()
	{
		requiredBlocks.insert( CommandBlockType(RESET_BLOCK | INITIALIZE_BLOCK | LED_SELECTION_BLOCK | TRIGGER_SETUP_BLOCK | PULSE_SETUP_BLOCK) );
		
		numAllowedBlocks.insert( std::pair<CommandBlockType, int>(RESET_BLOCK, 1) );
		numAllowedBlocks.insert( std::pair<CommandBlockType, int>(INITIALIZE_BLOCK, 1) );
		numAllowedBlocks.insert( std::pair<CommandBlockType, int>(LED_SELECTION_BLOCK, 1) );
		numAllowedBlocks.insert( std::pair<CommandBlockType, int>(TRIGGER_SETUP_BLOCK, 1) );
		numAllowedBlocks.insert( std::pair<CommandBlockType, int>(PULSE_SETUP_BLOCK, 1) );
	}
	
	bool GenericScriptGrammar::ValidBlock(CommandBlock * block)
	{
		switch (block->get_commandBlockType())
		{
			default:
				return true;
		}
	}
};
