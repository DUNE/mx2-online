#include "Command.h"
#include "../Blocks/CommandBlock.h"

#include "../LIScriptExceptions.h"

#include <iostream>
#include <string>
#include <map>
#include <set>

namespace Minerva
{
	bool Command::CheckCompatibility( const std::multimap<CommandType, int> & positionList, int myPosition )
	{
		// first check the exclusions.
		std::map<int, CommandType> positionMap;
		for (std::multimap<CommandType, int>::const_iterator commandIt = positionList.begin(); commandIt != positionList.end(); commandIt++)
		{
			CommandType cmdType = (*commandIt).first;
			int position = (*commandIt).second;
			
			// if any of the commands in the list are excluded by my command we know this list is incompatible.  don't look any further.
			if ( grammar->get_excludedCommands().find(cmdType) != grammar->get_excludedCommands().end() )
			{
				throw LIScriptCommandExcludedException(commandType, cmdType, position);
				return false;
			}
			
			// we'll need the multimap inverted for the next checking step.
			positionMap.insert( std::pair<int, CommandType>(position, cmdType) );
		}
		
		// check the requirements.
		for (std::map<CommandType, int>::const_iterator requirementIt = grammar->get_requiredCommands().begin(); requirementIt != grammar->get_requiredCommands().end(); requirementIt++)
		{
			CommandType cmdType = (*requirementIt).first;
			int positionOffset = (*requirementIt).second;

			
			// if the position is unimportant, all that we have to have is that the required command be in the list somewhere.
			//      if it isn't, we know this list isn't compatible. 
			// otherwise, check that the right kind of command is in the right place.
			if (positionOffset == 0)
			{
				if (positionList.count(cmdType) == 0)
				{
					throw LIScriptMissingRequiredCommandException(commandType, cmdType);
					return false;
				}
			}
			else
			{
				int position = myPosition + positionOffset;
				if ( position < 1 || position > positionMap.size() )		// if the list isn't big enough to contain the required elements.
				{
					throw LIScriptCommandListTooSmallException(commandType);
					return false;
				}
				if ( positionMap[position] != cmdType )
				{
					throw LIScriptCommandOutOfPlaceException(commandType, cmdType, positionMap[position], position);
					return false;
				}
			}
		}

		return true;
	}
	

};
