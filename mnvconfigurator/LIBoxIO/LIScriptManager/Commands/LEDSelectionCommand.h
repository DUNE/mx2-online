#ifndef LEDSELECTIONCOMMAND_H
#define LEDSELECTIONCOMMAND_H 1

#include "Command.h"
#include "LEDSelectionCommandGrammar.h"

#include <string>

namespace Minerva
{
	class LEDSelectionCommand : public Command
	{
		public:
			LEDSelectionCommand(char LEDgroup = '\0');
			
			inline bool Validate() { return (LEDgroup != '\0'); };
			
			std::string ToString();
			inline std::string Describe() { return std::string("Sets which groups of LEDs to fire."); };
			
			inline int get_LEDgroup() const                 { return LEDgroup; };
			void set_LEDgroup(char newLEDgroup);
			
			bool operator==(const LEDSelectionCommand& rhs) { return ( LEDgroup == rhs.get_LEDgroup() ); };

		private:
			char LEDgroup;

			static LEDSelectionCommandGrammar * class_grammar;
	};
};

#endif
