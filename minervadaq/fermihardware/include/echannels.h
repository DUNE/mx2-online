#ifndef echannels_h
#define echannels_h

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

/*********************************************************************************
* Class for creating Chain Read-Out Controller channel objects for use with the 
* MINERvA data acquisition system and associated software projects.
* 
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
***********************************************************************************/

/*! \class echannels
 *
 *  \brief This class holds data associated with a CROC-E channel.
 *
 * This class holds the data which belongs to a CROC-E channel, including the list
 * of FEB's which are on the channel.  
 *
 */

class echannels {
	private:
		unsigned int channelNumber;             /*!< the channel identifying index, used for retrieval, currently indexed 0-3 */  
		unsigned int channelBaseAddress;        /*!< channelBaseAddress is the CROC address */
		unsigned int channelDirectAddress;	/*!< base + offset */
		CVAddressModifier bltAddressModifier;   /*!< block transfers require a special modifier */

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

		unsigned short channelStatus;
		unsigned short dpmPointer; 
		bool use_sequencer_mode;

		std::vector<feb*> febsVector;           /*!< need to be able to direct access an FEB by index (address/number) */

		unsigned char *buffer; 			/*!< a buffer to hold unsorted DPM Memory */

	public:
		echannels( unsigned int baseVMEAddress, unsigned int channelNumber );
		~echannels();

		unsigned int GetChannelNumber();
		unsigned int GetParentECROCAddress();
		unsigned int GetDirectAddress();
		CVAddressModifier GetBLTModifier();

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

		unsigned short GetChannelStatus(); 
		void SetChannelStatus( unsigned short status );

		unsigned int GetDPMPointer();
		void SetDPMPointer( unsigned short pointer );

		unsigned char *GetBuffer();
		void SetBuffer( unsigned char *data ); 
		void DeleteBuffer(); 

		int DecodeStatusMessage();
		int CheckHeaderErrors(int dataLength);

		void AddFEB( feb* FEB ); 
		std::vector<feb*>* GetFebVector();
		feb* GetFebVector( int index /* should always equal FEB address */ );

		
};
#endif
