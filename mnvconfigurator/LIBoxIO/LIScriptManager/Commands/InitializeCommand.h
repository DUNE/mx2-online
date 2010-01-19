#ifndef INITIALIZECOMMAND_H
#define INITIALIZECOMMAND_H 1

#include "Command.h"

#include <string>

namespace Minerva
{
	class InitializeCommand : public Command
	{
		public:
			inline bool Validate()	{ return true; }		// there are no parameters for a reset command so it's always valid.
			
			inline std::string ToString()    { return std::string("aA"); };
			inline static std::string Description() { return std::string("Initialize the LI box."); };
			
			bool operator==(const PulseHeightStoreCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		protected:
			static const CommandType commandType    = INITIALIZE;
			static const std::string tokenTemplate  = "aA";

	};
};

#endif
