#include "CommandScript.h"
#include "LIBoxExceptions.h"

namespace Minerva
{
	// the generic version.  throws an exception (see  CommandScript.h)
	bool CommandScript::AddBlock(CommandBlock * block)
	{
		throw LIBoxCommandBlockException;
	}

};
