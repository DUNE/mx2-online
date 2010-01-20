#include "ResetCommandGrammar.h"
#include "Command.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	ResetCommandGrammar::ResetCommandGrammar()
	{
		tokenTemplate = std::string("_X");
	}
};
