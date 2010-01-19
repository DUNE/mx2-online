#ifndef RESETBLOCK_H
#define RESETBLOCK_H 1

#include "CommandBlock.h"
#include "../Commands/ResetCommand.h"

#include <string>

namespace Minerva
{
	class ResetBlock : public CommandBlock
	{
		public:
			static std::string  Description()		{ return std::string("Block of commands that resets the LI box."); };
			
			bool ValidCommand(ResetCommand * command) { return true; };
			
			void AddCommand(ResetCommand * command) { AddValidCommand(command); };
			
		protected:
			static void InitializeStatics();

			static CommandBlockType commandBlockType = RESET;

	};	
};

#endif
