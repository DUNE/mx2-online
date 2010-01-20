#ifndef COMMANDTYPES_H
#define COMMANDTYPES_H

namespace Minerva
{
	// DON'T change the values assigned in the enum (unless you want to change them to other, distinct powers of 2).
	// They need to be powers of 2 so that we can OR them together in requiredCommands entries in CommandBlocks.
	enum CommandType {
	                  RESET_COMMAND = 1,
	                  INITIALIZE_COMMAND = 2,
	                  LED_SELECTION_COMMAND = 4,
	                  PULSE_HEIGHT_HIGH_BIT_COMMAND = 8,
	                  PULSE_HEIGHT_LOW_BITS_COMMAND = 16,
	                  PULSE_HEIGHT_STORE_COMMAND = 32,
	                  PULSE_WIDTH_COMMAND = 64,
	                  TRIGGER_INTERNAL_COMMAND = 128,
	                  TRIGGER_EXTERNAL_COMMAND = 512,
	                  TRIGGER_RATE_HIGH_NUMBER_COMMAND = 1024,
	                  TRIGGER_RATE_LOW_NUMBER_COMMAND = 2048
	                  };

};

#endif
