#ifndef PULSESETUPBLOCK_H
#define PULSESETUPBLOCK_H 1

#include "CommandBlock.h"
#include "PulseSetupBlockGrammar.h"

#include <string>

namespace Minerva
{
	class PulseSetupBlock : public CommandBlock
	{
		public:
			PulseSetupBlock();
			
			std::string  Describe()		{ return std::string("Block of commands that sets up the pulse shape."); };
			
		protected:
			static PulseSetupBlockGrammar * class_grammar;
	};	
};

#endif
