#include "TriggerSetupBlock.h"
#include "../Commands/Command.h"

#include <map>

namespace Minerva
{
	// have to initialize static members outside class declaration
	TriggerSetupBlockGrammar * TriggerSetupBlock::class_grammar = NULL;

	TriggerSetupBlock::TriggerSetupBlock()
	{
		commandBlockType =TRIGGER_SETUP_BLOCK;
		
		if (TriggerSetupBlock::class_grammar == NULL)
			TriggerSetupBlock::class_grammar = new TriggerSetupBlockGrammar;

		grammar = TriggerSetupBlock::class_grammar;
	}


};
