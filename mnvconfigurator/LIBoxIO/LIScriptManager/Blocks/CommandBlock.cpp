#include "CommandBlock.h"
#include "../Commands/Command.h"
#include "../../LIBoxExceptions.h"

#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	// the 'catch-all' generic version.  derived classes will implement
	// versions for specific types of Commands which return true.
	CommandBlock::ValidCommand(Command * command)
	{
		return false; 
	}
	
	// again, a 'catch-all'.  derived classes will implement their own
	// versions for any commands that are allowed to be added.
	void CommandBlock::AddCommand(Command * command)
	{
		throw LIBoxCommandNotAllowedException;
	}
	
	bool CommandBlock::Validate()
	{
		// loop through the commands contained in this block.
		//  (1) are all of the necessary ones there?
		//  (2) are there too many of one kind of command?
		//  (3) do any of the commands exclude one another?
		//  (4) are all of the commands' requirements satisfied?
		int position = 1;
		std::multimap<CommandType, int> commandPlacement;
		for (std::vector<Command*> commandIt = commands.begin(); commandIt != commands.end(); commandIt++, position++)
		{
			Command * command = (*commandIt);
			commandPlacement.insert( std::pair<CommandType, int>(command->get_commandType, position) );
		}
		
		for (std::vector<CommandType>::iterator requirementIt = requiredCommands.begin(); requirementIt != requiredCommands.end(); requirementIt++)
		{
			CommandType requirement = *requirementIt;
			if ( commandPlacement.count(requirement) == 0 )
				return false;
		}

		for (std::map<CommandType, int>::iterator capIt = numAllowedCommands.begin(); capIt != numAllowedCommands.end(); capIt++)
		{
			CommandType capType = (*capIt).first;
			int capNum = (*capIt).second;
			if ( commandPlacement.count(capType) > capNum )
				return false;
		}

		// each Command knows how to check a list of commands to see if the list is compatible with it ( (3) and (4) above ).
		position = 1;
		for (std::vector<Command*> commandIt = commands.begin(); commandIt != commands.end(); commandIt++, position++)
			if ( !command.CheckCompatibility(commandPlacement, position) )
				return false;
				
		return true;
	} // CommandBlock::Validate()
	
	void CommandBlock::AddValidCommand(Command * command)
	{
		commands.push_back(command);
		
		return;
	}
	
	// note that derived classes may wish to override this ....
	// default behavior is just to concatenate the various commands within the block together,
	// separated by newlines.
	std::string CommandBlock::ToString()
	{
		std::string out;
		for ( std::vector<Command*>::const_iterator commandIt = commands.begin(); commandIt != commands.end(); commandIt++)
			out += (*commandIt)->ToString() + "\n";
			
		return out;
	}
};
