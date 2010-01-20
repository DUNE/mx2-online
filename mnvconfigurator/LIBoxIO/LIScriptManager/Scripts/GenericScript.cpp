#include "GenericScript.h"
#include "GenericScriptGrammar.h"

#include "../Blocks/CommandBlock.h"

namespace Minerva
{
	GenericScriptGrammar * GenericScript::class_grammar = NULL;

	GenericScript::GenericScript()
	{
		scriptType = GENERIC_SCRIPT;
		
		if (GenericScript::class_grammar == NULL)
			GenericScript::class_grammar = new GenericScriptGrammar;
		
		grammar = GenericScript::class_grammar;
	}
};
