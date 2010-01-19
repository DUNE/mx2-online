#ifndef PULSEWIDTHCOMMAND_H
#define PULSEWIDTHCOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class PulseWidthCommand : public Command
	{
		public:
			PulseWidthCommand();
			
			inline bool Validate() { return (width >= 0); };
			
			inline std::string ToString();
			inline static std::string Description() { return std::string("Sets pulse width."); };
			
			inline int get_width()                 { return width; };
			void set_width(int newWidth);
			
			bool operator==(const PulseWidthCommand& rhs) { return ( width == rhs.get_width() ); };

		protected:
			static const CommandType commandType    = PULSE_WIDTH;
			static const std::string tokenTemplate  = std::string("aD?");'
			
		private:
			int width;

	};
};

#endif
