#ifndef TRIGGEREXTERNALCOMMAND_H
#define TRIGGEREXTERNALCOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class TriggerExternalCommand : Command
	{
		public:
			inline bool Validate()	{ return true; }		// there are no parameters for a reset command so it's always valid.
			
			inline std::string ToString()    { return std::string("aQ"); };
			inline static std::string Description() { return std::string("Set external trigger mode."); };
			
			bool operator==(const TriggerExternalCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		protected:
			static const CommandType commandType    = TRIGGER_EXTERNAL;
			static const std::string tokenTemplate  = "aQ";

	};
};

#endif
