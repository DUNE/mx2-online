#ifndef TRIGGERRATEHIGHNUMBERCOMMAND_H
#define TRIGGERRATEHIGHNUMBERCOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class TriggerRateHighNumberCommand : public Command
	{
		public:
			TriggerRateHighNumberCommand();
			
			inline bool Validate() { return (digit1 >= 0 && digit2 >= 0); };
			
			inline std::string ToString();
			inline static std::string Description() { return std::string("Sets the high number of the internal trigger rate."); };
			
			inline int  get_digit1()                 { return digit1; };
			inline int  get_digit2()                 { return digit2; };
			void set_digit1(int newDigit1);
			void set_digit1(int newDigit1);
			
			bool operator==(const TriggerRateHighNumberCommand& rhs) { return ( (digit1 == rhs.get_digit1()) && (digit2 == rhs.get_digit2()); };

		protected:
			static const CommandType commandType    = TRIGGER_RATE_HIGH_NUMBER;
			static const std::string tokenTemplate  = std::string("aH??");'
			
		private:
			int digit1;
			int digit2;

	};
};

#endif
