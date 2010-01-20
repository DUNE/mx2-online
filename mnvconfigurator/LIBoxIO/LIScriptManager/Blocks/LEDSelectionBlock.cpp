#include "LEDSelectionBlock.h"
#include "LEDSelectionBlockGrammar.h"

#include "../Commands/Command.h"

namespace Minerva
{
	// have to initialize static members outside class declaration
	LEDSelectionBlockGrammar * LEDSelectionBlock::class_grammar = NULL;

	LEDSelectionBlock::LEDSelectionBlock()
	{
		commandBlockType = LED_SELECTION_BLOCK;
		
		if (LEDSelectionBlock::class_grammar == NULL)
			LEDSelectionBlock::class_grammar = new LEDSelectionBlockGrammar;
			
		grammar = LEDSelectionBlock::class_grammar;
	}
};
