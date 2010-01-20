#ifndef GENERICSCRIPTGRAMMAR_H
#define GENERICSCRIPTGRAMMAR_H 1

#include "ScriptGrammar.h"
#include "../Blocks/CommandBlock.h"

namespace Minerva
{
	class GenericScriptGrammar : public ScriptGrammar
	{
		public:
			GenericScriptGrammar();
			
			bool ValidBlock(CommandBlock * block);	
	};
};

#endif
