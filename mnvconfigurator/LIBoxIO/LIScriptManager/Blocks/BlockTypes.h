#ifndef BLOCKTYPES_H
#define BLOCKTYPES_H 1

namespace Minerva
{

	// DON'T change the assigned values in the enum (unless you change them to other distinct powers of 2) -- you'll mess up boolean logic done in CommandScripts.
	enum CommandBlockType { RESET_BLOCK = 1, INITIALIZE_BLOCK = 2, LED_SELECTION_BLOCK = 4, TRIGGER_SETUP_BLOCK = 8, PULSE_SETUP_BLOCK = 16 };

};

#endif
