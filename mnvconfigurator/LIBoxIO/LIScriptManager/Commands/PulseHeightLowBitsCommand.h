#ifndef PULSEHEIGHTLOWBITSCOMMAND_H
#define PULSEHEIGHTLOWBITSCOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class PulseHeightLowBitsCommand : public Command
	{
		public:
			PulseHeightLowBitsCommand();
			
			inline bool Validate() { return (lowBit1 >= 0 && lowBit2 >= 0); };
			
			inline std::string ToString();
			inline static std::string Description() { return std::string("Sets pulse height low bits."); };
			
			inline int  get_lowBit1()                 { return lowBit1; };
			inline int  get_lowBit2()                 { return lowBit2; };
			void set_lowBit1(int newLowBit1);
			void set_lowBit1(int newLowBit1);
			
			bool operator==(const PulseHeightLowBitsCommand& rhs) { return ( (lowBit1 == rhs.get_lowBit1()) && (lowBit2 == rhs.get_lowBit2()); };

		protected:
			static const CommandType commandType    = PULSE_HEIGHT_HIGH_BIT;
			static const std::string tokenTemplate  = std::string("aC?_?");'
			
		private:
			int lowBit1;
			int lowBit2;

	};
};

#endif
