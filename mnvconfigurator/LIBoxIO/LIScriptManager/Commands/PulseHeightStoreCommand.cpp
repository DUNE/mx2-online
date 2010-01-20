#include "PulseHeightStoreCommand.h"

#include <map>

namespace Minerva
{
	// have to initialize static members outside class declaration
	PulseHeightStoreCommandGrammar * PulseHeightStoreCommand::class_grammar = NULL;

	PulseHeightStoreCommand::PulseHeightStoreCommand()
	{
		commandType = PULSE_HEIGHT_STORE_COMMAND;
		
		if (PulseHeightStoreCommand::class_grammar == NULL)
			PulseHeightStoreCommand::class_grammar = new PulseHeightStoreCommandGrammar;
		
		grammar = PulseHeightStoreCommand::class_grammar;
	}
};
