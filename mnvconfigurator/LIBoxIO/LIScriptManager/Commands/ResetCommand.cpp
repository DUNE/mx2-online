#include "ResetCommand.h"
#include "ResetCommandGrammar.h"

namespace Minerva
{
	// have to initialize static members outside class declaration
	ResetCommandGrammar * ResetCommand::class_grammar = NULL;

	ResetCommand::ResetCommand()
	{
		commandType = RESET_COMMAND;

		if (ResetCommand::class_grammar == NULL)
			ResetCommand::class_grammar = new ResetCommandGrammar;
		
		grammar = ResetCommand::class_grammar;
	}
};
