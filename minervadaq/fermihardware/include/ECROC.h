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

		unsigned short channelResetRegisterMessage;
		unsigned short testPulseRegisterMessage;

		log4cpp::Appender* ECROCAppender;

		void MakeChannels(); 

	public:
		ECROC( unsigned int address, log4cpp::Appender* appender, Controller* controller); 
		~ECROC(); 

    void Initialize();
		unsigned int GetAddress(); 

		EChannels *GetChannel( unsigned int i ); 
		std::vector<EChannels*>* GetChannelsVector(); 

		void SetupTimingRegister(crocClockModes clockMode, 
        unsigned short testPulseDelayEnabled, 
        unsigned short testPulseDelayValue); 
		void SetupResetAndTestPulseRegister( unsigned short resetEnable, 
        unsigned short testPulseEnable ); 
		void InitializeRegisters( crocClockModes clockMode, 
				unsigned short testPulseDelayValue,
				unsigned short testPulseDelayEnabled ); 

    void FastCommandOpenGate();
    void ClearAndResetStatusRegisters();
    void EnableSequencerReadout();
    void DisableSequencerReadout();
    void SendSoftwareRDFE(); // manually start sequencer readout
    void WaitForSequencerReadoutCompletion();
};

#endif
