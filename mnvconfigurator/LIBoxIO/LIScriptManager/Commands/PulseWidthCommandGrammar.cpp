#include "PulseWidthCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	PulseWidthCommandGrammar::PulseWidthCommandGrammar()
	{
		tokenTemplate = std::string("aD?");
	}
};
