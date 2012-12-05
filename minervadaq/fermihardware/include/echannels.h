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
		unsigned int channelNumber;             /*!<the channel identifying index, used for retrieval, currently indexed 0-3 */  
		unsigned int channelBaseAddress;        /*!<channelBaseAddress is the CROC address */
		unsigned int channelDirectAddress;		
		CVAddressModifier bltAddressModifier;   /*!<block transfers require a special modifier */
		std::vector<feb*> febsVector;           /*!<need to be able to direct access an FEB by index (address/number) */
		int FIFOMaxSize; 	                /*!< bytes */
		int MemoryMaxSize;                      /*!< bytes */

		unsigned int receiveMemoryAddress;
		unsigned int crocSendMemoryAddress;
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
		bool has_febs;                          /*!< a flag for sorting available echannels with or without FEB's */

		unsigned char *buffer; 			/*!< a buffer to hold unsorted DPM Memory */

	public:
		echannels(unsigned int, int);
		~echannels();

		unsigned int GetChannelNumber();

		unsigned int GetReceiveMemoryAddress();
		unsigned int GetCrocSendMemoryAddress();
		unsigned int GetFramePointersMemoryAddress();
		unsigned int GetConfigurationAddress();
		unsigned int GetCommandAddress();
		unsigned int GetEventCounterAddress();
		unsigned int GetFramesCounterAndLoopDelayAddress();
		unsigned int GetFrameStatusAddress();
		unsigned int GetTxRxStatusAddress();
		unsigned int GetReceiveMemoryPointerAddress();

		unsigned short inline GetChannelStatus() {return channelStatus;};
		unsigned int inline GetDPMPointer() {return dpmPointer;};
		bool inline GetHasFebs() {return has_febs;};
		unsigned char inline *GetBuffer() {return buffer;};
		CVAddressModifier inline GetBLTModifier() {return bltAddressModifier;};

		/*! set functions for various data members*/
		void SetFEBs(int a, int nHits, log4cpp::Appender* appender=0); //feb address, maxHits, log appender
		void inline SetHasFebs(bool a) {has_febs = a;};
		void inline SetChannelStatus(unsigned short a) {channelStatus=a;};
		void inline SetDPMPointer(unsigned short a) {dpmPointer = a;};
		void SetBuffer(unsigned char *b); 
		void inline DeleteBuffer() {delete [] buffer;};

		/*! misc. channel setup and data handling functions */
		feb *MakeTrialFEB(int a, int nHits, log4cpp::Appender* appender=0); //feb address, maxHits, log appender
		int DecodeStatusMessage();
		void inline ClearBuffer() {delete [] buffer;};
		int CheckHeaderErrors(int dataLength);

		std::vector<feb*> inline *GetFebVector() {return &febsVector;};
		feb inline *GetFebVector(int i) {return febsVector[i];};

		
};
#endif
