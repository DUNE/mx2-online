#ifndef PULSEHEIGHTSTORECOMMAND_H
#define PULSEHEIGHTSTORECOMMAND_H 1

#include "Command.h"
#include "PulseHeightStoreCommandGrammar.h"

#include <string>

namespace Minerva
{
	class PulseHeightStoreCommand : public Command
	{
		public:
			PulseHeightStoreCommand();
		
			inline bool Validate()	{ return true; }		// there are no parameters for this command so it's always valid.
			
			inline std::string ToString()    { return std::string("aO"); };
			inline std::string Describe() { return std::string("Stores the pulse height commands."); };
			
			bool operator==(const PulseHeightStoreCommand& rhs) { return true; };		// again, no parameters, so two of these are always equal.

		private:
			static PulseHeightStoreCommandGrammar * class_grammar;
	};
};

#endif
