#ifndef INITIALIZEBLOCK_H
#define INITIALIZEBLOCK_H 1

#include "CommandBlock.h"
#include "../Commands/ResetCommand.h"

#include <string>

namespace Minerva
{
	class InitializeBlock : public CommandBlock
	{
		public:
			static std::string  Description()		{ return std::string("Block of commands that initializes the LI box."); };
			
			bool ValidCommand(InitializeCommand * command) { return true; };
			
			void AddCommand(InitializeCommand * command) { AddValidCommand(command); };
			
		protected:
			static void InitializeStatics();

			static CommandBlockType commandBlockType = INITIALIZE;

	};	
};

#endif
