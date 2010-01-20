#include "PulseSetupBlock.h"
#include "PulseSetupBlockGrammar.h"

#include "../Commands/Command.h"

namespace Minerva
{
	// have to initialize static members outside class declaration
	PulseSetupBlockGrammar * PulseSetupBlock::class_grammar = NULL;

	PulseSetupBlock::PulseSetupBlock()
	{
		commandBlockType = PULSE_SETUP_BLOCK;
		
		if (PulseSetupBlock::class_grammar == NULL)
			PulseSetupBlock::class_grammar = new PulseSetupBlockGrammar;

		grammar = PulseSetupBlock::class_grammar;
	}


};
