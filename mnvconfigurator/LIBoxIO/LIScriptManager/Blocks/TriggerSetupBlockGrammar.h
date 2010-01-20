#ifndef TRIGGERSETUPBLOCKGRAMMAR_H
#define TRIGGERSETUPBLOCKGRAMMAR_H 1

#include "BlockGrammar.h"
#include "../Commands/Command.h"

namespace Minerva
{
	class TriggerSetupBlockGrammar : public BlockGrammar
	{
		public:
			TriggerSetupBlockGrammar();
			
			bool ValidCommand(Command * command);	
	};
};

#endif
