#ifndef LEDSELECTIONBLOCK_H
#define LEDSELECTIONBLOCK_H 1

#include "CommandBlock.h"
#include "LEDSelectionBlockGrammar.h"

#include <string>

namespace Minerva
{
	class LEDSelectionBlock : public CommandBlock
	{
		public:
			LEDSelectionBlock();
		
			std::string  Describe()		{ return std::string("Block of commands that selects which LEDs to use."); };
			
		protected:
			// this guy allows us to avoid making one copy of the grammar for each object we instantiate.
			static LEDSelectionBlockGrammar * class_grammar;

	};	
};

#endif
