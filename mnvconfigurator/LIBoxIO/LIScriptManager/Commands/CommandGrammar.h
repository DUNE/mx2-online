#ifndef COMMANDGRAMMAR_H
#define COMMANDGRAMMAR_H 1

#include "CommandTypes.h"

#include <string>
#include <set>
#include <map>

namespace Minerva
{
	class CommandGrammar
	{
		public:
			virtual ~CommandGrammar() {};

			bool  TestString(std::string teststring);	// tests if a string matches the right pattern for this command.
			
			const std::map<CommandType, int> & get_requiredCommands()  { return requiredCommands; };
			const std::set<CommandType>      & get_excludedCommands()  { return excludedCommands; };

		
		protected:
			std::map<CommandType, int>    requiredCommands;
			std::set<CommandType>         excludedCommands;
			
			std::string tokenTemplate;
	};
};

#endif
