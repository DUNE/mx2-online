#ifndef TRIGGERSETUPBLOCK_H
#define TRIGGERSETUPBLOCK_H 1

#include "CommandBlock.h"
#include "TriggerSetupBlockGrammar.h"

#include <string>

namespace Minerva
{
	class TriggerSetupBlock : public CommandBlock
	{
		public:
			TriggerSetupBlock();

			std::string  Describe()		{ return std::string("Block of commands that sets up the triggering."); };
			
			
		protected:
			// this guy allows us to avoid making one copy of the grammar for each object we instantiate.
			static TriggerSetupBlockGrammar * class_grammar;
	};	
};

#endif
