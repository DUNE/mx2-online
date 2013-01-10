#ifndef ECROC_h
#define ECROC_h

#include <list>
#include <fstream>
#include "CAENVMEtypes.h"
#include "EChannels.h"
#include "MinervaDAQtypes.h"

/*********************************************************************************
* Class for creating CROC-E objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Gabriel Perdue, The University of Rochester
**********************************************************************************/

/*! \class ECROC
 *
 * \brief The class which controls data for CROC-Es. 
 *
 */

class ECROC : public VMECommunicator {

	private:
		std::vector<EChannels*> ECROCChannels; 

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

		log4cpp::Appender* ECROCAppender;

		void SetupChannels(); 

	public:
		ECROC( unsigned int address, log4cpp::Appender* appender, Controller* controller); 
		~ECROC(); 

		unsigned int GetAddress(); 

		EChannels *GetChannel( unsigned int i ); 
		std::vector<EChannels*>* GetChannelsVector(); 

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

    void ClearAndResetStatusRegisters();
    void ClearAndResetStatusRegisters( unsigned int channelNumber );
    void ClearAndResetStatusRegisters( EChannels* channel );

};

#endif
