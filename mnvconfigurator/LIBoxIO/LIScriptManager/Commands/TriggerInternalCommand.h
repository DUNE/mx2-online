#ifndef TRIGGERINTERNALCOMMAND_H
#define TRIGGERINTERNALCOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class TriggerInternalCommand : Command
	{
		public:
			inline bool Validate()	{ return true; }		// there are no parameters for a reset command so it's always valid.
			
			inline std::string ToString()    { InitializeStatics(); return std::string("aK"); };
			inline static std::string Description() { return std::string("Set triggering mode to 'internal'."); };
			
			bool operator==(const TriggerInternalCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		protected:
			static const CommandType commandType    = TRIGGER_INTERNAL;
			static const std::string tokenTemplate  = "aK";

	};
};

#endif
