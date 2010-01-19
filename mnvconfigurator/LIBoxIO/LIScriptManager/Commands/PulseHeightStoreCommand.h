#ifndef PULSEHEIGHTSTORECOMMAND_H
#define PULSEHEIGHTSTORECOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class PulseHeightStoreCommand : public Command
	{
		public:
			inline bool Validate()	{ return true; }		// there are no parameters for this command so it's always valid.
			
			inline std::string ToString()    { InitializeStatics(); return std::string("aO"); };
			inline static std::string Description() { return std::string("Stores the pulse height commands."); };
			
			bool operator==(const PulseHeightStoreCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		protected:
			static const CommandType commandType    = PULSE_HEIGHT_STORE;
			static const std::string tokenTemplate  = "aO";

	};
};

#endif
