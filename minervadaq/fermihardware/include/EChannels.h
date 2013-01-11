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
#include "FEB.h"
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
    log4cpp::Appender* echanAppender;

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

		bool use_sequencer_mode;

		std::vector<FEB*> FEBsVector;           /*!< need to be able to direct access an FEB by index (address/number) */

    bool isAvailable( FEB* feb );
    void WriteMessageToMemory( unsigned char* message, int messageLength );

	public:
		EChannels( unsigned int baseVMEAddress, unsigned int channelNumber, log4cpp::Appender* appender, Controller* controller );
		~EChannels();

    void ClearAndResetStatusRegister();  
    unsigned short ReadFrameStatusRegister();
    unsigned short ReadTxRxStatusRegister();

    void SendMessage();
    void WaitForMessageReceived();
    unsigned short ReadDPMPointer();
    /* void ReadMemory( unsigned short dataLength, unsigned char* dataBuffer ); */ 
    unsigned char* ReadMemory( unsigned short dataLength ); 

    // write the frames - load them to memory (don't send messages)
    // no WriteFrame is deliberate - too many configs - we just offer preconfigured reads
    void WriteFPGAProgrammingRegistersToMemory( FEB *feb );
    void WriteFPGAProgrammingRegistersReadFrameToMemory( FEB *feb ); 
    void WriteTRIPRegistersToMemory( FEB *feb, int tripNumber );
    void WriteTRIPRegistersReadFrameToMemory( FEB *feb, int tripNumber ); 
    // read the frames - load messages to memory, send them, and then check the dpm pointer
    unsigned short ReadFPGAProgrammingRegistersToMemory( FEB *feb );

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

    int DecodeStatusMessage();
    int CheckHeaderErrors(int dataLength);

    void SetupNFEBs( int nFEBs );
    std::vector<FEB*>* GetFEBVector();
    FEB* GetFEBVector( int index /* should always equal FEB address */ );


};
#endif
