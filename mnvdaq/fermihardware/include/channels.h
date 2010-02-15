#ifndef channels_h
#define channels_h

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

/*! \class channels
 *
 *  \brief This class holds data associated with a CROC channel.
 *
 * This class holds the data which belongs to a CROC channel, including the list
 * of FEB's which are on the channel.  Channel numbering uses C-style numbering so we don't have 
 * to try to keep track of an extra indexing value.  So the first channel is 0, despite
 * what the channel numbering on the front panel of the CROC has to say about it.
 *
 */

class channels {
	private:
		int channelNumber;/*!<the channel identifying index, used for retrieval */  
		//channel numbers on the card are labled starting at 1, btw (yeah, what about it...)
		unsigned int channelBaseAddress, channelDirectAddress;/*!<channelBaseAddress is the CROC address */
		CVAddressModifier bltAddressModifier; /*!<block transfers require a special modifier */
		std::list<feb*> febs; /*!<each channel can have up to 15 front end boards (feb's) */
		int FIFOMaxSize; /*!< bytes */
		int MemoryMaxSize; /*!< bytes */
		unsigned int fifoAddress, dpmAddress, dpmPointerAddress,
			sendMessageAddress, statusAddress, clearStatusAddress;  /*!< local addresses for each channel's registers */

		unsigned short channelStatus, dpmPointer; /*!< data members for holding status values */
		bool has_febs; /*!< a flag for sorting available channels with or without FEB's */

		unsigned char *buffer; /*!<we need a buffer to hold unsorted DPM Memory */
		// std::ofstream log_file; /*!< A debugging output file streamer */

	public:
		/*! the default constructor */
		channels() { };
		/*! the specific constructor */
		channels(unsigned int, int);
		/*! the destructor */
		~channels() {
			for (std::list<feb*>::iterator p=febs.begin(); p!=febs.end(); p++) delete (*p);
			febs.clear();
		};

		/*! get functions for various data members*/
		int inline GetChannelNumber() {return channelNumber;}; // TODO - properly distinguish between channels and chains!
		int inline GetChainNumber() {return channelNumber;}; // TODO - properly distinguish between channels and chains!
		unsigned int inline GetChannelAddress() {return channelDirectAddress;};
		unsigned int inline GetFIFOAddress() {return fifoAddress;};
		unsigned int inline GetDPMAddress() {return dpmAddress;};
		unsigned int inline GetDPMPointerAddress() {return dpmPointerAddress;};
		unsigned int inline GetSendMessageAddress() {return sendMessageAddress;};
		unsigned int inline GetStatusAddress() {return statusAddress;};
		unsigned int inline GetClearStatusAddress() {return clearStatusAddress;};
		unsigned short inline GetChannelStatus() {return channelStatus;};
		unsigned int inline GetDPMPointer() {return dpmPointer;};
		bool inline GetHasFebs() {return has_febs;};
		unsigned char inline *GetBuffer() {return buffer;};
		CVAddressModifier inline GetBLTModifier() {return bltAddressModifier;};
		std::list<feb*> inline *GetFebList() {return &febs;};

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

};
#endif
