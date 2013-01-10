#ifndef EChannels_h
#define EChannels_h

/* system header files here */
#include <list>
#include <fstream>
#include <string>
#include <sstream>

/* CAEN VME header files here */
#include "CAENVMEtypes.h"

/* custom header files here */
#include "feb.h"
#include "MinervaDAQtypes.h"
#include "FrameTypes.h"
#include "VMECommunicator.h"

/*********************************************************************************
* Class for creating CROC-E channel objects for use with the 
* MINERvA data acquisition system and associated software projects.
* 
* Gabriel Perdue, The University of Rochester
***********************************************************************************/

/*! \class EChannels
 *
 *  \brief This class holds data associated with a CROC-E channel.
 *
 * This class holds the data which belongs to a CROC-E channel, including the list
 * of FEB's which are on the channel.  
 *
 */

class EChannels : public VMECommunicator {
	private:
		unsigned int channelNumber;             /*!< the channel identifying index, used for retrieval, currently indexed 0-3 */  
		unsigned int channelDirectAddress;	    /*!< base + offset */

		unsigned int receiveMemoryAddress;
		unsigned int sendMemoryAddress;
		unsigned int framePointersMemoryAddress;
		unsigned int configurationAddress;
		unsigned int commandAddress;
		unsigned int eventCounterAddress;
		unsigned int framesCounterAndLoopDelayAddress;
		unsigned int frameStatusAddress;
		unsigned int txRxStatusAddress;
		unsigned int receiveMemoryPointerAddress;

		unsigned short dpmPointer; 
		bool use_sequencer_mode;

		std::vector<feb*> febsVector;           /*!< need to be able to direct access an FEB by index (address/number) */

		unsigned char *buffer; 			/*!< a buffer to hold unsorted DPM Memory */

	public:
		EChannels( unsigned int baseVMEAddress, unsigned int channelNumber, log4cpp::Appender* appender, Controller* controller );
		~EChannels();

    void ClearAndResetStatusRegister();  
    unsigned short ReadFrameStatusRegister();
    unsigned short ReadTxRxStatusRegister();

		unsigned int GetChannelNumber();
		unsigned int GetParentECROCAddress();
		unsigned int GetDirectAddress();

		unsigned int GetReceiveMemoryAddress();
		unsigned int GetSendMemoryAddress();
		unsigned int GetFramePointersMemoryAddress();
		unsigned int GetConfigurationAddress();
		unsigned int GetCommandAddress();
		unsigned int GetEventCounterAddress();
		unsigned int GetFramesCounterAndLoopDelayAddress();
		unsigned int GetFrameStatusAddress();
		unsigned int GetTxRxStatusAddress();
		unsigned int GetReceiveMemoryPointerAddress();

		unsigned int GetDPMPointer();
		void SetDPMPointer( unsigned short pointer );

		unsigned char *GetBuffer();
		void SetBuffer( unsigned char *data ); 
		void DeleteBuffer(); 

		int DecodeStatusMessage();
		int CheckHeaderErrors(int dataLength);

		void AddFEB( feb* FEB );  // TODO add a function in here that checks we are always adding a good number (0, 1, 2 in seq)
		std::vector<feb*>* GetFebVector();
		feb* GetFebVector( int index /* should always equal FEB address */ );

		
};
#endif
