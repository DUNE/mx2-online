#include "CommandBlock.h"
#include "../Commands/Command.h"
#include "../LIScriptExceptions.h"

#include <iostream>
#include <string>
#include <vector>
#include <map>

namespace Minerva
{
	// --------------------------------------------------------------------
	// CommandBlock::AddComand()
	//   throws an exception if this command is incompatible
	//   with the TYPES specified in the grammar, but doesn't check
	//   if adding the command violates the other rules.
	//   usually you should use AddValidCommand() instead.
	// --------------------------------------------------------------------
	void CommandBlock::AddCommand(Command * command)
	{
		if (grammar->ValidCommand(command))
			commands.push_back(command);
		else
			throw LIScriptCommandNotAllowedException();
	}
	
	// --------------------------------------------------------------------
	// CommandBlock::AddValidComand()
	//    tries adding the command and uses Validate() to see if it's ok.
	//    catches exceptions so that it can return a boolean corresponding
	//    to whether or not the command was successfully added.
	// --------------------------------------------------------------------
	bool CommandBlock::AddValidCommand(Command * command)
	{
		if (!grammar->ValidCommand(command))
			return false;
			
		commands.push_back(command);
		
		try
		{
			Validate();
		}
		catch (LIScriptException e)
		{
			commands.pop_back();
			return false;
		}
		
		return true;
	}
	
	// --------------------------------------------------------------------
	// CommandBlock::Validate()
	// --------------------------------------------------------------------
	bool CommandBlock::Validate()
	{
		// loop through the commands contained in this block.
		// first, make a map of where they are.
		int position = 1;
		std::multimap<CommandType, int> commandPlacement;
		for (std::vector<Command*>::iterator commandIt = commands.begin(); commandIt != commands.end(); commandIt++, position++)
		{
			Command * command = (*commandIt);
			commandPlacement.insert( std::pair<CommandType, int>(command->get_commandType(), position) );
		}
		
		//  (1) are all of the necessary ones there?
		for (std::set<CommandType>::const_iterator requirementIt = grammar->get_requiredCommands().begin(); requirementIt != grammar->get_requiredCommands().end(); requirementIt++)
		{
			CommandType requirement = *requirementIt;

			bool reqSatisfied = false;
			for (std::vector<Command*>::iterator commandIt = commands.begin(); commandIt != commands.end(); commandIt++)
			{
				// note that the comparison is supposed to be a BITWISE 'and' (only one ampersand '&').
				// this is how we check if a command satisfies a requirement that has been 'OR'ed together
				// out of several individual requirements.
				int matches = ((*commandIt)->get_commandType()) & requirement;
				if ( matches > 0 )
				{
					reqSatisfied = true;
					break;
				}
				
			} // for (commandIt)
			
			if ( !reqSatisfied )
			{
				throw LIScriptBlockCommandRequirementNotSatisfied(commandBlockType, requirement);
				return false;
			}
		} // for (requirementIt)

		//  (2) are there too many of one kind of command?
		for (std::map<CommandType, int>::const_iterator capIt = grammar->get_numAllowedCommands().begin(); capIt != grammar->get_numAllowedCommands().end(); capIt++)
		{
			CommandType capType = (*capIt).first;
			int capNum = (*capIt).second;
			if ( commandPlacement.count(capType) > capNum )
			{
				throw LIScriptBlockTooManyCommands(commandBlockType, capType, capNum);
				return false;
			}
		}

		// each Command knows how to check a list of commands to see if the list is compatible with it:
		//  (3) does it exclude any of the other commands in the list?
		//  (4) are the right number of other commands in the right places in the list?
		position = 1;
		for (std::vector<Command*>::iterator commandIt = commands.begin(); commandIt != commands.end(); commandIt++, position++)
		{
			Command * command = (*commandIt);
			if ( !command->CheckCompatibility(commandPlacement, position) )
			{
				throw LIBoxCommandNotCompatibleException(commandBlockType, command->get_commandType());
				return false;
			}
		}
				
		return true;
	} // CommandBlock::Validate()
	
	// --------------------------------------------------------------------
	// CommandBlock::CheckCompatibility
	//    if it seems strikingly similar to Command::CheckCompatibility,
	//    that's not an accident...
	// --------------------------------------------------------------------
	bool CommandBlock::CheckCompatibility( const std::multimap<CommandBlockType, int> & positionList, int myPosition )
	{
		// first check the exclusions.
		std::map<int, CommandBlockType> positionMap;
		for (std::multimap<CommandBlockType, int>::const_iterator blockIt = positionList.begin(); blockIt != positionList.end(); blockIt++)
		{
			CommandBlockType blockType = (*blockIt).first;
			int position = (*blockIt).second;
			
			// if any of the blocks in the list are excluded by my block we know this list is incompatible.  don't look any further.
			if ( grammar->get_excludedBlocks().find(blockType) != grammar->get_excludedBlocks().end() )
				return false;
			
			// we'll need the multimap inverted for the next checking step.
			positionMap.insert( std::pair<int, CommandBlockType>(position, blockType) );
		}
		
		// check the requirements.
		for (std::map<CommandBlockType, int>::const_iterator requirementIt = grammar->get_requiredBlocks().begin(); requirementIt != grammar->get_requiredBlocks().end(); requirementIt++)
		{
			CommandBlockType blockType = (*requirementIt).first;
			int positionOffset = (*requirementIt).second;
			
			// if the position is unimportant, all that we have to have is that the required block be in the list somewhere.
			//      if it isn't, we know this list isn't compatible. 
			// otherwise, check that the right kind of block is in the right place.
			if (positionOffset == 0 )
			{
				if (positionList.count(blockType) == 0)
					return false;
			}
			else
			{
				int position = myPosition + positionOffset;
				if ( position < 1 || position > positionMap.size() )		// if the list isn't big enough to contain the required elements.
					return false;
				if ( positionMap[position] != blockType )
					return false;
			}
		}

		return true;
	} // CommandBlock::CheckCompatibility

	
	// --------------------------------------------------------------------
	// CommandBlock::ToString()
	//    note that derived classes may wish to override this ....
	//    default behavior is just to concatenate the various commands within the block together,
	//    separated by newlines.
	// --------------------------------------------------------------------
	std::string CommandBlock::ToString()
	{
		if (	! Validate() )
			throw LIScriptInvalidBlockException(commandBlockType);
		
		std::string out;
		for ( std::vector<Command*>::const_iterator commandIt = commands.begin(); commandIt != commands.end(); commandIt++)
			out += (*commandIt)->ToString() + "\n";
			
		return out;
	}
}; // namespace Minerva
