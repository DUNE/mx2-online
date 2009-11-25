#ifndef croc_cpp
#define croc_cpp

#include "croc.h"

/*********************************************************************************
 * Class for creating Chain Read-Out Controller objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * April 22, 2009
 *
 **********************************************************************************/

croc::croc(unsigned int a, int crocid, CVAddressModifier b, CVDataWidth c, CVDataWidth cs) {
  /*!\fn ********************************************************************************
 * constructor takes the following arguments:
 * \param a:  The croc address 
 * \param crocid: An integer for use as reference to this croc
 * \param b: The VME address modifier
 * \param c:  The VME data width
 * \param cs:  The VME byte-swapped data width; used for FIFO and Block transfer reads & writes
 *      and associated functions
 *********************************************************************************/
  crocAddress = a; //store the croc address
  addressModifier = b; //store the address modifier
  dataWidth = c; //store the data width
  dataWidthSwapped = cs; //store the swapped data with
  id = crocid;
  
  /*********************************************************************************
 * The following sets the addresses for various registers used on a croc 
 ***********************************************************************************/
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

  /* the channel reset register, this just is, so we don't have to reset it all the time */
  channelResetRegister = 0x020;  //value to send the channel reset register to reset the croc
  
  /* same for the test pulse register */
  testPulseRegister = 0x040; //value to send the test pulse register

  SetupChannels(); //load the data/associate objects which belong to this croc
  
  CVDataWidth dpmDataWidth = dataWidthSwapped; //dpm transfers are byte-swapped.  Set this
                     //value for future reference
  for (int i=0;i<4;i++) {
    channel_available[i]=false;  //initialize all channels on all crocs to fales, i.e. it isn't connected
  }


  /* initialize the CROC timing registers, for now, the test pulse is not set */
  bool timing_init;
  InitializeRegisters((crocRegisters) 0xF000, 0x0, 0x0, timing_init);
}

void croc::SetTimingRegister(unsigned short cm, unsigned short tpde, unsigned short tpdv) {
  /*! \fn ********************************************************************************
 * setup the timing register data on the croc  
 *
 * \param cm the clock mode
 * \param tpde test pulse enable bit
 * \param tpdv test pulse delay value
 **********************************************************************************/
  timingRegister = cm & 0x8000; //the clock mode  (0x8000 is the bitmask for bit 15 high)
  timingRegister |= tpde & 0x1000; //test pulse delay enable bit (bit 12)
  timingRegister |= tpdv & 0x3FF; //test pules delay values (in 18.9 ns units) bits 0-9
}

void croc::SetResetNTestRegister(unsigned short pe, unsigned short tpe) {

  /*! \fn 
 * the parameter values must be sent as shorts with the appropriate bits set 
 * \param pe reset enable
 * \param tpe test pulse enable
 */
  resetNtestRegister = pe & 0xF00; //the reset enable (bits 8-11)
  resetNtestRegister |= tpe & 0xF; //the test pules enable (bits 0-3)
}

void croc::SetFastCommandRegister(unsigned short value) {
  /*! \fn********************************************************************************
 * set the value to be written to the fast command register, if needed 
 * \param value the command to be written to the fast command register
 **********************************************************************************/
  fastCommandRegister = value & 0xFF;
}

void croc::InitializeRegisters(crocRegisters cm,  unsigned short tpdv,
      unsigned short tpde, bool &registersInitialized) 
{
  /*! \fn********************************************************************************
  * a function to initialize registers to default values 
  * \param cm clock mode
  * \param tpdv test pulse delay value
  * \param tpde test pulse delay enable
  * \param registersInitialized a status flag
  *
  *********************************************************************************/
  SetTimingRegister(cm, tpde, tpdv);
  SetResetNTestRegister(0,0);
  registersInitialized = true;
}

void croc::SetupChannels() {
  /*! \fn********************************************************************************
 * a function which sets the channels belonging to this croc 
 *********************************************************************************/
  for (int i=0;i<4;i++) { 
    channels *tmp = new channels(crocAddress, i); //make a temporary channel object
    crocChannel.push_back(tmp); //put that channel into a list of channels belonging
                     //to this croc object
  }
}

channels *croc::GetChannel(int i) {
  /*! \fn********************************************************************************
 * a function which retrieves a specified croc channel belonging to this croc object
 * \param i the channel number (indexed from 0)
 *********************************************************************************/
  channels *tmp=0; //a channel temporary to be returned
  for (std::list<channels*>::iterator p=crocChannel.begin(); 
    p!=crocChannel.end(); p++) { //loop over the list of channels belonging to this croc
    if (((*p)->GetChannelNumber())==i) tmp = (*p); //check the channel identifier
  }
  return tmp; //return the channel object
}

#endif
