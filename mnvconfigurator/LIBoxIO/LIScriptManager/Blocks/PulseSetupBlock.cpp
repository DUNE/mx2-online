#include "PulseSetupBlock.h"
#include "PulseSetupBlockGrammar.h"

#include "../Commands/Command.h"

#include <vector>
#include <iostream>

namespace Minerva
{
	// have to initialize static members outside class declaration
	PulseSetupBlockGrammar * PulseSetupBlock::class_grammar = NULL;

	PulseSetupBlock::PulseSetupBlock()
	{
		commandBlockType = PULSE_SETUP_BLOCK;
		
		if (PulseSetupBlock::class_grammar == NULL)
			PulseSetupBlock::class_grammar = new PulseSetupBlockGrammar;

		grammar = PulseSetupBlock::class_grammar;
	}

	bool PulseSetupBlock::Validate()
	{
		for (std::vector<Command*>::const_iterator it = commands.begin(); it != commands.end(); it++)
			std::cout << (*it)->get_commandType() << " ";
			
		std::cout << std::endl;
		
		return CommandBlock::Validate();
	}

};
