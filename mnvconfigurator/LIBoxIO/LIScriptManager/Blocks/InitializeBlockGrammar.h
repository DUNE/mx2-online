#ifndef INITIALIZEBLOCKGRAMMAR_H
#define INITIALIZEBLOCKGRAMMAR_H 1

#include "BlockGrammar.h"
#include "../Commands/Command.h"

namespace Minerva
{
	class InitializeBlockGrammar : public BlockGrammar
	{
		public:
			InitializeBlockGrammar();
			
			bool ValidCommand(Command * command);	
	};
};

#endif
