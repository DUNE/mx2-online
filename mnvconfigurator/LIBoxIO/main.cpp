#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>

#include "getoptpp/getopt_pp.h"
#include "LIBoxIO.h"

using namespace std;

void showUsage();
void dumpValues(Minerva::LIBoxIO & liBox);

int main (int argc, char ** argv)
{
	// GetOpt parses command-line options for me.
	GetOpt::GetOpt_pp opts(argc, argv);
	
	bool optsOkay = true;
	
	string port = "";
	unsigned int baud = 0;
	unsigned int parity;
	unsigned int flowcontrol;
	unsigned int databits;
	unsigned int stopbits;
	string configfile;
	
	vector<string> commands;
	
	
	// parse the command line.
	// usage: LIBox <command> [options]
	// commands:
	//	arm					using the standard script, prepares the box for triggering via the pulser.
	//   disarm				using the standard script, sets the box to its idle state.
	//   runscript	<script>		run the LI box script indicated by <script>.
	// options:
	// 	-p, --port			<port>		port to use.  default: /dev/ttyS0
	// 	-b, --baud			<baud>		baud rate to use.  valid values: 1200, 2400, 4800, 9600, 19200, 38400, 57600.  default: 9600
	// 	-r, --parity			<parity>		use parity checking.  valid values: 0 ("none"), 1 ("odd"), 2 ("even").  default: 0
	// 	-f, --flow-control		<flow>		type of flow control to use.  valid values: 0 ("none"), 1 (hardware), or 2 (software).  default: 1
	//   -d, --data-bits		<data bits>	how many data bits to send at a time.  valid values: 1-8.  default: 8
	//   -s, --stop-bits		<stop bits>	how many stop bits to send.  valid values: 1-8.  default: 1
	//   -c, --config-file        <config-file>  the location of the configuration file.  default: /etc/LIBoxIO.conf
	opts >> GetOpt::Option('c',  "config-file", configfile, "/etc/LIBoxIO.conf");
	
	opts >> GetOpt::Option(GetOpt::GetOpt_pp::EMPTY_OPTION, commands); 
	
	// check the commands.  the options are checked by the setters of LIBoxIO, below (they throw exceptions if not specified correctly).
	if (commands.size() == 0)
		optsOkay = false;
	else
	{
		vector<string>::iterator command = commands.begin();
		if ( ! ( (( *command == "runscript" || *command == "issuecommand" ) && commands.size() == 2)
			    || ( (*command == "arm" || *command == "disarm") && commands.size() == 1) ) )
			optsOkay = false;
	}
	
	// create an instance of the LI box interface and set its properties.
	Minerva::LIBoxIO liBox(configfile);
	
	try
	{

		if (opts >> GetOpt::Option('p', "port", port))
			liBox.setSerialPortDev(port);
		if (opts >> GetOpt::Option('b', "baud", baud))
			liBox.setBaud(baud);
		if (opts >> GetOpt::Option('r', "parity", parity))
			liBox.setParity(parity);
		if (opts >> GetOpt::Option('f', "flow-control", flowcontrol))
			liBox.setFlowcontrol(flowcontrol);
		if (opts >> GetOpt::Option('d', "data-bits", databits))
			liBox.setDatabits(databits);
		if (opts >> GetOpt::Option('s', "stop-bits", stopbits))
			liBox.setStopbits(stopbits);
	}
	catch (invalid_argument & exc)
	{
		cerr << exc.what() << endl;
		optsOkay = false;
	}

	// inform the user if s/he didn't enter command-line stuff correctly and exit.
	if (!optsOkay)
	{
		showUsage();
		cerr << "Invalid command line." << endl;
		return 1;
	}

	
	// tell the LI box to do the thing specified by the user.
	try
	{
		string command = *(commands.begin());
		bool success;
		if (command == "arm")
			success = liBox.Arm();
		else if (command == "disarm")
			success = liBox.Disarm();
		else if (command == "runscript")
			success = liBox.RunScript( *(commands.begin() + 1) );		// the argument is the second element of the vector of strings
		else if (command == "issuecommand")
		{
			string arg = ( *(commands.begin() + 1) );
			string cmd;
			string resp;

			int loc = arg.find(":");
			if (loc == string::npos)
			{
				cerr << "Warning: response omitted: assuming you don't care what the response is..." << endl;
				cmd = arg;
				resp = "";
			}
			else
			{
				cmd.assign(arg, 0, loc);
				resp.assign(arg, loc+1, command.size() - (loc+1));
			}
			Minerva::IOPair commandPair = { cmd, resp };
			success = liBox.IssueSingleCommand ( commandPair );
		}

		if (opts >> GetOpt::OptionPresent('v', "verbose"))
			dumpValues(liBox);
	
		if (success)
			return 0;
		else
		{
			cerr << "Action failed..." << endl;
			return 1;
		}
	}
	catch (exception & e)
	{
		cerr << e.what() << endl;
		return 1;
	}
}

void showUsage()
{
	cout << "usage: LIBoxIO <command> [options]\n"
	     << "commands:\n"
	     << "  arm                                             prepares the box for triggering via the pulser.\n"
	     << "                                                     (uses the script specified in config-file)\n"
	     << "  disarm                                          returns the box to its idle state.\n"
	     << "                                                     (uses the script specified in config-file)\n"
	     << "  runscript               <script>                run the LI box script indicated by <script>.\n"
	     << "  issuecommand            <command>[:<response>]  send the single command <command> \n"
	     << "                                                     and optionally verify that <response> is received.\n"
	     << "options:\n"
	     << "  -b, --baud              <baud>                  baud rate to use.\n"
	     << "                                                     valid values:\n"
	     << "                                                       1200, 2400, 4800, 9600, 19200,\n"
	     << "                                                       38400, 57600, 115200.\n"
	     << "                                                     default: 9600\n"
	     << "  -d, --data-bits         <data bits>             how many data bits to send at a time.\n"
	     << "                                                     valid values: 5-8.\n"
	     << "                                                     default: 8\n"
	     << "  -f, --flow-control      <flow>                  type of flow control to use.\n"
	     << "                                                     valid values:\n"
	     << "                                                       0 (none), 1 (hardware), 2 (software).\n"
	     << "                                                     default: 1\n"
	     << "  -p, --port              <port>                  port to use.  default: /dev/ttyS0\n"
	     << "  -r, --parity            <parity>                use parity checking.\n"
	     << "                                                     valid values:\n"
	     << "                                                       0 (\"none\"), 1 (\"odd\"), 2 (\"even\").\n"
	     << "                                                     default: 0\n"
	     << "  -s, --stop-bits         <stop bits>             how many stop bits to send.\n"
	     << "                                                     valid values: 1-2.\n"
	     << "                                                     default: 1\n"
	     << "  -v, --verbose                                   dump out all the parameters used.\n"
	     << "      --config-file       <config-file>           the configuration file to use.\n"
	     << "                                                     default: /etc/LIBoxIO.conf\n"
	     << endl;
	     
	return;

}

void dumpValues(Minerva::LIBoxIO & liBox)
{
	std::cout << "\nI used the following parameters: \n"
	         << "   device: " << liBox.getSerialPortDev() << "\n"
	         << "   baud: " << liBox.getBaud() << "\n"
	         << "   parity: " << liBox.getParity() << "\n"
	         << "   flow control: " << liBox.getFlowcontrol() << "\n"
	         << "   data bits: " << liBox.getDatabits() << "\n"
	         << "   stop bits: " << liBox.getStopbits()
	         << std::endl;
	         
	return;
}

