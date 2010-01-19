#ifndef LEDSELECTIONCOMMAND_H
#define LEDSELECTIONCOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class LEDSelectionCommand : public Command
	{
		public:
			LEDSelectionCommand();
			
			inline bool Validate() { return (LEDgroup != '\0'); };
			
			std::string ToString();
			inline static std::string Description() { return std::string("Sets which groups of LEDs to fire."); };
			
			inline int get_LEDgroup()                 { return LEDgroup; };
			void set_LEDgroup(char newLEDgroup);
			
			bool operator==(const LEDSelectionCommand& rhs) { return ( LEDgroup == rhs.get_LEDgroup() ); };

		protected:
			static const CommandType commandType    = LED_SELECTION;
			static const std::string tokenTemplate  = std::string("aE?");'
			
		private:
			char LEDgroup;
	};
};

#endif
