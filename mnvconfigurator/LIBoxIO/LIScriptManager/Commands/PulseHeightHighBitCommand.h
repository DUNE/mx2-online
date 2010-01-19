#ifndef PULSEHEIGHTHIGHBITCOMMAND_H
#define PULSEHEIGHTHIGHBITCOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class PulseHeightHighBitCommand : public Command
	{
		public:
			PulseHeightHighBitCommand();
			
			inline bool Validate() { return (highBit >= 0); };
			
			inline std::string ToString();
			inline static std::string Description() { return std::string("Sets pulse height high bit."); };
			
			inline int get_highBit()                 { return highBit; };
			void  set_highBit(int newHighBit);
			
			bool operator==(const PulseHeightHighBitCommand& rhs) { return ( highBit == rhs.get_highBit() ); };

		protected:
			static const CommandType commandType    = PULSE_HEIGHT_HIGH_BIT;
			static const std::string tokenTemplate  = std::string("aB?");'
			
		private:
			int highBit;

	};
};

#endif
