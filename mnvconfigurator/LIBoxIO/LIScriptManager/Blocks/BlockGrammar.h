#ifndef BLOCKGRAMMAR_H
#define BLOCKGRAMMAR_H 1

#include "../Commands/Command.h"
#include "BlockTypes.h"

#include <vector>
#include <map>

namespace Minerva
{
	class BlockGrammar
	{
		public:
			virtual ~BlockGrammar() {};

			const std::map<CommandType, int> & get_numAllowedCommands()  { return numAllowedCommands; };
			const std::set<CommandType>   & get_requiredCommands()       { return requiredCommands; };

			const std::map<CommandBlockType, int> & get_requiredBlocks()    { return requiredBlocks; };
			const std::set<CommandBlockType>      & get_excludedBlocks()    { return excludedBlocks; };

			virtual bool ValidCommand(Command * command) = 0;
		
		protected:
			std::map<CommandType, int>         numAllowedCommands;
			std::set<CommandType>              requiredCommands;

			std::map<CommandBlockType, int>    requiredBlocks;
			std::set<CommandBlockType>         excludedBlocks;
	};
};

#endif
