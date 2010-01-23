#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>


#include "../getoptpp/getopt_pp.h"
#include "LIScriptManager.h"

using namespace std;

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
		
		Minerva::LIScriptManager manager;
		manager.set_fileName(filename);
		
		if (mode == "create" || mode == "verify")
		{
			bool   noInitialization;
			bool   noPulseConfig;
			float  pulseHeight;
			int    pulseWidth;
			bool   noLEDconfig;
			string LEDgroup;
			bool   noTriggerConfig;
			bool   triggerInternal;
			int    triggerRate;
			bool   requireResponse;
			string responseRequired;
			string responseSeparator;
			bool   includeReset;
			
			noInitialization = ( opts >> GetOpt::OptionPresent('I', "no-initialization")                             );
			noPulseConfig    = ( opts >> GetOpt::OptionPresent('P', "no-pulse-config")                               );
			opts >>                      GetOpt::Option       ('h', "pulse-height",       pulseHeight,        12.07f );
			opts >>                      GetOpt::Option       ('w', "pulse-width",        pulseWidth,         7      );
			noLEDconfig      = ( opts >> GetOpt::OptionPresent('P', "no-LED-config")                                 );
			opts >>                      GetOpt::Option       ('l', "LED-groups",         LEDgroup,           "ABCD" );
			noTriggerConfig  = ( opts >> GetOpt::OptionPresent('T', "no-trigger-config")                             );
			triggerInternal  = ( opts >> GetOpt::OptionPresent('N', "trigger-internal")                              );
			opts >>   std::hex        >> GetOpt::Option       ('r', "trigger-rate",       triggerRate,        0x0220 );
			requireResponse  = ( opts >> GetOpt::OptionPresent('R', "require-response")                              );
			opts >>                      GetOpt::Option       ('t', "response-required",  responseRequired,   ""     );
			opts >>                      GetOpt::Option       ('s', "response-separator", responseSeparator,  ":"    );
			includeReset     = ( opts >> GetOpt::OptionPresent('X', "include-reset")                                 );
			
			manager.set_noInitialization     (noInitialization);
			manager.set_noPulseConfig        (noPulseConfig);
			manager.set_pulseHeight          (pulseHeight);
			manager.set_pulseWidth           (pulseWidth);
			manager.set_noLEDconfig          (noLEDconfig);
			manager.set_LEDgroup             (LEDgroup);
			manager.set_noTriggerConfig      (noTriggerConfig);
			manager.set_triggerInternal      (triggerInternal);
			manager.set_triggerRateLowNumber (triggerRate % 0x100);
			manager.set_triggerRateHighNumber(triggerRate / 0x100);
			manager.set_requireResponse      (requireResponse);
			manager.set_responseRequired     (responseRequired);
			manager.set_responseSeparator    (responseSeparator);
			manager.set_doReset              (includeReset);
			
			manager.Create();
			
		}
		else if (mode == "validate" || mode == "describe")
		{}
		else
		{
			cerr << "Invalid command." << endl;
			optsOkay = false;
		}

		if (opts.options_remain())
			optsOkay = false;
	}
	
	if (!optsOkay)
	{
		showUsage();
		cerr << "Invalid command line." << endl;
		return 1;
	}
	
	return 0;
}

void showUsage()
{
	cerr << "\n"
	     << "usage: LIScriptManager <command> [options]\n"
	     << "commands:\n"
	     << "  create   <scriptname>              create a new LI box script.  see options below.\n"
	     << "  validate <scriptname>              check an LI box script for errors.\n"
	     << "                                        (not yet implemented.)\n"
	     << "  describe <scriptname>              write out the actions corresponding to\n"
	     << "                                        each command in the script.  (not yet implemented.)\n"
	     << "  verify   <scriptname>              check if a script corresponds to the parameters\n"
	     << "                                        passed on the command line.  (not yet implemented.)\n"
		<< "\n"
	     << "options:\n"
	     << "  -h, --pulse-height       <pulse height>  pulse height of pulse (in volts), 4.05-12.07.\n"
	     << "                                              default: 12.07.\n"
	     << "  -w, --pulse-width        <pulse width>   pulse width, 0-7 (roughly 20-35 ns).\n"
	     << "                                              default: 7.\n"
	     << "  -l, --LED-groups         <LED groups>    which LED groups should be active (of A, B, C, D).\n"
	     << "                                              default: all LEDs (ABCD).\n"
	     << "  -r, --trigger-rate       <rate>          trigger rate for internal triggering (4 hex digits).\n"
	     << "                                              2 'high' digits (a 'multiplier') and 2 low digits.\n"
	     << "                                              only included for INTERNAL triggering.\n"
	     << "                                              default: 0x0220.\n"
	     << "      --require-response                   whether to wait for a response from the LI box\n"
	     << "                                              after each command is issued.\n"
	     << "                                              (see '--response-required' below.)\n"
	     << "  -t, --response-required  <response>      what response to wait for after commands\n"
	     << "                                              are issued.\n"
	     << "                                              default: \"\" (no response).\n"
	     << "  -s, --response-separator <separator>     what character(s) to use as the separator between\n"
	     << "                                              LI box commands and the response required.\n"
	     << "                                              default: \":\".\n"
	     << "      --no-initialization                  don't include an 'initialize' command\n"
	     << "                                              at the beginning.\n"
	     << "      --no-pulse-config                    don't include the pulse configuration (height, width)\n"
	     << "                                              commands in the script.\n"
	     << "      --trigger-internal                   if the triggering is INTERNAL.  (for EXTERNAL\n"
	     << "                                              triggering just don't include this option.)\n"
	     << "      --no-trigger-config                  don't include the trigger configuration block\n"
	     << "                                              (internal/external, rate) in the script.\n"
	     << "      --no-LED-config                      don't include the LED group selection command\n"
	     << "                                              in the script.\n"
	     << "      --include-reset                      whether to include a 'reset' command at the end.\n"
	     << endl;

	return;
}
