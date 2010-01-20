#include "LEDSelectionCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	LEDSelectionCommandGrammar::LEDSelectionCommandGrammar()
	{
		tokenTemplate = std::string("aE?");
	}
};
