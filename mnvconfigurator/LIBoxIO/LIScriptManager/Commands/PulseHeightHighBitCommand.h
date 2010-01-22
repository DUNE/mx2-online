#ifndef PULSEHEIGHTHIGHBITCOMMAND_H
#define PULSEHEIGHTHIGHBITCOMMAND_H 1

#include "Command.h"
#include "PulseHeightHighBitCommandGrammar.h"

#include <string>

namespace Minerva
{
	class PulseHeightHighBitCommand : public Command
	{
		public:
			PulseHeightHighBitCommand(int highBit = -1);
			
			inline bool Validate() { return (highBit >= 0); };
			
			std::string ToString();
			inline std::string Describe() { return std::string("Sets pulse height high bit."); };
			
			inline int get_highBit() const                        { return highBit; };
			void  set_highBit(int newHighBit);
			
			bool operator==(const PulseHeightHighBitCommand& rhs) { return ( highBit == rhs.get_highBit() ); };

		private:
			int highBit;
			
			static PulseHeightHighBitCommandGrammar * class_grammar;

	};
};

#endif
