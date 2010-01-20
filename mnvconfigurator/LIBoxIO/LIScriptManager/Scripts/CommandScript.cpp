#include "CommandScript.h"
#include "../../LIBoxExceptions.h"

#include <string>

namespace Minerva
{
	// --------------------------------------------------------------------
	// CommandScript::ValidCommand()
	//    the generic version.  throws an exception since derived classes
	//    should implement overloaded versions that accept specific
	//    command blocks (calling AddValidBlock()).
	// --------------------------------------------------------------------
	void CommandScript::AddBlock(CommandBlock * block)
	{
		if (grammar->ValidBlock(block))
			blocks.push_back(block);
		else			
			throw LIBoxBlockNotAllowedException();

		return;
	}
	
	// --------------------------------------------------------------------
	// CommandScript::Validate()
	//    derived classes may want to override this, but they don't have to.
	//    you may find that this is very similar to 
	//    CommandBlock::Validate()...
	// --------------------------------------------------------------------
	bool CommandScript::Validate()
	{
		// loop through the blocks contained in this script.
		// first, make a map of where they are.
		int position = 1;
		std::multimap<CommandBlockType, int> blockPlacement;
		for (std::vector<CommandBlock*>::iterator blockIt = blocks.begin(); blockIt != blocks.end(); blockIt++, position++)
		{
			CommandBlock * block = (*blockIt);
			blockPlacement.insert( std::pair<CommandBlockType, int>(block->get_commandBlockType(), position) );
		}
		
		//  (1) are all of the necessary blocks there?
		for (std::set<CommandBlockType>::const_iterator requirementIt = grammar->get_requiredBlocks().begin(); requirementIt != grammar->get_requiredBlocks().end(); requirementIt++)
		{
			CommandBlockType requirement = *requirementIt;

			bool reqSatisfied = false;
			for (std::vector<CommandBlock*>::iterator blockIt = blocks.begin(); blockIt != blocks.end(); blockIt++)
			{
				// note that the comparison is supposed to be a BITWISE 'and' (only one ampersand '&').
				// this is how we check if a block satisfies a requirement that has been 'OR'ed together
				// out of several individual requirements.
				if ( ((*blockIt)->get_commandBlockType()) & requirement > 0 )
				{
					reqSatisfied = true;
					break;
				}
			} // for (commandIt)
			
			if ( !reqSatisfied )
				return false;
		} // for (requirementIt)

		//  (2) are there too many of one kind of command?
		for (std::map<CommandBlockType, int>::const_iterator capIt = grammar->get_numAllowedBlocks().begin(); capIt != grammar->get_numAllowedBlocks().end(); capIt++)
		{
			CommandBlockType capType = (*capIt).first;
			int capNum = (*capIt).second;
			if ( blockPlacement.count(capType) > capNum )
				return false;
		}

		// each CommandBlock knows how to check a list of blocks to see if the list is compatible with it:
		//  (3) does it exclude any of the other blocks in the list?
		//  (4) are the right number of other blocks in the right places in the list?
		position = 1;
		for (std::vector<CommandBlock*>::iterator blockIt = blocks.begin(); blockIt != blocks.end(); blockIt++, position++)
		{
			CommandBlock * block = (*blockIt);
			if ( !block->CheckCompatibility(blockPlacement, position) )
				return false;
		}
				
		return true;
	} // CommandScript::Validate()
	
	// --------------------------------------------------------------------
	// CommandScript::ToString()
	//    derived classes may want to override this, but they don't have to.
	//    all it does right now is concatenate together the output 
	//    of the individual blocks' ToString() methods.
	// --------------------------------------------------------------------
	std::string CommandScript::ToString()
	{
		std::string out("");
		for (std::vector<CommandBlock*>::iterator blockIt = blocks.begin(); blockIt != blocks.end(); blockIt++)
		{
			CommandBlock * block = (*blockIt);
			out += block->ToString();
		}
			
		return out;
	}	
};
