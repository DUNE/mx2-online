#ifndef RESETBLOCKGRAMMAR_H
#define RESETBLOCKGRAMMAR_H 1

#include "BlockGrammar.h"
#include "../Commands/Command.h"

namespace Minerva
{
	class ResetBlockGrammar : public BlockGrammar
	{
		public:
			ResetBlockGrammar();
			
			bool ValidCommand(Command * command);	
	};
};

#endif
