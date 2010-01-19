#include "CommandBlock.h"

#include <string>
#include <map>
#include <set>

namespace Minerva
{
	bool Command::TestString(std::string teststring)
	{
		InitializeStatics();
		
		if ( teststring.length() != tokenTemplate.length() )
			return false;
			
		for ( int i = 0; i < teststring.length(); i++ )
		{
			if ( (teststring[i] != tokenTemplate[i]) && (tokenTemplate[i] != '?'))
				return false;
		}
		
		return true;
	}
	
	bool Command::CheckCompatibility( const std::multimap<CommandType, int> & positionList, int myPosition )
	{
		// first check the exclusions.
		std::map<int, CommandType> positionMap;
		for (std::multimap<CommandType, int>::const_iterator commandIt = positionList.begin(); commandIt != positionList.end(); commandIt++)
		{
			CommandType commandType = (*commandIt).first;
			int position = (*commandIt).second;
			
			// if any of the commands in the list are excluded by my command we know this list is incompatible.  don't look any further.
			if ( excludedCommands.find(commandType) != excludedCommands.end() )
				return false;
			
			// we'll need the multimap inverted for the next checking step.
			positionMap.insert( std::pair<int, CommandType>(position, commandType) );
		}
		
		// check the requirements.
		for (std::map<CommandType, int>::iterator requirementIt = requiredCommands.begin(); requirementIt != requiredCommands.end(); requirementIt++)
		{
			CommandType commandType = (*requirementIt).first;
			int positionOffset = (*requirementIt).second;
			
			// if the position is unimportant, all that we have to have is that the required command be in the list somewhere.
			//      if it isn't, we know this list isn't compatible. 
			// otherwise, check that the right kind of command is in the right place.
			if (positionOffset == 0 && positionList.count(commandType) == 0)
				return false;
			else
			{
				int position = myPosition + positionOffset;
				if ( position < 1 || position > positionMap.size() )		// if the list isn't big enough to contain the required elements.
					return false;
				if ( positionMap[position] != commandType )
					return false;
			}
		}

		return true;
	}
	

};
