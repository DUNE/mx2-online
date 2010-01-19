#ifndef COMMANDBLOCK_H
#define COMMANDBLOCK_H 1

#include "../CommandStructure.h"
#include "../Commands/Command.h"

#include <vector>
#include <map>
#include <string>

namespace Minerva
{
	enum CommandBlockTypes { RESET, INITIALIZE, LED_SELECTION, TRIGGER_SETUP, PULSE_SETUP };

	class CommandBlock : public CommandStructure
	{
		public:
			virtual        std::string  ToString();
			virtual static std::string  Description()      = 0;
			
			bool Validate();			
			bool ValidCommand(Command * command);
			void AddCommand(Command * command);
			
		protected:
			virtual static void InitializeStatics() = 0;		// initializes any static variables (like the ones below) that can't be initialized here (like ones with std::maps, std::vectors, etc.)
			static bool initialized = false;
			
			void AddValidCommand(Command * command);

			std::vector<Command *> commands;
			
			// the grammar for the command block type.
			// derived classes will use these to specify
			// what kind of commands are ok in their block,
			// and what other blocks must (or must not) accompany them
			static std::map<CommandType, int>         numAllowedCommands;
			static std::vector<CommandType>           requiredCommands;

			static std::map<CommandBlockType, int>    requiredBlocks;
			static std::vector<CommandBlockType>      excludedBlocks;

			static CommandBlockType commandBlockType;
			
			std::map<CommandType, int> numCommands;
			
		private:

	};

};

#endif
