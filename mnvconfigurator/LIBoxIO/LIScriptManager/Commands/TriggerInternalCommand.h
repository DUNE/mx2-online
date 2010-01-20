#ifndef TRIGGERINTERNALCOMMAND_H
#define TRIGGERINTERNALCOMMAND_H 1

#include "Command.h"
#include "TriggerInternalCommandGrammar.h"

#include <string>

namespace Minerva
{
	class TriggerInternalCommand : public Command
	{
		public:
			TriggerInternalCommand();
			
			inline bool Validate()	{ return true; };		// there are no parameters for a reset command so it's always valid.
			
			inline std::string ToString()    { return std::string("aK"); };
			inline std::string Describe() { return std::string("Set triggering mode to 'internal'."); };
			
			bool operator==(const TriggerInternalCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		private:
			static TriggerInternalCommandGrammar * class_grammar;

	};
};

#endif
