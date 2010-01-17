#ifndef COMMAND_H
#define COMMAND_H

#include "CommandStructure.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	enum CommandType { RESET, LED_SELECTION, PULSE_HEIGHT, PULSE_WIDTH };

	class Command : public CommandStructure
	{
		public:
			virtual std::string        ToString()    = 0;
			static virtual std::string Description() = 0;
			
			virtual bool Validate()                         = 0;			
			static bool  TestString(std::string teststring);	// tests if a string matches the right pattern for this command.
			
			
		protected:
			std::vector<Command *> commands;
			
			// the grammar for the command type.
			// derived classes will use these to specify
			// what kind of commands it's compatible with.
			static std::map<CommandType, int>    numAllowedCommands;

			static std::map<CommandType, int>    requiredCommands;
			static std::vector<CommandType>      excludedCommands;
			
			std::map<CommandType, int>           numCommands;
			
			static const CommandType commandType;
			static const std::string tokenTemplate;
			
			
	};
};
