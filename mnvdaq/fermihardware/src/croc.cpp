#ifndef croc_cpp
#define croc_cpp

#include "croc.h"

/*********************************************************************************
* Class for creating Chain Read-Out Controller objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
**********************************************************************************/

croc::croc(unsigned int a, int crocid, CVAddressModifier b, CVDataWidth c, CVDataWidth cs) 
{
/*!\fn 
 * constructor takes the following arguments:
 * \param a:  The croc address 
 * \param crocid: An integer for use as reference to this croc
 * \param b: The VME address modifier
 * \param c:  The VME data width
 * \param cs:  The VME byte-swapped data width; used for FIFO and Block transfer reads & writes
 *      and associated functions
 */
	crocAddress = a; //store the croc address
	addressModifier = b; //store the address modifier
	dataWidth = c; //store the data width
	dataWidthSwapped = cs; //store the swapped data with
	id = crocid;

	// Set the addresses for various registers used on the croc.
	crocRegisters registerOffset;
	registerOffset = crocTimingSetup;
	timingAddress = crocAddress+registerOffset;  //timing register address
	registerOffset = crocResetAndTestMask;
	resetNtestAddress = crocAddress+registerOffset; //reset and test register address
	registerOffset = crocChannelReset;
	channelResetAddress = crocAddress+registerOffset; //channel reset register address
	registerOffset = crocFastCommand;
	fastCommandAddress = crocAddress+registerOffset; //fast command register address
	registerOffset = crocTestPulse;
	testPulseAddress = crocAddress+registerOffset; //test pulse register address

	// the channel reset register, this just is, so we don't have to reset it all the time.
	channelResetRegister = 0x020;  //value to send the channel reset register to reset the croc

	// same for the test pulse register 
	testPulseRegister = 0x040; //value to send the test pulse register

	SetupChannels(); //load the data/associate objects which belong to this croc

	// DPM transfers are byte-swapped.  Set this value for future reference.
	CVDataWidth dpmDataWidth = dataWidthSwapped; 
					
	// Initialize all channels on all crocs to false, i.e. it isn't connected
	for (int i=0;i<4;i++) {
		channel_available[i]=false;  
	}

	// initialize the CROC register data, for now, the test pulse is not set 
	bool timing_init;
	InitializeRegisters((crocRegisters) 0x1, 0x0, 0x0, timing_init);
}


void croc::SetTimingRegister(unsigned short cm, unsigned short tpde, unsigned short tpdv) 
{
/*! \fn 
 * This function sets up the timing register data for the croc object.  (It does not write 
 * to the registers.)  
 *
 * \param cm the clock mode - 1 for external, 0 for internal
 * \param tpde test pulse enable bit
 * \param tpdv test pulse delay value
 */
// TODO - Fix the SetTimingRegister function to behave for some interface choice...
#if (DEBUG_VERBOSE)&&(DEBUG_CROC)
	std::cout << "  Entering croc::SetTimingRegister..." << std::endl;
	std::cout << "    Clock Mode        = " << cm << std::endl;
	std::cout << "    Test Pulse Enable = " << tpde << std::endl;
	std::cout << "    Test Pulse Delay  = " << tpdv << std::endl;
#endif
	timingRegister = (cm & 0x1)<<15 ;   // the clock mode  (0x8000 is the bitmask for bit 15 high)
	timingRegister |= (tpde & 0x1)<<12; // test pulse delay enable bit (bit 12)
	timingRegister |= tpdv & 0x3FF;     // test pules delay values (in 18.9 ns units) bits 0-9
	timingRegister &= 0xFFFF;
#if (DEBUG_VERBOSE)&&(DEBUG_CROC)
	printf("    Timing Register = 0x%04X\n",timingRegister);
#endif
}


void croc::SetResetNTestRegister(unsigned short pe, unsigned short tpe) 
{
/*! \fn 
 * This function sets up the reset and test pulse register data for the croc object.  (It 
 * does not write to the registers.)  The parameter values must be sent as shorts with the 
 * appropriate bits set. 
 * \param pe reset enable
 * \param tpe test pulse enable
 */
	resetNtestRegister = pe & 0xF00; //the reset enable (bits 8-11)
	resetNtestRegister |= tpe & 0xF; //the test pules enable (bits 0-3)
}


void croc::SetFastCommandRegister(unsigned short value) 
{
/*! \fn
 * Set the value to be written to the fast command register, if needed.
 * \param value the command to be written to the fast command register
 */
	fastCommandRegister = value & 0xFF;
}


void croc::InitializeRegisters(crocRegisters cm,  unsigned short tpdv,
	unsigned short tpde, bool &registersInitialized) 
{
/*! \fn********************************************************************************
 * This function initializes register data to default values.  It does not write to the 
 * registers!
 * \param cm clock mode
 * \param tpdv test pulse delay value
 * \param tpde test pulse delay enable
 * \param registersInitialized a status flag
 *
 */
	SetTimingRegister(cm, tpde, tpdv);
	SetResetNTestRegister(0,0);
	registersInitialized = true;
}


void croc::SetupChannels() 
{
/*! \fn
 * This function instantiates the channel objects belonging to this croc 
 */
	for (int i=0;i<4;i++) { 
		channels *tmp = new channels(crocAddress, i);
		crocChannel.push_back(tmp); 
	}
}


channels *croc::GetChannel(int i) {
/*! \fn
 * This function retrieves a specified croc channel belonging to this croc object.
 * \param i the channel number (indexed from 0)
 */
	channels *tmp=0; //a channel temporary to be returned
	for (std::list<channels*>::iterator p=crocChannel.begin(); 
	p!=crocChannel.end(); p++) { //loop over the list of channels belonging to this croc
		if (((*p)->GetChannelNumber())==i) tmp = (*p); //check the channel identifier
	}
	return tmp; //return the channel object
}

#endif
