#ifndef LEDSELECTIONBLOCKGRAMMAR_H
#define LEDSELECTIONBLOCKGRAMMAR_H 1

#include "BlockGrammar.h"
#include "../Commands/Command.h"

namespace Minerva
{
	class LEDSelectionBlockGrammar : public BlockGrammar
	{
		public:
			LEDSelectionBlockGrammar();
			
			bool ValidCommand(Command * command);	
	};
};

#endif
