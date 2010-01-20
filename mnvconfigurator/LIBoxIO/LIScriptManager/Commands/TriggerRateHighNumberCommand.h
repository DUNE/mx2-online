#ifndef TRIGGERRATEHIGHNUMBERCOMMAND_H
#define TRIGGERRATEHIGHNUMBERCOMMAND_H 1

#include "Command.h"
#include "TriggerRateHighNumberCommandGrammar.h"

#include <string>

namespace Minerva
{
	class TriggerRateHighNumberCommand : public Command
	{
		public:
			TriggerRateHighNumberCommand();
			
			inline bool Validate() { return (digit1 >= 0 && digit2 >= 0); };
			
			inline std::string ToString();
			inline std::string Describe() { return std::string("Sets the high number of the internal trigger rate."); };
			
			inline int  get_digit1() const                { return digit1; };
			inline int  get_digit2() const                { return digit2; };
			void set_digit1(int newDigit1);
			void set_digit2(int newDigit1);
			
			bool operator==(const TriggerRateHighNumberCommand& rhs) { return ( (digit1 == rhs.get_digit1()) && (digit2 == rhs.get_digit2()) ); };

		private:
			int digit1;
			int digit2;

			static TriggerRateHighNumberCommandGrammar * class_grammar;

	};
};

#endif
