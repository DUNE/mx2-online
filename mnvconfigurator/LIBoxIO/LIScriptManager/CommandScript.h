#ifndef COMMANDSCRIPT_H
#define COMMANDSCRIPT_H 1

#include "CommandStructure.h"
#include "
#include <string>

namespace Minerva
{
	class CommandScript: public CommandStructure
	{
		public:
			virtual bool Validate() = 0;
			virtual std::string ToString() = 0;
			virtual static std::string Description() = 0;
			
			// this is the generic version.  
			// it will throw an exception because the derived classes should implement overloaded versions
			// for valid blocks to add.
			// note that this is NOT virtual because it is not expected to be reimplemented.
			bool AddBlock(CommandBlock * block);
	};
};

#endif
