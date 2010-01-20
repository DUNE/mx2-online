#ifndef INITIALIZEBLOCK_H
#define INITIALIZEBLOCK_H 1

#include "CommandBlock.h"
#include "InitializeBlockGrammar.h"

#include <string>

namespace Minerva
{
	class InitializeBlock : public CommandBlock
	{
		public:
			InitializeBlock();
			
			std::string  Describe()		{ return std::string("Block of commands that initializes the LI box."); };
			
		protected:
			// this guy allows us to avoid making one copy of the grammar for each object we instantiate.
			static InitializeBlockGrammar * class_grammar;
	};	
};

#endif
