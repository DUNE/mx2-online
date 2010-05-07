#ifndef croc_h
#define croc_h

/* system headers go here */
#include <list>
#include <fstream>

/* CAEN VME headers go here */
#include "CAENVMEtypes.h"

/* custom headers go here */
#include "channels.h"
#include "MinervaDAQtypes.h"

/*********************************************************************************
* Class for creating Chain Read-Out Controller objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
**********************************************************************************/

/*! \class croc
 *
 * \brief the class which controls data for CROC's 
 *
 */

class croc {
	private:
		unsigned int crocAddress; /*!<The croc's VME address */
		std::list<channels*> crocChannel; /*!<each croc card has 4 channels */
		CVAddressModifier addressModifier; /*!<remember, these can be different from the controller's */
		CVDataWidth dataWidth, dataWidthSwapped; /*!<remember, these can be different from the controller's */
		int id; /*!<an id number for a croc */

		/*! card level registers */
		unsigned int timingAddress, resetNtestAddress, channelResetAddress, 
			fastCommandAddress, testPulseAddress;

		unsigned short timingRegister, resetNtestRegister, channelResetRegister, 
			fastCommandRegister, testPulseRegister;

		bool registersInitialized; /*!< a flag for the initialization state of the croc */
		bool channel_available[4]; /*!< a flag for the channels which are available - really indexing chains here! */
		bool chain_available[4];   /*!< a flag for the chains which are available (chain==channel-1)*/

	public:
		/*! the default constructor */
		croc() { };
		/*! the specialized constructor */
		croc(unsigned int, int,CVAddressModifier, CVDataWidth, CVDataWidth);
		/*! the destructor */
		~croc() { 
			for (std::list<channels*>::iterator p=crocChannel.begin();
			p!=crocChannel.end();p++) delete (*p);
			crocChannel.clear();
		};

		/*! assigns channels to crocs */
		void SetupChannels(); //assignes channels to the croc
		/*! sets up the croc timing register */
		void InitializeRegisters(crocRegisters cm,  unsigned short tpdv,
			unsigned short tpde, bool &registersInitialized);

		/*! get and set functions */
		CVAddressModifier inline GetAddressModifier() {return addressModifier;};
		CVDataWidth inline GetDataWidth() {return dataWidth;};
		CVDataWidth inline GetDataWidthSwapped() {return dataWidthSwapped;};
		unsigned int inline GetAddress() {return crocAddress;};
		channels *GetChannel(int i); // returns the ith *chain* - should be updated to work like a channel
		channels *GetChain(int i); // returns the ith *chain*
		bool inline GetChainAvailable(int i) {return chain_available[i];}; // indexed by *chain*!
		bool inline GetChannelAvailable(int i) {return channel_available[i];}; // indexed by *chain*!
		int inline GetCrocID() {return id;};
		int inline GetCrocAddress() {return crocAddress;};


		/*! This sets up the full timing register.  We can decode the elements later */
		void SetTimingRegister(unsigned short cm, unsigned short tpde, unsigned short tpdval); 
		unsigned int GetTimingAddress(){return timingAddress;};
		unsigned short GetTimingRegister() {return timingRegister;};

		/*! this sets up the test & reset register */
		/*! the parameters are sent as shorts with appropriate bits set, bits are NOT shifted!! */
		void SetResetNTestRegister(unsigned short  re, unsigned short tpe);

		/*! set the fast command register, whatever this does... */
		void SetFastCommandRegister(unsigned short value);
		unsigned int GetFastCommandAddress(){return fastCommandAddress;};
		unsigned short GetFastCommandRegister(){return fastCommandRegister;};

		//we need to know which of the channels are instrumented
		void inline SetChannelAvailable(int i) {channel_available[i]=true;}; 
		void inline SetChainAvailable(int i) {chain_available[i]=true;}; 

};

#endif
