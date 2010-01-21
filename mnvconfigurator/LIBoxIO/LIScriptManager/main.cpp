#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>


#include "../getoptpp/getopt_pp.h"

using namespace std;

void other();
void showUsage();

int main (int argc, char ** argv)
{
	// GetOpt parses command-line options for me.
	GetOpt::GetOpt_pp opts(argc, argv);

	bool optsOkay = true;

	vector<string> commands;

	opts >> GetOpt::Option(GetOpt::GetOpt_pp::EMPTY_OPTION, commands); 
	
	// check the commands.  always need the mode & a filename.
	if (commands.size() != 2)
		optsOkay = false;
	
	if (optsOkay)
	{
		vector<string>::iterator command = commands.begin();
		string mode = (*command);
		transform(mode.begin(), mode.end(), mode.begin(), ::tolower); 	// convert the mode to lower case for easy checking
		
		string filename = *(++command);
		
		if (mode == "create" || mode == "verify")
		{
			float  pulseHeight;
			int    pulseWidth;
			string LEDgroup;
			bool   triggerInternal;
			string triggerRate;
			bool   requireResponse;
			string responseRequired;
			string responseSeparator;
			
			opts >>                     GetOpt::Option       ('h', "pulse-height",       pulseHeight,        12.07f );
			opts >>                     GetOpt::Option       ('w', "pulse-width",        pulseWidth,         7      );
			opts >>                     GetOpt::Option       ('l', "ledgroup",           LEDgroup,           "ABCD" );
			triggerInternal = ( opts >> GetOpt::OptionPresent('I', "trigger-internal")                              );
			opts >>                     GetOpt::Option       ('r', "trigger-rate",       triggerRate,        "0220" );
			requireResponse = ( opts >> GetOpt::OptionPresent('R', "require-response")                              );
			opts >>                     GetOpt::Option       ('t', "response-required",  responseRequired,   ""     );
			opts >>                     GetOpt::Option       ('s', "response-separator", responseSeparator,  ":"    );
			
			
		}
		else if (mode == "validate" || mode == "describe")
		{
			if (opts.options_remain())
				optsOkay = false;
		}
		else
		{
			cerr << "Invalid command." << endl;
			optsOkay = false;
		}
	}
	
	if (!optsOkay)
	{
		showUsage();
		cerr << "Invalid command line." << endl;
		return 1;
	}
	
	return 0;
}

void other()
{
		float pulseHeight = 0;
		
		// note that the two following integer type casts TRUNCATE the decimal parts (they don't round).
		int highBit = int( (pulseHeight - 4.0429) / 2.01 );
		int lowBit = int( (pulseHeight - highBit * 2.01 - 4.0429) / .00783 );

          // Converting the low bit into a pair of HEX values
		int lowBit1 = lowBit / 16;		// INTEGER division.
		int lowBit2 = lowBit % 16;
}

void showUsage()
{
	cerr << "\n"
	     << "usage: LIScriptManager <command> [options]\n"
	     << "commands:\n"
	     << "  create   <scriptname>             create a new LI box script.  see options below.\n"
	     << "  validate <scriptname>             check an LI box script for errors.\n"
	     << "  describe <scriptname>             write out the actions corresponding to\n"
	     << "                                       each command in the script.\n"
	     << "  verify   <scriptname>             check if a script corresponds to the parameters\n"
	     << "                                       passed on the command line.\n"
		<< "\n"
	     << "options:\n"
	     << "  -h, --pulse-height <pulseheight>  pulse height of pulse.\n"
	     << endl;

	return;
}
