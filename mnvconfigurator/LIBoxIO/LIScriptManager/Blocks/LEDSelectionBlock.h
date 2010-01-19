#ifndef LEDSELECTIONBLOCK_H
#define LEDSELECTIONBLOCK_H 1

#include "CommandBlock.h"
#include "../Commands/ResetCommand.h"

#include <string>

namespace Minerva
{
	class LEDSelectionBlock : public CommandBlock
	{
		public:
			static std::string  Description()		{ return std::string("Block of commands that selects which LEDs to use."); };
			
			bool ValidCommand(LEDSelectionCommand * command) { return true; };
			
			void AddCommand(LEDSelectionCommand * command) { AddValidCommand(command); };
			
		protected:
			static void InitializeStatics();

			static CommandBlockType commandBlockType = LED_SELECTION;

	};	
};

#endif
