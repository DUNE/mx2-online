#include "InitializeCommand.h"
#include "InitializeCommandGrammar.h"

namespace Minerva
{
	// have to initialize static members outside class declaration
	InitializeCommandGrammar * InitializeCommand::class_grammar = NULL;

	InitializeCommand::InitializeCommand()
	{
		commandType = INITIALIZE_COMMAND;
		
		if (InitializeCommand::class_grammar == NULL)
			InitializeCommand::class_grammar = new InitializeCommandGrammar;
		
		grammar = InitializeCommand::class_grammar;
	}

};
