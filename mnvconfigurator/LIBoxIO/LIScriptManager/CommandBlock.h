#ifndef COMMANDBLOCK_H
#define COMMANDBLOCK_H 1

#include "CommandStructure.h"
#include "CommandBlock.h"
#include "Command.h"

#include <vector>
#include <map>
#include <string>

namespace Minerva
{
	enum CommandBlockTypes { Reset, Initialize, LEDSelection, TriggerSetup, PulseSetup };

	class CommandBlock : public CommandStructure
	{
		public:
			virtual std::string ToString()         = 0;
			static std::string  Description()      = 0;
			
			virtual bool Validate()                = 0;			
			bool ValidCommand(Command * command);
			
			
		protected:
			std::vector<Command *> commands;
			
			// the grammar for the command block type.
			// derived classes will use these to specify
			// what kind of commands are ok in their block,
			// and what other blocks must (or must not) accompany them
			static std::map<CommandType, int>         numAllowedCommands;
			static std::vector<CommandType>           requiredCommands;

			static std::map<CommandBlockType, int>    requiredBlocks;
			static std::vector<CommandBlockType>      excludedBlocks;
			
			std::map<CommandType, int> numCommands;
			
		private:

	};

};

#endif
