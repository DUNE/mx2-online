#include "ResetBlock.h"
#include "ResetBlockGrammar.h"

#include "../Commands/Command.h"

namespace Minerva
{
	// have to initialize static members outside class declaration
	ResetBlockGrammar * ResetBlock::class_grammar = NULL;

	ResetBlock::ResetBlock()
	{
		commandBlockType = RESET_BLOCK;

		if (ResetBlock::class_grammar == NULL)
			ResetBlock::class_grammar = new ResetBlockGrammar;

		grammar = ResetBlock::class_grammar;
	}


};
