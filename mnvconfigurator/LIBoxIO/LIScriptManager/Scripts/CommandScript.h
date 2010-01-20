#ifndef COMMANDSCRIPT_H
#define COMMANDSCRIPT_H 1

#include "../CommandStructure.h"
#include "../Blocks/CommandBlock.h"
#include "ScriptGrammar.h"
#include "ScriptTypes.h"

#include <string>
#include <vector>

namespace Minerva
{
	
	class CommandScript: public CommandStructure
	{
		public:
			virtual ~CommandScript()   {};
			
			virtual bool Validate();
			virtual std::string ToString();
			virtual std::string Describe() = 0;
			
			void AddBlock(CommandBlock * block);
			
		protected:
			ScriptGrammar * grammar;
			std::vector<CommandBlock*> blocks;
			CommandScriptType scriptType;
	};
};

#endif
