#ifndef PULSESETUPBLOCKGRAMMAR_H
#define PULSESETUPBLOCKGRAMMAR_H 1

#include "BlockGrammar.h"
#include "../Commands/Command.h"

namespace Minerva
{
	class PulseSetupBlockGrammar : public BlockGrammar
	{
		public:
			PulseSetupBlockGrammar();
			
			bool ValidCommand(Command * command);	
	};
};

#endif
