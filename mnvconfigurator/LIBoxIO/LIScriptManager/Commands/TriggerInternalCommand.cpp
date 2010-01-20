#include "TriggerInternalCommand.h"
#include "TriggerInternalCommandGrammar.h"

namespace Minerva
{
	// have to initialize static members outside class declaration
	TriggerInternalCommandGrammar * TriggerInternalCommand::class_grammar = NULL;

	TriggerInternalCommand::TriggerInternalCommand()
	{
		commandType = TRIGGER_INTERNAL_COMMAND;

		if (TriggerInternalCommand::class_grammar == NULL)
			TriggerInternalCommand::class_grammar = new TriggerInternalCommandGrammar;
		
		grammar = TriggerInternalCommand::class_grammar;
	}
};
