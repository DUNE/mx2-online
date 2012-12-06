#ifndef ecroc_h
#define ecroc_h

#include <list>
#include <fstream>
#include "CAENVMEtypes.h"
#include "echannels.h"
#include "MinervaDAQtypes.h"

/*********************************************************************************
* Class for creating CROC-E objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Gabriel Perdue, The University of Rochester
**********************************************************************************/

/*! \class ecroc
 *
 * \brief The class which controls data for CROC-Es. 
 *
 */

class ecroc {
	private:
		unsigned int vmeAddress; 		// the bit-shifted VME address
		int id; 				// the id is an "index" used by the controller
		std::list<echannels*> ecrocChannels; 
		CVAddressModifier addressModifier; 
		CVDataWidth dataWidth;
		CVDataWidth dataWidthSwapped;

		unsigned int timingSetupAddress;
		unsigned int resetAndTestPulseMaskAddress;
		unsigned int channelResetAddress;
		unsigned int fastCommandAddress;
		unsigned int testPulseAddress;
		unsigned int rdfePulseDelayAddress;
		unsigned int rdfePulseCommandAddress;

		unsigned short timingRegisterMessage;
		unsigned short resetAndTestPulseMaskRegisterMessage;
		unsigned short channelResetRegisterMessage;
		unsigned short fastCommandRegisterMessage;
		unsigned short testPulseRegisterMessage;

		// TODO: Figure out how the heck this works, I have totally forgotten!
		log4cpp::Appender* ecrocAppender;

	public:
		ecroc( unsigned int address, int ecrocid, log4cpp::Appender* appender=0 ); 
		~ecroc(); 

		unsigned int GetAddress(); 
		int GetCrocID(); 
		CVAddressModifier GetAddressModifier(); 
		CVDataWidth GetDataWidth();
		CVDataWidth GetDataWidthSwapped(); 

		void SetupChannels(); 
		echannels *GetChannel( unsigned int i ); 
		std::list<echannels*>* GetChannelsList(); 

		unsigned int GetTimingSetupAddress();
		void SetTimingRegisterMessage(crocClockModes clockMode, unsigned short testPulseDelayEnabled, unsigned short testPulseDelayValue); 
		unsigned short GetTimingRegisterMessage(); 

		void SetResetAndTestPulseRegisterMessage( unsigned short resetEnable, unsigned short testPulseEnable ); 

		void SetFastCommandRegisterMessage(unsigned short value);
		unsigned int GetFastCommandAddress();
		unsigned short GetFastCommandRegisterMessage();

		void InitializeRegisters( crocClockModes clockMode, 
				unsigned short testPulseDelayValue,
				unsigned short testPulseDelayEnabled ); 



};

#endif
