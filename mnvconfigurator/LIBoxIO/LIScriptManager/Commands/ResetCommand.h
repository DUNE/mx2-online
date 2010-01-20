#ifndef RESETCOMMAND_H
#define RESETCOMMAND_H 1

#include "Command.h"
#include "ResetCommandGrammar.h"

#include <string>

namespace Minerva
{
	class ResetCommand : Command
	{
		public:
			ResetCommand();
		
			inline bool Validate()	{ return true; }		// there are no parameters for a reset command so it's always valid.
			
			inline std::string ToString()    { return std::string("_X"); };
			inline static std::string Description() { return std::string("Soft reset for the LI box."); };
			
			bool operator==(const ResetCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		private:
			static ResetCommandGrammar * class_grammar;

	};
};

#endif
