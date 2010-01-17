#include "CommandBlock.h"

#include <string>

namespace Minerva
{
	bool Command::TestString(std::string teststring)
	{
		if ( teststring.length() != tokenTemplate.length() )
			return false;
			
		for ( int i = 0; i < teststring.length(); i++ )
		{
			if ( (teststring[i] != tokenTemplate[i]) && (tokenTemplate[i] != '?') )
				return false;
		}
		
		return true;
	}
	

};
