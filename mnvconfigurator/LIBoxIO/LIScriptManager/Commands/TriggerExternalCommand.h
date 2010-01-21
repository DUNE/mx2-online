#ifndef TRIGGEREXTERNALCOMMAND_H
#define TRIGGEREXTERNALCOMMAND_H 1

#include "Command.h"
#include "TriggerExternalCommandGrammar.h"

#include <string>

namespace Minerva
{
	class TriggerExternalCommand : public Command
	{
		public:
			TriggerExternalCommand();
			
			inline bool Validate()	{ return true; }		// there are no parameters for this command so it's always valid.
			
			inline std::string ToString()    { return std::string("aQ"); };
			inline std::string Describe()    { return std::string("Set external trigger mode."); };
			
			bool operator==(const TriggerExternalCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		private:
			static TriggerExternalCommandGrammar * class_grammar;

	};
};

#endif
