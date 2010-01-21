#ifndef COMMANDBLOCK_H
#define COMMANDBLOCK_H 1

#include "BlockTypes.h"
#include "../CommandStructure.h"
#include "../Commands/Command.h"
#include "BlockGrammar.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{

	class CommandBlock : public CommandStructure
	{
		public:
			virtual ~CommandBlock() {};
		
			virtual std::string  ToString();
			virtual std::string  Describe()      = 0;
			
			bool Validate();		
			bool AddValidCommand(Command * command);	
			void AddCommand(Command * command);
			bool CheckCompatibility( const std::multimap<CommandBlockType, int> & positionList, int myPosition );

			CommandBlockType get_commandBlockType() { return commandBlockType; };

		protected:
			BlockGrammar * grammar;
			
			std::vector<Command *> commands;
			
			CommandBlockType commandBlockType;
	};

};

#endif
