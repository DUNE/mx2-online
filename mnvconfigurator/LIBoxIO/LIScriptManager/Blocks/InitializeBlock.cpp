#include "InitializeBlock.h"
#include "InitializeBlockGrammar.h"

#include "../Commands/Command.h"

namespace Minerva
{
	// have to initialize static members outside class declaration
	InitializeBlockGrammar * InitializeBlock::class_grammar = NULL;

	InitializeBlock::InitializeBlock()
	{
		commandBlockType = INITIALIZE_BLOCK;
		
		if (InitializeBlock::class_grammar == NULL)
			InitializeBlock::class_grammar = new InitializeBlockGrammar;

		grammar = InitializeBlock::class_grammar;
	}
};
