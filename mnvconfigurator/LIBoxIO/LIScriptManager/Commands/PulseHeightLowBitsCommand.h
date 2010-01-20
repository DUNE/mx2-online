#ifndef PULSEHEIGHTLOWBITSCOMMAND_H
#define PULSEHEIGHTLOWBITSCOMMAND_H 1

#include "Command.h"
#include "PulseHeightLowBitsCommandGrammar.h"

#include <string>

namespace Minerva
{
	class PulseHeightLowBitsCommand : public Command
	{
		public:
			PulseHeightLowBitsCommand();
			
			inline bool Validate() { return (lowBit1 >= 0 && lowBit2 >= 0); };
			
			std::string ToString();
			inline std::string Description() { return std::string("Sets pulse height low bits."); };
			
			inline int  get_lowBit1() const                 { return lowBit1; };
			inline int  get_lowBit2() const                 { return lowBit2; };
			void set_lowBit1(int newLowBit1);
			void set_lowBit2(int newLowBit2);
			
			bool operator==(const PulseHeightLowBitsCommand& rhs) { return ( (lowBit1 == rhs.get_lowBit1()) && (lowBit2 == rhs.get_lowBit2()) ); };

		private:
			int lowBit1;
			int lowBit2;

			static PulseHeightLowBitsCommandGrammar * class_grammar;
	};
};

#endif
