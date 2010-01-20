#include "GenericScriptGrammar.h"

#include "../Blocks/CommandBlock.h"

namespace Minerva
{
	GenericScriptGrammar::GenericScriptGrammar()
	{
		requiredBlocks.insert( CommandBlockType(RESET_BLOCK | INITIALIZE_BLOCK | LED_SELECTION_BLOCK | TRIGGER_SETUP_BLOCK | PULSE_SETUP_BLOCK) );
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
