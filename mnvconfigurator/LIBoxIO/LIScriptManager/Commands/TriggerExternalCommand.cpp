#include "TriggerExternalCommand.h"
#include "TriggerExternalCommandGrammar.h"

#include <vector>

namespace Minerva
{
	// have to initialize static members outside class declaration
	TriggerExternalCommandGrammar * TriggerExternalCommand::class_grammar = NULL;

	TriggerExternalCommand::TriggerExternalCommand()
	{
		commandType = TRIGGER_EXTERNAL_COMMAND;
		
		if (TriggerExternalCommand::class_grammar == NULL)
			TriggerExternalCommand::class_grammar = new TriggerExternalCommandGrammar;
		
		grammar = TriggerExternalCommand::class_grammar;
	}
};
