#ifndef COMMAND_H
#define COMMAND_H 1

#include "CommandTypes.h"
#include "../CommandStructure.h"
#include "CommandGrammar.h"

#include <string>
#include <map>

namespace Minerva
{

	class Command : public CommandStructure
	{
		public:
			virtual              ~Command() {};
		
			virtual std::string  ToString() = 0;
			virtual std::string  Describe() = 0;
			
			virtual bool         Validate() = 0;
			bool                 CheckCompatibility( const std::multimap<CommandType, int> & positionList, int myPosition );

			inline CommandType   get_commandType() { return commandType; };
			
		protected:
			CommandGrammar * grammar;
			
			CommandType commandType;
	};
};

#endif
