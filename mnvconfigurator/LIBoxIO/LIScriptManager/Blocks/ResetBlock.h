#ifndef RESETBLOCK_H
#define RESETBLOCK_H 1

#include "CommandBlock.h"
#include "ResetBlockGrammar.h"

#include <string>

namespace Minerva
{
	class ResetBlock : public CommandBlock
	{
		public:
			ResetBlock();
			
			std::string  Describe()		{ return std::string("Block of commands that resets the LI box."); };
			
		protected:
			// this guy allows us to avoid making one copy of the grammar for each object we instantiate.
			static ResetBlockGrammar * class_grammar;
	};	
};

#endif
