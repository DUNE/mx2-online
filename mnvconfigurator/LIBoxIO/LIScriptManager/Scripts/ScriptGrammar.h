#ifndef SCRIPTGRAMMAR_H
#define SCRIPTGRAMMAR_H 1

#include "../Blocks/CommandBlock.h"
#include "../Blocks/BlockTypes.h"

#include <set>
#include <map>

namespace Minerva
{
	class ScriptGrammar
	{
		public:
			virtual ~ScriptGrammar() {};

			const std::map<CommandBlockType, int> & get_numAllowedBlocks()  { return numAllowedBlocks; };
			const std::set<CommandBlockType>   & get_requiredBlocks()       { return requiredBlocks; };

			virtual bool ValidBlock(CommandBlock * block) = 0;
		
		protected:
			std::map<CommandBlockType, int>         numAllowedBlocks;
			std::set<CommandBlockType>           requiredBlocks;
	};
};

#endif
