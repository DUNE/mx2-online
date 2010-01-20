#ifndef TRIGGERRATELOWNUMBERCOMMAND_H
#define TRIGGERRATELOWNUMBERCOMMAND_H 1

#include "Command.h"
#include "TriggerRateLowNumberCommandGrammar.h"

#include <string>

namespace Minerva
{
	class TriggerRateLowNumberCommand : public Command
	{
		public:
			TriggerRateLowNumberCommand();
			
			inline bool Validate() { return (digit1 >= 0 && digit2 >= 0); };
			
			inline std::string ToString();
			inline std::string Describe() { return std::string("Sets the low number of the internal trigger rate."); };
			
			inline int  get_digit1() const                { return digit1; };
			inline int  get_digit2() const                { return digit2; };
			void set_digit1(int newDigit1);
			void set_digit2(int newDigit1);
			
			bool operator==(const TriggerRateLowNumberCommand& rhs) { return ( (digit1 == rhs.get_digit1()) && (digit2 == rhs.get_digit2()) ); };

		private:
			int digit1;
			int digit2;
			
			static TriggerRateLowNumberCommandGrammar * class_grammar;

	};
};

#endif
