#ifndef LIBOXIO_H
#define LIBOXIO_H 1

#include <iostream>
#include <string>
#include <exception>

#include "libserial/src/SerialStream.h"


namespace Minerva
{
	struct IOPair
	{
		std::string command;
		std::string expectedResponse;
	};
	
	class LIBoxIO
	{
		public:
			// constructors and destructor
			LIBoxIO();
			LIBoxIO(std::string configfile);
			~LIBoxIO();
			
			// the real end-user functionality
			bool Arm();
			bool Disarm();
			bool RunScript(const std::string & scriptName);
			bool IssueSingleCommand(const IOPair & commandPair);
			
			// getters and setters
			inline std::string	getSerialPortDev()		{ return serialPortDev; };
			inline unsigned int	getBaud()				{ return baud; };
			inline unsigned int	getParity()			{ return parity; };
			inline unsigned int	getFlowcontrol()		{ return flowcontrol; };
			inline unsigned int	getDatabits()			{ return databits; };
			inline unsigned int	getStopbits()			{ return stopbits; };
			inline std::string	getConfigFile()		{ return configFile; };
			inline std::string	getScriptFileLocation()	{ return scriptFileLocation; };
			inline std::string	getArmScriptName()		{ return armScriptName; };
			inline std::string	getDisarmScriptName()	{ return disarmScriptName; };
			
			void setBaud(unsigned int newbaud);
			void setParity(unsigned int newparity);
			void setFlowcontrol(unsigned int newflowcontrol);
			void setDatabits(unsigned int newdatabits);
			void setStopbits(unsigned int newstopbits);
			
			inline void setSerialPortDev(std::string & port)				{ serialPortDev = port; };
			inline void setConfigFile(std::string & newconfigfile)			{ configFile = newconfigfile; };
			inline void setScriptFileLocation(std::string & newlocation)	{ scriptFileLocation = newlocation; };
			inline void setArmScriptName(std::string & newarmscript)		{ armScriptName = newarmscript; };
			inline void setDisarmScriptName(std::string & newdisarmscript)	{ disarmScriptName = newdisarmscript; };

		protected:
			void ReadConfig();
			void InitializePort();
			bool ExecuteScript(const std::string & scriptName);

		private:
			
			std::string	serialPortDev;
			unsigned int	baud;
			unsigned int	parity;
			unsigned int	flowcontrol;
			unsigned int	databits;
			unsigned int	stopbits;
			std::string	configFile;
			
			std::string	scriptFileLocation;
			std::string	armScriptName;
			std::string	disarmScriptName;
			
			LibSerial::SerialStream * serialPort;

			
	};
};

#endif
