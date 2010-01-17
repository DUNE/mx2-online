#ifndef PULSEHEIGHTCOMMAND_H
#define PULSEHEIGHTCOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class PulseHeightCommand : Command
	{
		public:
			inline bool Validate() { return (pulseHeight >= 4.05 && pulseHeight <= 12.07); };
			
			inline static std::string ToString();
			inline static std::string Description() { return std::string("Pulse h reset for the LI box."); };
			
		protected:
			static const CommandType commandType    = PULSE_HEIGHT;
			static const std::string tokenTemplate  = "_X";'
			
		private:
			float pulseHeight;

	};
};

#endif
