#ifndef INITIALIZECOMMAND_H
#define INITIALIZECOMMAND_H 1

#include "Command.h"
#include "InitializeCommandGrammar.h"

#include <string>

namespace Minerva
{
	class InitializeCommand : public Command
	{
		public:
			InitializeCommand();
		
			inline bool Validate()	        { return true; }		// there are no parameters for an initialization command so it's always valid.
			
			inline std::string ToString()    { return std::string("aA"); };
			inline std::string Describe()    { return std::string("Initialize the LI box."); };
			
			inline bool operator==(const InitializeCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		private:
			static InitializeCommandGrammar * class_grammar;
	};
};

#endif
