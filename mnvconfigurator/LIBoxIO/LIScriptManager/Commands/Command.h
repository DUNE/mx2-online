#ifndef COMMAND_H
#define COMMAND_H

#include "CommandStructure.h"

#include <string>
#include <map>
#include <set>

namespace Minerva
{
	enum CommandType { RESET, INITIALIZE, LED_SELECTION, PULSE_HEIGHT_HIGH_BIT, PULSE_HEIGHT_LOW_BITS, PULSE_HEIGHT_STORE, PULSE_WIDTH, TRIGGER_INTERNAL, TRIGGER_EXTERNAL, TRIGGER_RATE_HIGH_NUMBER, TRIGGER_RATE_LOW_NUMBER };

	class Command : public CommandStructure
	{
		public:
			virtual std::string        ToString()    = 0;
			static virtual std::string Description() = 0;
			
			virtual bool Validate()                  = 0;			
			static bool  TestString(std::string teststring);	// tests if a string matches the right pattern for this command.
			
			static CommandType get_CommandType() { return commandType; };
			static bool        CheckCompatibility( const std::multimap<CommandType, int> & positionList, int myPosition );		// check if this command is compatible with a certain group
			
		protected:
			virtual static void InitializeStatics() = 0;		// initializes any static variables (like the ones below) that can't be initialized here (like ones with std::maps, std::vectors, etc.)
			static bool initialized = false;

			// the grammar for the command type.
			// derived classes will use these to specify
			// what kind of other commands it's compatible with.
			//
			// the actual initialization of these is done in InitializeStatics().
			static std::map<CommandType, int>    requiredCommands;
			static std::set<CommandType>      excludedCommands;
			
			static const CommandType commandType;
			static const std::string tokenTemplate;
	};
};
