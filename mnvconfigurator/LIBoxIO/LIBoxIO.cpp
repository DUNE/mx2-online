#include <stdexcept>
#include <fstream>
#include <algorithm>
#include <string>
#include <cctype>
#include <stdlib.h>

#include "LIBoxIO.h"
#include "LIBoxExceptions.h"
#include "libserial/src/SerialStream.h"

namespace Minerva
{
	// ****************************************************************************
	// Constructors & destructor
	// ****************************************************************************
	
	// Default constructor.
	LIBoxIO::LIBoxIO()
	 : serialPortDev("/dev/ttyS0"), baud(9600), parity(0),
	   flowcontrol(1), databits(8), stopbits(1),
	   serialPort(NULL), scriptFileLocation("/usr/share/LIBoxScripts"),
	   armScriptName("arm.li"), disarmScriptName("disarm.li"), configFile("")
	{}

	// Constructor with specification of configuration file.
	LIBoxIO::LIBoxIO(std::string configfile)
	 : serialPortDev("/dev/ttyS0"), baud(9600), parity(0),
	   flowcontrol(1), databits(8), stopbits(1),
	   serialPort(NULL), scriptFileLocation("/usr/share/LIBoxScripts"),
	   armScriptName("arm.li"), disarmScriptName("disarm.li"), configFile(configfile)
	{
		// open up the configuration file, if possible
		try
		{
			ReadConfig();
		}
		catch (LIBoxFileException & e)
		{
			std::cerr << "Warning: configuration file " << e.getFile() << " cannot be opened.  Using default parameters..." << std::endl;
		}
	}

	// Default destructor
	LIBoxIO::~LIBoxIO()
	{
		if (serialPort != NULL)
		{
			if (serialPort->IsOpen())
				serialPort->Close();
			
			delete serialPort;
		}
	}
	

	// ****************************************************************************
	// Getters & setters (non-inline)
	// ****************************************************************************
	void LIBoxIO::setBaud(unsigned int newbaud)
	{
		switch (newbaud)
		{
			case 1200:	// fall through
			case 2400:	// fall through
			case 4800:	// fall through
			case 9600:	// fall through
			case 19200:	// fall through
			case 38400:	// fall through
			case 57600:	// fall through
			case 115200:	// fall through
				baud = newbaud;
				break;
				
			default:
				throw std::invalid_argument("Invalid baud rate specified.");
				break;
		}
		return;
	}
	
	void LIBoxIO::setParity(unsigned int newparity)
	{
		switch ( newparity )
		{
			case 0:
			case 1:
			case 2:
				parity = newparity;
				break;
				
			default:
				throw std::invalid_argument("Invalid parity specified.");
				break;
				
		}
		return;
	}
	
	void LIBoxIO::setFlowcontrol(unsigned int newflowcontrol)
	{
		switch ( newflowcontrol )
		{
			case 0:
			case 1:
			case 2:
				flowcontrol = newflowcontrol;
				break;
				
			default:
				throw std::invalid_argument("Invalid flow control specified.");
				break;
				
		}
		return;
	}
	
	void LIBoxIO::setDatabits(unsigned int newdatabits)
	{
		switch ( newdatabits )
		{
			case 5:
			case 6:
			case 7:
			case 8:
				databits = newdatabits;
				break;
				
			default:
				throw std::invalid_argument("Invalid number of data bits specified.");
				break;
				
		}
		return;
	}
	
	void LIBoxIO::setStopbits(unsigned int newstopbits)
	{
		switch ( newstopbits )
		{
			case 1:
			case 2:
				stopbits = newstopbits;
				break;
				
			default:
				throw std::invalid_argument("Invalid number of stop bits specified.");
				break;
				
		}
		return;
	}

	// ****************************************************************************
	// Other methods
	// ****************************************************************************
	
	// InitializePort() applies the user-specified settings to the serial port.
	void LIBoxIO::InitializePort()
	{
//		// if we don't have the serial port hooked up, this all is meaningless.
//		return;
	
		// if it's already been initialized, don't do it again.
		if (serialPort != NULL)
			return;
		
		// should never happen ...
		if ( serialPortDev == "" )
			throw std::invalid_argument("Serial port location must be specified before initialization.");
		
		// first, open up the serial port.
		using namespace LibSerial;    
		serialPort = new SerialStream();
		serialPort->Open( serialPortDev ) ;
		if ( ! serialPort->good() ) 
			throw LIBoxSerialConnectionException();
			
		// now, go through the parameters set by the user and apply them to the serial port.
		switch (baud)
		{
			case 1200:
				serialPort->SetBaudRate( SerialStreamBuf::BAUD_1200 ) ;
				break;

			case 2400:
				serialPort->SetBaudRate( SerialStreamBuf::BAUD_2400 ) ;
				break;

			case 4800:
				serialPort->SetBaudRate( SerialStreamBuf::BAUD_4800 ) ;
				break;

			case 9600:
				serialPort->SetBaudRate( SerialStreamBuf::BAUD_9600 ) ;
				break;

			case 19200:
				serialPort->SetBaudRate( SerialStreamBuf::BAUD_19200 ) ;
				break;

			case 38400:
				serialPort->SetBaudRate( SerialStreamBuf::BAUD_38400 ) ;
				break;

			case 57600:
				serialPort->SetBaudRate( SerialStreamBuf::BAUD_57600 ) ;
				break;

			case 115200:
				serialPort->SetBaudRate( SerialStreamBuf::BAUD_115200 ) ;
				break;
		}
		
		switch (databits)
		{
			case 5:
				serialPort->SetCharSize( SerialStreamBuf::CHAR_SIZE_5 ) ;
				break;

			case 6:
				serialPort->SetCharSize( SerialStreamBuf::CHAR_SIZE_6 ) ;
				break;

			case 7:
				serialPort->SetCharSize( SerialStreamBuf::CHAR_SIZE_7 ) ;
				break;

			case 8:
				serialPort->SetCharSize( SerialStreamBuf::CHAR_SIZE_8 ) ;
				break;
		}
		
		switch (parity)
		{
			case 0:
				serialPort->SetParity( SerialStreamBuf::PARITY_NONE ) ;
				break;

			case 1:
				serialPort->SetParity( SerialStreamBuf::PARITY_ODD ) ;
				break;

			case 2:
				serialPort->SetParity( SerialStreamBuf::PARITY_EVEN ) ;
				break;
		}
		
		serialPort->SetNumOfStopBits(stopbits);
		
		switch (flowcontrol)
		{
			case 0:
				serialPort->SetFlowControl( SerialStreamBuf::FLOW_CONTROL_NONE ) ;
				break;

			case 1:
				serialPort->SetFlowControl( SerialStreamBuf::FLOW_CONTROL_HARD ) ;
				break;

			case 2:
				serialPort->SetFlowControl( SerialStreamBuf::FLOW_CONTROL_SOFT ) ;
				break;
		}

		// if it failed, inform the user.
		if ( ! serialPort->good() ) 
			throw LIBoxSerialParameterException();

		return;
	}
	
	// ReadConfig() reads out the configuration settings stored in configFile.
	void LIBoxIO::ReadConfig()
	{
		// try to open file in read mode.  if it doesn't exist or can't be opened, throw an exception.
		std::ifstream configFileStream(configFile.c_str());
		if ( !configFileStream.is_open() )
			throw LIBoxFileException(configFile);
			
		// read the config file line by line, writing the settings to member variables as appropriate.
		std::string line;
		int lineNum = 0;
		while (getline(configFileStream, line))
		{
			lineNum++;
			
			// ignore commented and blank lines
			if (line[0] == '#' || line == "")
				continue;
			
			int loc = line.find('=');
			if (loc == std::string::npos)
			{
				std::cerr << "Warning: gobbledygook on line " << lineNum << " of configuration file is not of the expected form: setting=value.  Ignoring..." << std::endl; 
				continue;
			}
			
			std::string settingName;
			std::string settingValue;
			
			settingName.assign(line, 0, loc);
			settingValue.assign(line, loc+1, line.size() - (loc+1));
			
			// convert the setting name to lowercase for easier checking.
			std::transform(settingName.begin(), settingName.end(), settingName.begin(), tolower);
			
			// incorrect parameter settings trigger exceptions.  better be prepared to handle them!
			try
			{
				if (settingName == "scriptlocation")
					setScriptFileLocation(settingValue);
				else if (settingName == "armscript")
					setArmScriptName(settingValue);
				else if (settingName == "disarmscript")
					setDisarmScriptName(settingValue);
				else if (settingName == "serialdevice")
					setSerialPortDev(settingValue);
				else if (settingName == "baud")
					setBaud( (unsigned int) atoi(settingValue.c_str()) );			// this setter expects an UNSIGNED int, but atoi() always returns a SIGNED one.  gotta cast to avoid compiler complaints... sigh.
				else if (settingName == "parity")
					setParity( (unsigned int) atoi(settingValue.c_str()) );
				else if (settingName == "flowcontrol")
					setFlowcontrol( (unsigned int) atoi(settingValue.c_str()) );
				else if (settingName == "databits")
					setDatabits( (unsigned int) atoi(settingValue.c_str()) );
				else if (settingName == "stopbits")
					setStopbits( (unsigned int) atoi(settingValue.c_str()) );
				else
					std::cerr << "Warning: setting name '" << settingName << "' on line " << lineNum << " of configuration file is not recognized.  Skipping..." << std::endl;
			}
			catch (std::exception & e)
			{
				std::cerr << "Warning in configuration file processing: " << e.what() << ".  Skipping..." << std::endl;
			}
			
//			std::cout << "Picked up configuration setting: name '" << settingName << "', value '" << settingValue << "'." << std::endl;
		} // while (getline(... line))
		
		configFileStream.close();
	}
	
	// ExecuteScript() does the dirty work of opening and sending the contents of a script to the LI box.
	bool LIBoxIO::ExecuteScript(const std::string & scriptName)
	{
		// try to open file in read mode.  if it doesn't exist or can't be opened, throw an exception.
		std::ifstream scriptStream(scriptName.c_str());
		if ( !scriptStream.is_open() )
			throw LIBoxFileException(scriptName);
		
		bool success = true;
		
		// read the script file line by line, sending commands to the LI box via IssueSingleCommand().
		std::string line;
		int lineNum = 0;
		while (getline(scriptStream, line) && success)
		{
			lineNum++;
			
			// ignore commented and blank lines
			if (line[0] == '#' || line == "")
				continue;
			
			std::string command;
			std::string expectedResponse;
			
			// if there's no ':', we assume the whole thing is intended as a command and that the user doesn't care what the response is.
			int loc = line.find(':');
			if (loc == std::string::npos)
			{
				expectedResponse = "";
				command = line;
			}
			else
			{
				command.assign(line, 0, loc);
				expectedResponse.assign(line, loc+1, line.size() - (loc+1));
			}
			
			IOPair commandPair = { command, expectedResponse };
			success = success && IssueSingleCommand(commandPair);
			
		} // while (getline(... line))
		
		scriptStream.close();
		
		return success;
	}
	
	// Arm() prepares the LI box to receive instructions from the pulser.
	bool LIBoxIO::Arm()
	{
		InitializePort();

		std::cout << "Arming LI Box..." << std::endl;
		
		bool success = true;
		std::string fullArmScriptName = scriptFileLocation + "/" + armScriptName;
		try
		{
			success = ExecuteScript(fullArmScriptName);
		}
		catch (LIBoxFileException & e)
		{
			std::cerr << "Error: 'arm' script '" << e.getFile() << "' cannot be opened.  Arm failed." << std::endl;
			return false;
		}
		
		return success;
	}
	
	// Disarm() returns the LI box to its standby state.
	bool LIBoxIO::Disarm()
	{
		InitializePort();

		std::cout << "Disarming LI Box..." << std::endl;

		bool success = true;
		std::string fullDisarmScriptName = scriptFileLocation + "/" + disarmScriptName;
		try
		{
			success = ExecuteScript(fullDisarmScriptName);
		}
		catch (LIBoxFileException & e)
		{
			std::cerr << "Error: 'disarm' script '" << e.getFile() << "' cannot be opened.  Disarm failed." << std::endl;
			return false;
		}
		
		return success;
	}
	
	// RunScript() runs a user-specified script
	bool LIBoxIO::RunScript(const std::string & scriptName)
	{
		InitializePort();
		
		std::cout << "Running script '" << scriptName << "'..." << std::endl;

		bool success = true;

		try
		{
			success = ExecuteScript(scriptName);
		}
		catch (LIBoxFileException & e)
		{
			// check if the user wanted a script that's in the default script location.
			// use that if it exists.
			std::string fullfilename = scriptFileLocation + "/" + scriptName;
			std::ifstream testfile(fullfilename.c_str());
			if (testfile.is_open())
			{
				testfile.close();
				std::cerr << "Warning: found script '" << scriptName << "' in default script location (" << scriptFileLocation << ").  Using that...\n"
				          << "  (If the script you want is elsewhere, be sure to give the full path to it...)" << std::endl;
				return ExecuteScript(fullfilename);
			}
			else
			{
				std::cerr << "Error: script '" << e.getFile() << "' cannot be opened.  Run failed." << std::endl;
				return false;
			}
		}
		
		return success;
	}
	
	// IssueSingleCommand() is the actual mechanism for sending an individual command to the LI box.
	bool LIBoxIO::IssueSingleCommand(const IOPair & commandPair)
	{
		if (serialPort == NULL)
			InitializePort();
		
		bool success = true;
		
		std::string response;
		
		std::cout << "  Issuing command '" << commandPair.command << "'..." << std::flush;
		(*serialPort) << commandPair.command << std::endl;

		if (commandPair.expectedResponse != "")
		{
			std::cout << " (awaiting response) ... " << std::flush;
			(*serialPort) >> response;
			
			std::cout << "received response '" << response;
		
			if (response != commandPair.expectedResponse)
			{
				std::cout << "' ... NOT ok.";
				success = false;
			}
			else
				std::cout << "' ... OK.";
		}
		else
			std::cout << " OK.";
		std::cout << std::endl;
		
		return success;
	}
}
