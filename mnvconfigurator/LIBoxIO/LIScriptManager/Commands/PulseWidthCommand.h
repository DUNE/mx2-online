#ifndef PULSEWIDTHCOMMAND_H
#define PULSEWIDTHCOMMAND_H 1

#include "Command.h"
#include "PulseWidthCommandGrammar.h"

#include <string>

namespace Minerva
{
	class PulseWidthCommand : public Command
	{
		public:
			PulseWidthCommand();
			
			inline bool Validate() { return (width >= 0); };
			
			inline std::string ToString();
			inline std::string Describe() { return std::string("Sets pulse width."); };
			
			inline int get_width() const              { return width; };
			void set_width(int newWidth);
			
			bool operator==(const PulseWidthCommand& rhs) { return ( width == rhs.get_width() ); };

		private:
			int width;

			static PulseWidthCommandGrammar * class_grammar;
	};
};

#endif
