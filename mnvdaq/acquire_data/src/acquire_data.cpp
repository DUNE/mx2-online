/*! \file 
 *
 * acquire_data.cpp:  Contains all of the functions needed for the 
 * initialization of DAQ electronics and execute an FEB acquisition.
 *
 * Also contains the passing of data frames to the ET for further 
 * processing.
 *
 */

#ifndef acquire_data_cxx
#define acquire_data_cxx

#include "acquire_data.h"
#include <sys/time.h>

const int acquire_data::dpmMax = 1024*6; //we have only 6 Kb of space in the DPM Memory per channel

void acquire_data::InitializeDaq(int id) {

/*! \fn void acquire_data::InitializeDaq()
 *
 * Executes the functions needed to fill the vectors with the numbers of 
 * CRIM's, CROC's, and FEB's which will need to be serviced during the
 * acquisition cycle.
 *
 * No parameters
 *
 */

  #if TIME_ME
     struct timeval start_time, stop_time;
     gettimeofday(&start_time, NULL);
  #endif

/* a log for keeping track of controller messages */

  std::ofstream controller_log;
  controller_log.open("controller_log");

/* Grab the VME read/write access functions */
  daqAcquire = new acquire(); 

/* first off, we need a controller to control the VME bus */
  daqController = new controller(0x00,id,controller_log); 
         /*! \todo { at some point we'll have a second controller 
 *                   this will need to be taken into account.} */

  try {
    int error = daqController->ContactController();
    if (error) throw error;
  } catch (int e) {
    controller_log<<"Error contacting controller"<<std::endl;
    exit(-1);
  } 

/* then we need the cards which can read off the data  */

/*! \note {Please note: for right now, the addresses of the cards have been 
  hard coded in.  This should be changed at some point, but for 
  the next few weeks, 
  hard coding is the name of the game.} */


  //in real life, here we need to access some data base or setup file or map or something
  //that will allow us to loop over all crocs & crims & controllers.  
  //But I don't know what that is just yet...So we'll hard code it until we get to FNAL and
  //do this for real.

  #if RUT&&THREAD_ME
    #if CRIM
      boost::thread crim_thread(boost::bind(&acquire_data::InitializeCrim,
                                this,0xF00000));
    #endif
      boost::thread croc_thread(boost::bind(&acquire_data::InitializeCroc,
                                this, 0x070000,1));
  #endif

  #if FNAL&&THREAD_ME
    #if CRIM
      boost::thread crim_thread(boost::bind(&acquire_data::InitializeCrim, 
                                this,0xE00000)); //test FNAL CRIM
    #endif
      boost::thread croc_thread(boost::bind(&acquire_data::InitializeCroc,
                                this, 0x080000,1)); //test FNAL CROC
  #endif

  #if NO_THREAD
    #if CRIM&&FNAL
      InitializeCrim(0xE00000);
    #endif
    #if CRIM&RUT
      InitializeCrim(0xF00000);
    #endif
    #if FNAL
      InitializeCroc(0x010000,1);
    #else
      InitializeCroc(0x070000,1);
    #endif
  #endif
/* end of electronics iniialization */

  #if (RUT||FNAL)&&THREAD_ME
    #if CRIM
    crim_thread.join(); //wait for the crim thread to return
    #endif
    #if DEBUG_THREAD
      std::cout<<"Crim Thread Complete"<<std::endl;
    #endif
    croc_thread.join(); //wait for the croc thread to return
    #if DEBUG_THREAD
      std::cout<<"Croc Thread Complete"<<std::endl;
    #endif
  #endif

  /*set the flag that tells us how many crocs are on this controller */
  daqController->SetCrocVectorLength(); 

  /* enable the CAEN IRQ handler */
  #if CRIM
    try {
     unsigned short bitmask = daqController->GetCrim()->GetInterruptMask();
     int error = CAENVME_IRQEnable(daqController->handle,~bitmask );
     if (error) throw error;
    } catch (int e) {
      std::cout<<"Error enabling CAEN VME IRQ handler"<<std::endl;
      exit(-8);
    }    
  #endif

  /* done with initialization procedures */

  #if TIME_ME
    gettimeofday(&stop_time,NULL);
    double duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
    controller_log<<"********************************************************************************"
                  <<std::endl; 
    controller_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                  <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
    controller_log<<"********************************************************************************"
                  <<std::endl; 
  #endif
}

void acquire_data::InitializeCrim(int address) {

/*! \fn void acquire_data::InitializeCrim(int address)
 *
 * This function checks the CRIM addressed by "address"
 * is available by reading a register.  
 *
 * Then the interrupt handler is set up.
 *
 * \param address an integer VME addres for the CRIM
 *
 */

  #if DEBUG_THREAD
    std::ofstream crim_thread;
    std::stringstream thread_number;
    thread_number<<address;
    std::string filename;
    filename = "crim_thread_"+thread_number.str();
    crim_thread.open(filename.c_str());
    crim_thread<<"Initializing CRIM, Start"<<std::endl;
  #endif

  /* make a CRIM object on this controller */

  daqController->MakeCrim(address); //make the crim

  /* make sure that we can actually talk to the cards */
  try {
    int status = daqController->GetCardStatus(); //tell me if the crim is working 
             //actually using the timing register at the moment
    if (status) throw status;
  } catch (int e)  {
    exit(-3);
  } 

  /* now set up the IRQ handler, initializing the global enable bit for the 
 *   first go-around */
  SetupIRQ();

  #if DEBUG_THREAD
    crim_thread<<"In InitializeCrim, Done"<<std::endl;
    crim_thread.close();
  #endif

  #if DEBUG_ME
    std::cout<<"Finished Setting up CRIM"<<std::endl;
  #endif
}

void acquire_data::InitializeCroc(int address, int crocNo) {

/*! \fn void acquire_data::InitializeCroc(int address, int crocNo)
 *
 * This function checks the CROC addressed by "address"
 * is available by reading the status register.  
 *
 * The CROC is then assigned the id crocNo.
 *
 * Then the FEB list for each channel on this croc is built.
 *
 * \param address an integer VME addres for the CROC
 * \param crocNo an integer given this CROC for ID
 *
 */

  #if DEBUG_ME
    std::cout<<"Initializing CROC"<<std::endl;
  #endif

  #if DEBUG_THREAD
    std::ofstream croc_thread;
    std::stringstream thread_number;
    thread_number<<address;
    std::string filename;
    filename = "croc_thread_"+thread_number.str();
    croc_thread.open(filename.c_str());
    croc_thread<<"In InitializeCrroc, Starting"<<std::endl;
  #endif

  daqController->MakeCroc(address,crocNo); //make the croc

  /* make sure that we can actually talk to the cards */
  try {
    int status = daqController->GetCardStatus(crocNo); //tell me if the croc is working 
    if (status) throw status;
  } catch (int e)  {
    exit(-2);
  }

  /* now make threads which will search all channels on the croc to find out which
 *   ones have FEB's on them.  Then set up the FEB's */

  #if THREAD_ME
    boost::thread *chan_thread[4];
  #endif

  /*  Build the FEB list for each channel */
 
  #if DEBUG_ME
    std::cout<<"Building FEB List"<<std::endl;
  #endif
  for (int i=0;i<4;i++) {
    /* now set up the channels and FEB's */
    croc *tmpCroc = daqController->GetCroc(crocNo);
    bool avail = false;
    avail = tmpCroc->GetChannelAvailable(i);
    if (avail) {
      channels *tmpChan=tmpCroc->GetChannel(i);
      #if THREAD_ME
        #if DEBUG_THREAD
          croc_thread<<"Launching build FEB list thread "<<i<<std::endl;
        #endif
          chan_thread[i] = new boost::thread(boost::bind(&acquire_data::BuildFEBList,this,i,1));
      #else
          BuildFEBList(i, 1);
      #endif
    }
  }

  #if THREAD_ME
    /* if we are working in multi-threaded operation we need to wait for the each 
 *     thread we launched to complete. */
    for (int i=0;i<4;i++) {
      chan_thread[i]->join(); //wait for all the threads to finish up before moving on
      #if DEBUG_THREAD
        croc_thread<<"Build FEB List: channel "<<i<<" thread completed"<<std::endl;
        croc_thread.close();
      #endif
      delete chan_thread[i];
    }  
  #endif

  #if DEBUG
    std::cout<<"RETURNED FROM BUILD FEB LIST"<<std::endl;
  #endif
}

int acquire_data::SetHV(feb *febTrial, croc *tmpCroc, channels *tmpChan,
                                int newHV, int newPulse, int hvEnable) {
/*! \fn int acquire_data::SetHV(feb *febTrial, croc *tmpCroc, channels *tmpChan,
 *                                 int newHV, int newPulse, int hvEnable)
 *  Formulates the appropriate FPGA messages to set the high voltage on 
 *  an FEB.
 *
 *  \param *febTrial a pointer to the feb object being manipulated
 *  \param *tmpCroc a pointer to the croc object on which this FEB resides
 *  \param *tmpChan a pointer to the channels object to thich this FEB belongs
 *  \param newHV an integer value setpoint for the HV
 *  \param newPulse an integer value of the pulse-width setpoint
 *  \param hvEnable an integer, sets the HV enable bit on the FEB
 *
 *  Returns a status integer. 
 *
 */

  /* we're making a WRITE header to send the new message */
  Devices dev = FPGA;
  Broadcasts b = None;
  Directions d = MasterToSlave;
  FPGAFunctions f = Write;
  unsigned char val[1] = {5};
  febTrial->SetHVNumAve(val); //the default setting for this value is 5
  val[0]=0;
  febTrial->SetHVManual(val); //make sure HVManual is set to 0
  febTrial->SetHVTarget(newHV); //set the HV to 44000 units
  val[0]=newPulse&0xFF; //select the lowest 8 bits of this integer
  febTrial->SetHVPulseWidth(val);
  val[0]=hvEnable&0xFF; //select lowest 8 bits of integer
  char set_hv[2];
  febTrial->SetHVEnabled(val);

  /* for lack of a better place to put this for now, I will set the gate while we set the HV */
  febTrial->SetGateLength(1024);
  
  febTrial->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) febTrial->GetBoardNumber());
  febTrial->MakeMessage();

  try {
    /* send a message to the FEB */ 
    int success = SendMessage(febTrial,tmpCroc, tmpChan,true); 
    if (success) throw success;
  } catch (int e) {
    std::cout<<"Unable to set HV on FEB: "<<febTrial->GetBoardNumber()<<" on channel: "
             <<tmpChan->GetChannelNumber()<<std::endl;
    exit(-12);
  }

  return 0;
}

int acquire_data::MonitorHV(feb *febTrial, croc *tmpCroc, channels *tmpChan) {
/*! \fn int acquire_data::MonitorHV(feb *febTrial, croc *tmpCroc, channels *tmpChan)
 *  Formulates the appropriate FPGA messages to monitor the high voltage on 
 *  an FEB.
 *
 *  \param *febTrial a pointer to the feb object being manipulated
 *  \param *tmpCroc a pointer to the croc object on which this FEB resides
 *  \param *tmpChan a pointer to the channels object to thich this FEB belongs
 *
 *  Returns high voltage value from this reading.
 */

  /* we're making a write header to send the new message */
  Devices dev = FPGA;
  Broadcasts b = None;
  Directions d = MasterToSlave;
  FPGAFunctions f = Read;
  
  febTrial->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) febTrial->GetBoardNumber());
  febTrial->MakeMessage();
  try {
    /* send the message to the FEB */
    int success = SendMessage(febTrial,tmpCroc, tmpChan,true); 
    if (success) throw (success);
  } catch (int e) {
    std::cout<<"Unable to set HV on FEB: "<<febTrial->GetBoardNumber()<<" on channel: "
             <<tmpChan->GetChannelNumber()<<std::endl;
    exit(-12);
  }

  /* now read a message back from the FEB */
  try {
    int success = ReceiveMessage(febTrial,tmpCroc, tmpChan);
    if (success) throw success;
  } catch (int e) {
    std::cout<<"Unable to monitor HV on FEB: "<<febTrial->GetBoardNumber()<<" on channel: "
             <<tmpChan->GetChannelNumber()<<std::endl;
    exit(-13);
  }
 
  /* now extract the FEB's HV value */
  int hv_value = febTrial->GetHVActual(); 

  /* return the value read off from the FEB */
  return hv_value;
}

int acquire_data::SetupIRQ() {

  /*!\fn int acquire_data::SetupIRQ()
 *
 * These are the steps to setting the IRQ:
     1)  Select an IRQ LINE on which the system with wait for an assert.  We have set this
         when the CRIM is enabled to the CNRST pulse.

     2)  Set the Interrupt mask on the crim.

     3)  Check the interrupt status & clear any pending interrupts.  They are a vestage of other
         processed.

     4)  Set the IRQ LEVEl which is asserted on the LINE.  We have set this to IRQ5, or 5 in the register
         when the CRIM is created.

     5)  Set the Global IRQ Enable bit.

     6)  Send this bitmask to the CRIM.

     7)  Enable the IRQ LINE on the CAEN controller to be the NOT of the IRQ LINE sent to the CRIM.

    Returns a status value.
  */


  int error = 0; 

  /* set up the crim interrupt mask */
  daqController->GetCrim()->SetInterruptMask(); //set the mask
  unsigned char crim_send[2] = {0,0};
  crim_send[0]=(daqController->GetCrim()->GetInterruptMask()) & 0xff;
  crim_send[1]=((daqController->GetCrim()->GetInterruptMask())>>0x08) & 0xff;
  try {
    error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
         daqController->GetCrim()->GetInterruptMaskAddress(), daqController->GetAddressModifier(),
         daqController->GetDataWidth()); //send it
    if (error) throw error;
  } catch (int e) {
    std::cout<<"Error setting crim IRQ mask"<<std::endl;
    exit(-4);
  }

  /* check the interrupt status */
  try {
    crim_send[0]=0; crim_send[1]=0; //reinitialize 
    error=daqAcquire->ReadCycle(daqController->handle,crim_send,
        daqController->GetCrim()->GetInterruptStatusAddress(), daqController->GetAddressModifier(),
        daqController->GetDataWidth()); //send it
    if (error) throw error;

  /* clear any pending interrupts */
    unsigned short interrupt_status = 0;
    interrupt_status = (unsigned short) (crim_send[0]|(crim_send[1]<<0x08));
    if (interrupt_status!=0) { //clear the pending interrupts
      crim_send[0]=daqController->GetCrim()->GetClearInterrupts() & 0xff;
      crim_send[1]=(daqController->GetCrim()->GetClearInterrupts()>>0x08) & 0xff;
      try {
        error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
                daqController->GetCrim()->GetClearInterruptsAddress(), daqController->GetAddressModifier(),
                daqController->GetDataWidth()); //send it
        if (error) throw error;
      } catch (int e) {
        std::cout<<"Error clearing crim interrupts "<<e<<std::endl;
        exit(-6);
      }
    }
  } catch (int e) {
    std::cout<<"Error getting crim interrupt status"<<std::endl;
    exit(-5);
  }

  /* now set the IRQ LEVEL */
  ResetGlobalIRQEnable();
  crim_send[0]=(daqController->GetCrim()->GetInterruptConfig()) & 0xff;
  crim_send[1]=((daqController->GetCrim()->GetInterruptConfig())>>0x08) & 0xff;
  #if DEBUG_ME
    std::cout.setf(std::ios::hex,std::ios::basefield);
    std::cout<<"IRQ LEVEL: "<<daqController->GetCrim()->GetInterruptConfig()<<std::endl;
    std::cout<<"IRQ LEVEL: "<<daqController->GetCrim()->GetInterruptsConfigAddress()<<std::endl;
  #endif
  try {
    error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
         daqController->GetCrim()->GetInterruptsConfigAddress(), daqController->GetAddressModifier(),
         daqController->GetDataWidth()); //send it
    if (error) throw error;
  } catch (int e) {
    std::cout<<"Error setting crim IRQ mask"<<std::endl;
    exit(-4);
  }

  /* now enable the line on the CAEN controller */
  error = CAENVME_IRQEnable(daqController->handle,~daqController->GetCrim()->GetInterruptMask());
 
  return 0;
}

int acquire_data::ResetGlobalIRQEnable() {

/*!  \fn int acquire_data::ResetGlobalIRQEnable()
 *
 * Sets the global enable bit on the CRIM interrupt handler
 *
 * Returns a status value.
 *
 */

  /*set the global enable bit */
  unsigned char crim_send[2];
  daqController->GetCrim()->SetInterruptGlobalEnable(true);

  crim_send[0]=((daqController->GetCrim()->GetInterruptConfig()) & 0xff);
  crim_send[1]=(((daqController->GetCrim()->GetInterruptConfig())>>0x08) & 0xff);
  try { 
    int error = daqAcquire->WriteCycle(daqController->handle,2,crim_send,
               daqController->GetCrim()->GetInterruptsConfigAddress(), 
               daqController->GetAddressModifier(),
               daqController->GetDataWidth()); //send it
    if (error) throw error;
  } catch (int e) {
    std::cout<<"Error setting IRQ Global Enable Bit "<<e<<std::endl;
    exit(-7);
  }
  return 0;
}

int acquire_data::BuildFEBList(int i, int croc_id) {
/*! \fn
 * int acquire_data::BuildFEBList(int i, int croc_id)
 *
 *  Builds up the FEB list on each CROC channel.
 *
 *  Finds FEB's by sending a message to each 1 through 16 potential FEB's
 *  per channel.  Those channels which respond with "message received"
 *  for that FEB have and FEB of the corresponding number 
 *  loaded into an STL list containing objects of type feb.
 *
 *  \param i an integer for the channel number
 *  \param croc_id an integer the ID number for the CROC
 *
 *  Returns a status value.
 *
 */

  #if DEBUG_THREAD
    std::ofstream build_feb_thread;
    std::stringstream thread_number;
    thread_number<<i<<"_"<<croc_id;
    std::string filename;
    filename = "FEB_list_"+thread_number.str();
    build_feb_thread.open(filename.c_str());
    build_feb_thread<<"Called BuildFEBList"<<std::endl;
  #endif

/* exract the CROC object and Channel object from the controller 
 * and assign them to a tmp of each type for ease of use */

  croc *tmpCroc = daqController->GetCroc(croc_id);
  channels *tmpChan = daqController->GetCroc(croc_id)->GetChannel(i);

  #if DEBUG_ME
    std::cout<<"Called BuildFEBList"<<std::endl;
  #endif

  /* We are trying to find which feb's are on a channel.
 *   the address numbers run from 1 to 15 so we'll loop
 *   over all possible address numbers */
 
  for (int j=1;j<16;j++) { //loop over possible feb's
  //for (int j=1;j<2;j++) { //loop over possible feb's
    #if DEBUG_ME
      std::cout<<"Making FEB: "<<j<<std::endl;
    #endif

    #if DEBUG_THREAD
      build_feb_thread<<"Making FEB: "<<j<<std::endl;
    #endif
    
      /* make a "trial" FEB for the current address */
      feb *tmpFEB = tmpChan->MakeTrialFEB(j); 

    #if DEBUG_ME
      std::cout<<"Made FEB: "<<i<<std::endl;
      std::cout<<"Making Message: "<<i<<std::endl;
    #endif

    #if DEBUG_THREAD
      build_feb_thread<<"Made FEB: "<<i<<std::endl;
      build_feb_thread<<"Making Message: "<<i<<std::endl;
      build_feb_thread<<"New FEB Number: "<<tmpFEB->GetBoardNumber()<<std::endl;
    #endif

      /* make an outgoing message to test the whether or not an FEB of this address
 *       is available on this channel */
      tmpFEB->MakeMessage(); 

    #if DEBUG_ME
      std::cout<<"Made Message: "<<i<<std::endl;
      std::cout<<"Sending Message: "<<i<<std::endl;
    #endif

    #if DEBUG_THREAD
      build_feb_thread<<"Made Message: "<<i<<std::endl;
      build_feb_thread<<"Sending Message: "<<i<<std::endl;
    #endif
    
    /* send the message */
    int success = SendMessage(tmpFEB,tmpCroc, tmpChan,true); 
    tmpFEB->DeleteOutgoingMessage();
    
    /* receive a message */
    success = ReceiveMessage(tmpFEB,tmpCroc,tmpChan);
    delete [] tmpFEB->message;

    #if DEBUG_THREAD
      build_feb_thread<<"BoardNumber--Receive: "<<tmpFEB->GetBoardNumber()<<std::endl;
      build_feb_thread<<"FEBNumber--Receive: "<<(int)tmpFEB->GetFEBNumber()<<std::endl;
      build_feb_thread<<"HV? "<<tmpFEB->GetHVActual()<<std::endl;
    #endif

    /* if the FEB is available, then load it into the channel's FEB list and 
 *     initialize it's trips */
    if (!success) {
      #if DEBUG_ME
        std::cout<<"FEB: "<<tmpFEB->GetBoardNumber()<<" is available on this channel "
          <<tmpChan->GetChannelNumber()<<" "<<tmpFEB->GetInit()<<std::endl;;
      #endif

      #if DEBUG_THREAD
        build_feb_thread<<"FEB: "<<tmpFEB->GetBoardNumber()<<" is available on this channel "
          <<tmpChan->GetChannelNumber()<<" "<<tmpFEB->GetInit()<<std::endl;;
      #endif
      /* set the FEB in the list */
      tmpChan->SetFEBs(j); 

      /* set the FEB available flag */
      tmpChan->SetHasFebs(true);
     
      /* initialize the FEB's trips */
      //InitializeTrips(tmpFEB, tmpCroc, tmpChan);

      /* clean up the memory */
      delete tmpFEB;  
    } else {
      #if DEBUG_ME
        std::cout<<"FEB: "<<(int)tmpFEB->GetBoardNumber()<<" is not available on this channel "
                <<tmpChan->GetChannelNumber()<<std::endl;
      #endif

      #if DEBUG_THREAD
        build_feb_thread<<"FEB: "<<(int)tmpFEB->GetBoardNumber()<<" is not available on this channel "
                 <<tmpChan->GetChannelNumber()<<std::endl;
      #endif

      /* clean up the memory */
      delete tmpFEB; 
    }  
  }
  #if DEBUG_ME
    std::cout<<"RETURNING FROM BUILD FEB LIST"<<std::endl;
  #endif

  #if DEBUG_THREAD
    build_feb_thread<<"RETURNING FROM BUILD FEB LIST"<<std::endl;
    build_feb_thread.close();
  #endif
  return 0;
}

int acquire_data::InitializeTrips(feb *tmpFEB, croc *tmpCroc, channels *tmpChan) {
  /*! \fn 
 * int acquire_data::InitializeTrips(feb *tmpFEB, croc *tmpCroc, channels *tmpChan)
 *
 *   The function which executes a trip initialization.
 *
 *   \param *tmpFEB  a pointer to the FEB object being initialized 
 *   \param *tmpCroc a pointer to the CROC object on which the FEB/Channel resides
 *   \param *tmpChan a pointer to the Channel object which has this FEB on it's list
 *
 *   Returns a status value.
 *
 */
 

  /* set the FEB default values */
  tmpFEB->SetFEBDefaultValues();

  /* make the outgoing message to send these default values */
  tmpFEB->MakeMessage();
  for (int index=0;index<tmpFEB->GetOutgoingMessageLength();index++) {
    std::cout<<"Outgoing Message before send: "<<(int)tmpFEB->GetOutgoingMessage()[index]<<std::endl;
  }
  try {
    /* send the message */
    int success = SendMessage(tmpFEB,tmpCroc,tmpChan,true);
    if (success) throw success;
  } catch (int e) {
    std::cout<<"Unable to access already listed FEB: "<<tmpFEB->GetBoardNumber()
             <<" on channel: "<<tmpChan->GetChannelNumber()<<std::endl;
    exit(-9);
  }
  for (int index=0;index<tmpFEB->GetOutgoingMessageLength();index++) {
    std::cout<<"Outgoing Message after send: "<<(int)tmpFEB->GetOutgoingMessage()[index]<<std::endl;
  }
  tmpFEB->DeleteOutgoingMessage();

  try {
    /* receive a message from the FEB to make sure it's there */
    int success = ReceiveMessage(tmpFEB,tmpCroc, tmpChan);
    if (success) throw (success);
  } catch (int e) {
    std::cout<<"Unable to read message from FEB: "<<tmpFEB->GetBoardNumber()
             <<" on channel: "<<tmpChan->GetChannelNumber()<<std::endl;
    exit(-10);
  }
  delete [] tmpFEB->message;
 
  /* turn on the trip power */
  if (tmpFEB->GetTripPowerOff()) {
    unsigned char val[1]={0}; //zero is trip power on, go figure
    tmpFEB->SetTripPowerOff(val);

    /* now make up a new header */
    Devices dev = FPGA;
    Broadcasts b = None;
    Directions d = MasterToSlave;
    FPGAFunctions f = Write;

    tmpFEB->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) tmpFEB->GetBoardNumber());
    tmpFEB->MakeMessage(); //make the new message
    #if DEBUG_ME
       std::cout<<"Turning on the TRIPS"<<std::endl;
    #endif
    try {
      int success = SendMessage(tmpFEB,tmpCroc,tmpChan,true); //resend the message to turn the trips on
      if (success) throw success;
    } catch (int e) {
      std::cout<<"Unable to access already listed FEB: "<<tmpFEB->GetBoardNumber()
             <<" on channel: "<<tmpChan->GetChannelNumber()<<std::endl;
      exit(-9);
    }
    try {
      /* receive a message from the FEB to make sure it's there */
      int success = ReceiveMessage(tmpFEB,tmpCroc, tmpChan);
      if (success) throw (success);
    } catch (int e) {
      std::cout<<"Unable to read message from FEB: "<<tmpFEB->GetBoardNumber()
             <<" on channel: "<<tmpChan->GetChannelNumber()<<std::endl;
      exit(-10);
    }
    #if DEBUG_ME
       std::cout<<"Done turning on the trips"<<std::endl;
    #endif
  } 
  for (int qq=0;qq<6;qq++) {
    //make the message
    tmpFEB->GetTrip(qq)->MakeMessage();
    #if DEBUG_ME
      std::cout<<"Init Trip Message Length: "<<tmpFEB->GetTrip(qq)->GetOutgoingMessageLength()<<std::endl;
    #endif
    try {
      int success = SendMessage(tmpFEB->GetTrip(qq), tmpCroc, tmpChan,true);
      if (success) throw success;
    } catch (int e) {
      std::cout<<"Unable to set trip: "<<qq<<" on FEB: "<<tmpFEB->GetBoardNumber()
             <<" on channel: "<<tmpChan->GetChannelNumber()<<std::endl;
      exit(-11);
    }
    tmpFEB->GetTrip(qq)->DeleteOutgoingMessage();
  }
  tmpFEB->SetInitialized(true); //now the FEB is intitialzed and we're ready to go!
  
  //Done with the initialization procedures
  return 0;
}

int acquire_data::GetBlockRAM(croc *crocTrial, channels *channelTrial) {

/*! \fn int acquire_data::GetBlockRAM(croc *crocTrial, channels *channelTrial)
 * \param *crocTrial a pointer to a croc object
 * \param *channelTrial a pointer to a channel object
 *
 * This function retrieves any data in a CROC channel's DPM and puts it into the buffer
 * DPMBuffer. This buffer is then assinged to a channel buffer for later use.
 *
 * Returns a status value.
 *
 */
  #if DEBUG_ME
    std::cout<<"Getting block ram"<<std::endl;
  #endif
  /* read of DPM RAM to a general purpose buffer for further processing */
  CVAddressModifier AM = daqController->GetAddressModifier();
  CVAddressModifier AM_BLT = channelTrial->GetBLTModifier(); 
  //CVDataWidth DW = daqController->GetDataWidth();
  CVDataWidth DWS = crocTrial->GetDataWidthSwapped();
  
  unsigned short dpmPointer;
  unsigned char status[2];
  daqAcquire->ReadCycle(daqController->handle,status,channelTrial->GetDPMPointerAddress(), AM,DWS);
  dpmPointer = (int) (status[0] | status[1]<<0x08);
  #if DEBUG_ME
    std::cout<<"dpmPointer: "<<dpmPointer<<std::endl;
  #endif
  if (dpmPointer%2) {
    DPMData = new unsigned char [dpmPointer+1];
  } else {
    DPMData = new unsigned char [dpmPointer];
  }
  int success = daqAcquire->ReadBLT(daqController->handle, DPMData,dpmPointer,channelTrial->GetDPMAddress(),
                           AM_BLT, DWS);
  #if DEBUG_ME
  /*  for (int index=0;index<dpmPointer;index++) {
      std::cout<<(int)DPMData[index]<<std::endl;
    } */
    std::cout<<"moving to SetBuffer"<<std::endl;
  #endif

  channelTrial->SetDPMPointer(dpmPointer);
  channelTrial->SetBuffer(DPMData);


  #if DEBUG_ME
    std::cout<<"What gives?"<<std::endl;
  #endif

  #if DEBUG_ME
    std::cout<<"returned from SetBuffer"<<std::endl;
    for (int index=0;index<12;index++) {
      std::cout<<"data: "<<DPMData[index]<<std::endl;
    }
    std::cout<<"returning from acquiring dpm"<<std::endl;
  #endif

  delete [] DPMData;
 //return success;
 return 0;
}

template <class X> bool acquire_data::FillDPM(croc *crocTrial, channels *channelTrial, X *frame, 
                           int outgoing_length, int incoming_length) {

/*! \fn template <class X> bool acquire_data::FillDPM(croc *crocTrial, channels *channelTrial, X *frame,
 *                            int outgoing_length, int incoming_length)
 *
 *  A templated function for filling a CROC channel's DPM.  This function is always used, however, the DPM is not
 *  necessarily always filled before moving on to the next processing step.  This allows for a single
 *  block transfer of data from a channel's DPM to a buffer assigned to that channel for later processing.
 *
 *  Currently, only one device's data is written to the DPM and is then processed.
 *
 *  \param croc *crocTrial  a pointer to the CROC object being accessed
 *  \param channels *channelTrial a pointer to the CROC channel object being accessed
 *  \param  X *frame a pointer to the genaric "frame" or device being read
 *  \param int outgoing_length an integer value for the outoing message length
 *  \param int incoming_length an integer value for the incoming message length
 *
 *  Returns a status bit.
 *
 */
  CVAddressModifier AM = daqController->GetAddressModifier();
  CVDataWidth DWS = crocTrial->GetDataWidthSwapped();
  
  unsigned short dpmPointer;
  unsigned char status[2];

  daqAcquire->ReadCycle(daqController->handle,status,channelTrial->GetDPMAddress(), AM,DWS);
  dpmPointer = (unsigned short) (status[0] | (status[1]<<0x08));
  
  if ((dpmPointer<dpmMax) && ((dpmMax-incoming_length)>incoming_length)) {
    SendMessage(frame, crocTrial, channelTrial, true);
    return true; 
  }
  return false;
}

bool acquire_data::TakeAllData(feb *febTrial, channels *channelTrial, croc *crocTrial, 
                               event_handler *evt, int thread,   et_att_id  attach, 
                               et_sys_id  sys_id) {

/*! \fn bool acquire_data::TakeAllData(feb *febTrial, channels *channelTrial, croc *crocTrial,
 *                                event_handler *evt, int thread,   et_att_id  attach,
 *                                                               et_sys_id  sys_id)
 *
 *  The main acquisition sequence.  This function organizes all of the incoming and outgoing 
 *  messages to the data acquisition electronics, collects those messages, fills a structure
 *  for future data handling, and sends the data on to the event builder.
 *
 *  \param feb *febTrial  a pointer to the feb being accessed
 *  \param channels *channelTrial  a pointer to the CROC channel which olds the FEB
 *  \param croc *crocTrial  a pointer to the CROC that has the FEB/Channel being accessed
 *  \param event_handler *evt  a pointer to an event_handler structure for data processing
 *  \param int thread   an integer value for the thread executing
 *  \param et_att_id  attach the ET attachemnt to which the data will be sent
 *  \param et_sys_id  sys_id the system ID for ET which will handle the data
 *
 *  Returns a status bit.
 *
 */

/*********************************************************************************/
/*   Setup an output file if we're going to estimate execution timing            */
/*********************************************************************************/
  #if TIME_ME
    lock lock(data_lock);
    double duration = -1;
    std::ofstream take_data_log;
    std::stringstream threadno;
    threadno<<thread<<"_"<<febTrial->GetFEBNumber();
    std::string filename;
    filename = "take_data_time_log_"+threadno.str();
    take_data_log.open(filename.c_str());
    lock.unlock();
  #endif
  #if DEBUG_ME
     std::cout<<"--------------------------------------------------------------------------------"<<std::endl;
  #endif


/*********************************************************************************/
/*     Set up some threads for using the event builder                           */
/*********************************************************************************/

  #if THREAD_ME
    boost::thread *eb_threads[3];
  #endif

/*********************************************************************************/
/*   Set up some execution status variables                                      */
/*********************************************************************************/

  bool success = false;
  bool memory_reset = false;
  int hits=-1;

/*********************************************************************************/
/*   Fill entries in the event_handler structure for this event.                 */
/*********************************************************************************/

  evt->new_event = false; //we are always processing an already created event fromt this function!!!
  evt->feb_info[0]=0; //we need to sort this out later (link number)
  evt->feb_info[1]=0; //crate number (make later)
  evt->feb_info[2]=crocTrial->GetCrocID();
  evt->feb_info[3]=channelTrial->GetChannelNumber();
  evt->feb_info[6]=febTrial->GetFEBNumber();

/*********************************************************************************/
/*   Make sure the DPM is reset for taking the FEB INFO Frames                   */
/*********************************************************************************/

  memory_reset = ResetDPM(crocTrial, channelTrial);
  #if DEBUG_ME
    std::cout<<"Memory Reset  FEB INFO: "<<memory_reset<<std::endl;
  #endif

/*********************************************************************************/
/*   Begin taking FEB info frame information                                     */
/*********************************************************************************/
  try {
    if (!memory_reset) throw memory_reset;

      #if TIME_ME
         struct timeval start_time, stop_time;
         gettimeofday(&start_time, NULL);
      #endif

/*********************************************************************************/
/*   Make up the outgoing FEB Message                                            */
/*********************************************************************************/
      //first, the feb info stuff
      Devices dev = FPGA;
      Broadcasts b = None;
      Directions d = MasterToSlave;
      FPGAFunctions f = Read;
  
      febTrial->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) febTrial->GetBoardNumber());
      febTrial->MakeMessage();
      try {

/*********************************************************************************/
/*  Acquire the data from the electronics                                        */
/*********************************************************************************/

        success=AcquireDeviceData(febTrial, crocTrial, channelTrial, FEB_INFO_SIZE);

        #if SHOW_REGISTERS
          febTrial->message = new unsigned char [FEB_INFO_SIZE];
          for (int debug_index=0; debug_index<febTrial->GetIncomingMessageLength(); debug_index++) {
            febTrial->message[debug_index]=channelTrial->GetBuffer()[debug_index];
          }
          febTrial->DecodeRegisterValues(febTrial->GetIncomingMessageLength());
          febTrial->ShowValues();
          febTrial->DeleteOutgoingMessage();
          delete [] febTrial->message;
        #endif

/*********************************************************************************/
/*  Complete the time estimate                                                   */
/*********************************************************************************/

        #if TIME_ME
          lock.lock();
          gettimeofday(&stop_time,NULL);
          duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
          take_data_log<<"******************FEB FRAMES******************************************"<<std::endl; 
          take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                        <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
          take_data_log<<"********************************************************************************"<<std::endl; 
          frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"2"<<"\t"<<(start_time.tv_sec*1000000+start_time.tv_usec)
                     <<"\t"<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
          lock.unlock();
        #endif
        #if DEBUG_ME
          std::cout<<"Acquired FEB data for"<<std::endl;
          std::cout<<"CROC: "<<crocTrial->GetCrocID()<<std::endl;
          std::cout<<"Channel: "<<channelTrial->GetChannelNumber()<<std::endl;
          std::cout<<"FEB: "<<febTrial->GetBoardNumber()<<std::endl;
          std::cout<<"--------------------------------------------------------------------------------"<<std::endl;
        #endif

/*********************************************************************************/
/*    Prepare to fill the event_handler structure with the newly acquired data   */
/*********************************************************************************/

        #if TIME_ME
           gettimeofday(&start_time, NULL);
        #endif

/*********************************************************************************/
/*    Fill the structure                                                         */
/*********************************************************************************/
        FillEventStructure(evt, 2, febTrial, channelTrial);

/*********************************************************************************/
/*  Complete the time estimate                                                   */
/*********************************************************************************/

        #if TIME_ME
            lock.lock();
            gettimeofday(&stop_time,NULL);
            duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
            take_data_log<<"******************FEB FILL EVENT STRUCTURE******************************************"<<std::endl; 
            take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                        <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
            take_data_log<<"********************************************************************************"<<std::endl; 
            frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"10"<<"\t"
                             <<(start_time.tv_sec*1000000+start_time.tv_usec)<<"\t"
                             <<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
            lock.unlock();
        #endif
        evt->feb_info[7]=(int)febTrial->GetFirmwareVersion();
        #if DEBUG_ME
           std::cout<<"firmware version: "<<(int)evt->feb_info[7]<<std::endl;
           std::cout<<"length: "<<evt->feb_info[5]<<std::endl;
           std::cout<<"bank: "<<evt->feb_info[4]<<std::endl;
        #endif
        if (success) throw success;
      } catch (bool e) {
        std::cout<<"Error adding FEB Information to DPM"<<std::endl;
        exit(-1001);
      }

/*********************************************************************************/
/*      Preapre to send the data to EB via ET                                    */
/*********************************************************************************/
        #if DEBUG_ME
           std::cout<<"Contacting the Event Builder Service"<<std::endl;
           std::cout<<"bank: "<<evt->feb_info[4]<<std::endl;
        #endif

        #if TIME_ME
             gettimeofday(&start_time, NULL);
        #endif

/*********************************************************************************/
/*                 Send the data to EB via ET                                    */
/*********************************************************************************/

        #if KEEP_DATA
          #if NO_THREAD
              ContactEventBuilder(evt,thread,attach,sys_id); //load FEB information into the event
	      channelTrial->DeleteBuffer();
          #elif THREAD_ME
              eb_threads[0] = new boost::thread((boost::bind(&acquire_data::ContactEventBuilder,this,
                                         boost::ref(evt),thread,attach,sys_id)));
	      channelTrial->DeleteBuffer();
          #endif
        #endif

/*********************************************************************************/
/*  Complete the time estimate                                                   */
/*********************************************************************************/

        #if TIME_ME
            lock.lock();
            gettimeofday(&stop_time,NULL);
            duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
            take_data_log<<"******************FEB FRAMES:  CONTACT_EB******************************************"<<std::endl; 
            take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                        <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
            take_data_log<<"********************************************************************************"<<std::endl; 
            frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"20"<<"\t"
                             <<(start_time.tv_sec*1000000+start_time.tv_usec)<<"\t"
                             <<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
            lock.unlock();
        #endif 

        #if DEBUG_ME
           std::cout<<"Back from EB?"<<std::endl;
        #endif

        #if v81

/*********************************************************************************/
/*      Prepare to take DISC Frame Data                                          */
/*********************************************************************************/

          #if DEBUG_ME
               std::cout<<"--------------------------------------------------------------------------------"<<std::endl;
               std::cout<<"  DISC FRAMES"<<std::endl;
          #endif

          /* first, decide if the discriminators are on */
          bool disc_set = false;
          for (int trip_index=0;trip_index<6;trip_index++) {
            int vth = febTrial->GetTrip(trip_index)->GetTripValue(9); //get the SET threshold value
            if (vth) {
              disc_set=true;
              break;
            }
          }

/*********************************************************************************/
/*      Prepare to acquire DISC Frame data from electronics                      */
/*********************************************************************************/

          if (disc_set) { 
            memory_reset = ResetDPM(crocTrial,channelTrial); //reset the DPM
          #if TIME_ME
                 gettimeofday(&start_time, NULL);
          #endif
          try {

/*********************************************************************************/
/*      Execute the acquire Routine                                               */
/*********************************************************************************/

            success=AcquireDeviceData(febTrial->GetDisc(), crocTrial, channelTrial,FEB_DISC_SIZE);

/*********************************************************************************/
/*      Complete the time estimate                                               */
/*********************************************************************************/

          #if TIME_ME
            lock.lock();
            gettimeofday(&stop_time,NULL);
            duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
            take_data_log<<"*************************DISC FRAMES***********************************"<<std::endl; 
            take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                        <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
            take_data_log<<"********************************************************************************"<<std::endl; 
            frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"1"<<"\t"<<(start_time.tv_sec*1000000+start_time.tv_usec)
                     <<"\t"<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
            lock.unlock();
          #endif

/*********************************************************************************/
/*    Fill the event_handler structure                                           */
/*********************************************************************************/
 
          #if TIME_ME
            gettimeofday(&start_time, NULL);
          #endif

          FillEventStructure(evt, 1, febTrial->GetDisc(), channelTrial);

/*********************************************************************************/
/*      Complete the time estimate                                               */
/*********************************************************************************/

          #if TIME_ME
            lock.lock();
            gettimeofday(&stop_time,NULL);
            duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
            take_data_log<<"*************************DISC FILL EVENT STRUCTURE***********************************"<<std::endl; 
            take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                        <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
            take_data_log<<"********************************************************************************"<<std::endl; 
            frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"11"<<"\t"
                             <<(start_time.tv_sec*1000000+start_time.tv_usec)<<"\t"
                             <<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
            lock.unlock();
          #endif
          if ((success)||(!memory_reset)) throw success;
          #if DEBUG_ME
            std::cout<<"Acquired DISC data for"<<std::endl;
            std::cout<<"CROC: "<<crocTrial->GetCrocID()<<std::endl;
            std::cout<<"Channel: "<<channelTrial->GetChannelNumber()<<std::endl;
            std::cout<<"FEB: "<<febTrial->GetBoardNumber()<<std::endl;
            std::cout<<"--------------------------------------------------------------------------------"<<std::endl;
          #endif
        } catch (bool e) {
          std::cout<<"Error adding DISC Information to DPM"<<std::endl;
          exit(-1002);
        }
        //Now figure out how many hits we have & get ready to read them off
        //Do stuff that processes data here.
        #if DEBUG_ME
          std::cout<<"Contacting the Event Builder Service"<<std::endl;
          std::cout<<"bank: "<<evt->feb_info[4]<<std::endl;
        #endif

/*********************************************************************************/
/*      Contact the EB via ET                                                    */
/*********************************************************************************/
 
        #if KEEP_DATA
          #if NO_THREAD
            ContactEventBuilder(evt,thread,attach,sys_id); //load FEB information into the event
	    channelTrial->DeleteBuffer();
          #elif THREAD_ME
            eb_threads[0] = new boost::thread((boost::bind(&acquire_data::ContactEventBuilder,this,
                                           boost::ref(evt),thread,attach,sys_id)));
	    channelTrial->DeleteBuffer();
          #endif
        #endif

/*********************************************************************************/
/*     Fill the hits variable for so we can read off the correct number          */
/*     of ADC Frames.                                                            */
/*********************************************************************************/

        hits = evt->feb_info[8]; //how many hits do we read off? 
     } //Are the discriminators on?
      
     if (hits == -1) hits = 1; 
     for (int i=0;i<hits;i++) {
       if (!(memory_reset = ResetDPM(crocTrial, channelTrial))) {
         std::cout<<"Unable to reset DPM!"<<std::endl;
         exit(-1004);
       } //reset the DPM
       try {

/*********************************************************************************/
/*   Now take the ADC Frames                                                     */ 
/*********************************************************************************/

         #if TIME_ME
           gettimeofday(&start_time, NULL);
         #endif
         #if DEBUG_ME
           std::cout<<"--------------------------------------------------------------------------------"<<std::endl;
           std::cout<<"     v81 ADC FRAMES  "<<std::endl;
         #endif

/*********************************************************************************/
/*          Acquire ADC frames from electronics                                  */
/*********************************************************************************/

         success=AcquireDeviceData(febTrial->GetADC(i), crocTrial, channelTrial,FEB_HITS_SIZE);

/*********************************************************************************/
/*    Complete the time estimate                                                 */
/*********************************************************************************/

         #if TIME_ME
           lock.lock();
           gettimeofday(&stop_time,NULL);
           duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                     (start_time.tv_sec*1e6+start_time.tv_usec);
           take_data_log<<"********************ADC FRAMES*****************************************************"<<std::endl; 
           take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                       <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
           take_data_log<<"********************************************************************************"<<std::endl; 
           frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"0"<<"\t"<<(start_time.tv_sec*1000000+start_time.tv_usec)
                    <<"\t"<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
           lock.unlock();
         #endif

         #if DEBUG_ME
           std::cout<<"--------------------------------------------------------------------------------"<<std::endl;
         #endif

/*********************************************************************************/
/*          Fill the event_handler structure with data                           */
/*********************************************************************************/

         #if TIME_ME
           gettimeofday(&start_time, NULL);
         #endif

/*********************************************************************************/
/*        Execute the Fill Structure function                                    */
/*********************************************************************************/

         FillEventStructure(evt, 0, febTrial->GetADC(i), channelTrial);

/*********************************************************************************/
/*    Complete the Time estimate                                                 */
/*********************************************************************************/

         #if TIME_ME
           lock.lock();
           gettimeofday(&stop_time,NULL);
           duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                     (start_time.tv_sec*1e6+start_time.tv_usec);
           take_data_log<<"********************ADC FILL EVENT STRUCTURE*****************************************************"
                       <<std::endl; 
           take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                       <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
           take_data_log<<"********************************************************************************"<<std::endl; 
           frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"12"<<"\t"
                           <<(start_time.tv_sec*1000000+start_time.tv_usec)<<"\t"
                           <<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
           lock.unlock();
         #endif

         #if DEBUG_ME
           std::cout<<"Contacting the Event Builder Service"<<std::endl;
           std::cout<<"bank: "<<evt->feb_info[4]<<std::endl;
         #endif

/*********************************************************************************/
/*             Contact the EB via ET                                             */
/*********************************************************************************/

         #if KEEP_DATA
           #if NO_THREAD
             ContactEventBuilder(evt,thread,attach,sys_id); //load FEB information into the event
	     channelTrial->DeleteBuffer();
           #elif THREAD_ME
             eb_threads[2] = new boost::thread((boost::bind(&acquire_data::ContactEventBuilder,this,
                                              boost::ref(evt),thread,attach,sys_id)));
	     channelTrial->DeleteBuffer();
           #endif
         #endif
         if (success) throw success;
         #if DEBUG_ME
           std::cout<<"Acquired ADC data for"<<std::endl;
           std::cout<<"CROC: "<<crocTrial->GetCrocID()<<std::endl;
           std::cout<<"Channel: "<<channelTrial->GetChannelNumber()<<std::endl;
           std::cout<<"FEB: "<<febTrial->GetBoardNumber()<<std::endl;
         #endif
       } catch (bool e) {
          std::cout<<"Error adding ADC Information to the DPM"<<std::endl;
          exit(-1003);
       }
     } //end of hits loop

   #endif

   #if v65

/*********************************************************************************/
/*        Prepare to read of the ADC Frames (v65)                                */ 
/*********************************************************************************/

     if (!(memory_reset = ResetDPM(crocTrial, channelTrial))) {
       std::cout<<"Unable to reset DPM!"<<std::endl;
       exit(-1004);
     } //reset the DPM
     try {
     #if TIME_ME
       struct timeval start_time, stop_time;
       gettimeofday(&start_time, NULL);
     #endif

     #if DEBUG_ME
        std::cout<<"--------------------------------------------------------------------------------"<<std::endl;
        std::cout<<"     v65 ADC FRAMES  "<<std::endl;
     #endif

/*********************************************************************************/
/*      Acquire ADC data from electronics                                        */
/*********************************************************************************/
 
     success=AcquireDeviceData(febTrial->GetADC(0), crocTrial, channelTrial,FEB_HITS_SIZE);

     #if SHOW_REGISTERS
       unsigned char *tmp_buffer = new unsigned char [FEB_HITS_SIZE];
       febTrial->GetADC(0)->message = new unsigned char [FEB_HITS_SIZE];
       tmp_buffer = channelTrial->GetBuffer();
       for (int debug_index=0; debug_index<febTrial->GetADC(0)->GetIncomingMessageLength(); debug_index++) {
         febTrial->GetADC(0)->message[debug_index]=tmp_buffer[debug_index];
       }
       febTrial->GetADC(0)->DecodeRegisterValues(0);
       Devices dev = FPGA;
       Broadcasts b = None;
       Directions d = MasterToSlave;
       FPGAFunctions f = Read;
  
       febTrial->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) febTrial->GetBoardNumber());
       febTrial->MakeMessage();
       delete [] tmp_buffer;
       success=AcquireDeviceData(febTrial, crocTrial, channelTrial, FEB_INFO_SIZE);
       tmp_buffer = new unsigned char [FEB_HITS_SIZE];
       febTrial->message = new unsigned char [FEB_INFO_SIZE];
       tmp_buffer = channelTrial->GetBuffer();
       for (int debug_index=0; debug_index<febTrial->GetIncomingMessageLength(); debug_index++) {
         febTrial->message[debug_index]=tmp_buffer[debug_index];
       }
       febTrial->DecodeRegisterValues(febTrial->GetIncomingMessageLength());
       febTrial->ShowValues();
       febTrial->DeleteOutgoingMessage();
     #endif

/*********************************************************************************/
/*     Complete the Timing Estimate                                              */ 
/*********************************************************************************/

     #if TIME_ME
       lock.lock();
       gettimeofday(&stop_time,NULL);
       double duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
       take_data_log<<"***********************ADC FRAMES**************************************"<<std::endl; 
       take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                        <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
       take_data_log<<"********************************************************************************"<<std::endl; 
       frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"0"<<"\t"<<(start_time.tv_sec*1000000+start_time.tv_usec)
                     <<"\t"<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
       lock.unlock();
     #endif

     #if DEBUG_ME
       std::cout<<"--------------------------------------------------------------------------------"<<std::endl;
     #endif

/*********************************************************************************/
/*      Prepare to Fill the event_handler structure                              */
/*********************************************************************************/
 
     #if TIME_ME
       gettimeofday(&start_time, NULL);
     #endif

/*********************************************************************************/
/*      Execute FillEventStructre                                                */
/*********************************************************************************/
 
     FillEventStructure(evt, 0, febTrial->GetADC(0), channelTrial);

/*********************************************************************************/
/*     Complete the Timing Estimate                                              */ 
/*********************************************************************************/

     #if TIME_ME
       lock.lock();
       gettimeofday(&stop_time,NULL);
       duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
       take_data_log<<"***********************ADC FILL EVENT STRUCTURE**************************************"<<std::endl; 
       take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                        <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
       take_data_log<<"********************************************************************************"<<std::endl; 
       frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"12"<<"\t"<<(start_time.tv_sec*1000000+start_time.tv_usec)
                     <<"\t"<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
       lock.unlock();
     #endif

/*********************************************************************************/
/*          Preapre to Contact EB via ET                                         */
/*********************************************************************************/

     #if DEBUG_ME
      std::cout<<"Contacting the Event Builder Service"<<std::endl;
      std::cout<<"bank: "<<evt->feb_info[4]<<std::endl;
     #endif

     #if TIME_ME
       gettimeofday(&start_time, NULL);
     #endif

/*********************************************************************************/
/*             ContactEventBuilder                                               */
/*********************************************************************************/
 
     #if KEEP_DATA
       #if NO_THREAD
         ContactEventBuilder(evt,thread,attach, sys_id);
	 channelTrial->DeleteBuffer();
       #elif THREAD_ME
          eb_threads[2] = new boost::thread((boost::bind(&acquire_data::ContactEventBuilder,this,
                                               boost::ref(evt),thread,attach,sys_id)));
	  channelTrial->DeleteBuffer();
       #endif
     #endif

/*********************************************************************************/
/*     Complete the Timing Estimate                                              */ 
/*********************************************************************************/

     #if TIME_ME
       lock.lock();
       gettimeofday(&stop_time,NULL);
       duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
                      (start_time.tv_sec*1e6+start_time.tv_usec);
       take_data_log<<"******************ADC FRAMES:  CONTACT_EB******************************************"<<std::endl; 
       take_data_log<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
                        <<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<std::endl;
       take_data_log<<"********************************************************************************"<<std::endl; 
       frame_acquire_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<"21"<<"\t"<<(start_time.tv_sec*1000000+start_time.tv_usec)
                     <<"\t"<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<std::endl;
       lock.unlock();
     #endif 

     if (success) throw success;
       #if DEBUG_ME
         std::cout<<"Acquired ADC data for"<<std::endl;
         std::cout<<"CROC: "<<crocTrial->GetCrocID()<<std::endl;
         std::cout<<"Channel: "<<channelTrial->GetChannelNumber()<<std::endl;
         std::cout<<"FEB: "<<febTrial->GetBoardNumber()<<std::endl;
       #endif
    } catch (bool e) {
       std::cout<<"Error adding ADC Information to the DPM"<<std::endl;
       exit(-1003);
    }
  #endif
  } catch (bool e)  {
    std::cout<<"The DPM wasn't reset! If you'd done this right, it wouldn't have happened!"<<std::endl;
    exit(-1000);
  }

/*********************************************************************************/
/*         Wait for threads to join if nedessary                                 */
/*********************************************************************************/

  #if THREAD_ME
    eb_threads[0]->join();
    eb_threads[2]->join();
  #endif 

  #if DEBUG_ME
    std::cout<<"--------Returning from TakeAllData--------"<<std::endl;
  #endif

/*********************************************************************************/
/*                        Done                                                   */
/*********************************************************************************/

  return success;
}

bool acquire_data::ResetDPM(croc *crocTrial, channels *channelTrial) {

/*! \fn bool acquire_data::ResetDPM(croc *crocTrial, channels *channelTrial)
 *
 * A function which clears the DPM pointer on a CROC channel.
 *
 * \param croc *crocTrial  a pointer to a croc object
 * \param channels *channelTrial a pointer to a channel object
 *
 * Returns a status bit.
 */
  #if DEBUG_ME
    std::cout<<"Resetting dpm"<<std::endl;
  #endif
  bool reset = false;
  CVAddressModifier AM = daqController->GetAddressModifier();
  CVDataWidth DW = daqController->GetDataWidth();
  CVDataWidth DWS = crocTrial->GetDataWidthSwapped();
  unsigned char message[2]={0x0A, 0x0A};
  daqAcquire->WriteCycle(daqController->handle,2,message, 
                         channelTrial->GetClearStatusAddress(), AM,DW); //clear the status register
  daqAcquire->ReadCycle(daqController->handle,message, 
                        channelTrial->GetDPMPointerAddress(), AM,DWS); //get the value of the dpm pointer
  unsigned short status = (unsigned short) (message[0] | (message[1]<<0x08));
  #if DEBUG_ME
    std::cout<<"reset dpm status: "<<status<<std::endl;
    std::cout<<"message[0]: "<<(int) message[0]<<std::endl;
    std::cout<<"message[1]: "<<(int) message[1]<<std::endl;
  #endif
  if (status==2) reset = true; //reset successful
  
  #if DEBUG_ME
    std::cout<<"getting ready to return form ResetDPM"<<std::endl;
  #endif
  return reset;
}

template <class X> int acquire_data::SendMessage(X *device, croc *crocTrial, channels *channelTrial, bool singleton) {

/*! \fn template <class X> int acquire_data::SendMessage(X *device, croc *crocTrial, channels *channelTrial, bool singleton)
 *
 * A templated function for sending messages to a generic device.  This function is used throughout the acquisition 
 * sequence.
 *
 * \param X *device the "frame" being processed
 * \param croc *crocTrial a pointer to the croc object 
 * \param channels *channelTrial a pointer to a croc channel object
 * \param bool singleton a flag telling us whether we are going to do one or more than one send (for fill DPM)
 *
 * Returns a status integer.
 *
 */
  int success = 1; //the success of finding an feb on the channel
  CVAddressModifier AM = daqController->GetAddressModifier();
  CVDataWidth DW = daqController->GetDataWidth();
  CVDataWidth DWS = crocTrial->GetDataWidthSwapped();

  unsigned char send_message[2] ={0x01, 0x01}; //send message
  unsigned short status;
  unsigned char reset_status[2];
  if (singleton) {
    unsigned char reset_message[2] ={0x0A, 0x0A}; //the reset bits
    int testme = daqAcquire->ReadCycle(daqController->handle,reset_status,channelTrial->GetStatusAddress(),AM,DW);
    #if DEBUG_ME
      status = (unsigned short) (reset_status[0] | reset_status[1]<<0x08);
      std::cout.setf(std::ios::hex,std::ios::basefield);
      std::cout<<"channel status: "<<status<<" "<<testme<<std::endl;
      std::cout.setf(std::ios::dec,std::ios::basefield);
    #endif
    daqAcquire->WriteCycle(daqController->handle,2,reset_message,channelTrial->GetClearStatusAddress(),
		AM,DW); //clear status bits
    daqAcquire->ReadCycle(daqController->handle,reset_status,channelTrial->GetStatusAddress(),AM,DW);
    status = (unsigned short) (reset_status[0] | reset_status[1]<<0x08);
    channelTrial->SetChannelStatus(status);
    try {
      if (status!=0x3700) throw (1);
    } catch (int e) {
        std::cout.setf(std::ios::hex,std::ios::basefield);
	std::cout<<"Unable to reset channel "<<status<<std::endl;
	std::cout<<"Channel Number: "<<channelTrial->GetChannelNumber()<<std::endl;
        #if DEBUG_ME
          std::cout<<"Checked the status from an error condition"<<std::endl;
        #endif
	channelTrial->DecodeStatusMessage();
	exit(-103);
    }
  }

  int synch, deserializer;
  deserializer = status & 0x0400;
  synch = status & 0x0200;
  if ((deserializer) && (synch)) {
    int count;
    daqAcquire->WriteCycle(daqController->handle, device->GetOutgoingMessageLength(), device->GetOutgoingMessage(),
			   channelTrial->GetFIFOAddress(), AM, DWS) ; //load up message  
    /*CAENVME_FIFOBLTWriteCycle(daqController->handle, channelTrial->GetFIFOAddress(), 
                              device->GetOutgoingMessage(), device->GetOutgoingMessageLength(), 
                              AM, DWS, &count);   */
    //system("sleep 0.001s");
    daqAcquire->WriteCycle(daqController->handle,2,send_message, 
                           channelTrial->GetSendMessageAddress(), AM,DW); //send it
    while (success) {
      daqAcquire->ReadCycle(daqController->handle,reset_status,channelTrial->GetStatusAddress(),AM,DW); //check the status
      status = (unsigned short) (reset_status[0] | reset_status[1]<<0x08);
      channelTrial->SetChannelStatus(status);
      success = channelTrial->DecodeStatusMessage();
    }
  }  
  return success;
}

template <class X> int acquire_data::ReceiveMessage(X *device, croc *crocTrial, channels *channelTrial) {
/*! \fn template <class X> int acquire_data::ReceiveMessage(X *device, croc *crocTrial, channels *channelTrial)
 *
 * A templated function for receiving messages to a generic device.  This function is used throughout the acquisition 
 * sequence.
 *
 * \param X *device the "frame" being processed
 * \param croc *crocTrial a pointer to the croc object 
 * \param channels *channelTrial a pointer to a croc channel object
 *
 * Returns a status integer.
 *
 */
  //int success = 1; //the success of finding an feb on the channel //compiler error if this line is kept
  CVAddressModifier AM = daqController->GetAddressModifier();
  CVAddressModifier AM_BLT = channelTrial->GetBLTModifier();
  CVDataWidth DWS = crocTrial->GetDataWidthSwapped();

  unsigned short dpmPointer;
  unsigned char status[2];
  daqAcquire->ReadCycle(daqController->handle,status,channelTrial->GetDPMPointerAddress(), AM,DWS);
  dpmPointer = (unsigned short) (status[0] | status[1]<<0x08);
  #if DEBUG_ME
    std::cout<<"DPM Pointer (ReceiveMessage): "<<dpmPointer<<std::endl;
  #endif
  device->SetIncomingMessageLength(dpmPointer-2);
  if (dpmPointer%2) {
    device->message = new unsigned char [dpmPointer+1];
  } else {
    device->message = new unsigned char [dpmPointer];
  }
  daqAcquire->ReadBLT(daqController->handle, device->message,dpmPointer,channelTrial->GetDPMAddress(),
                           AM_BLT, DWS);
  bool success = device->CheckForErrors();
  if (success) {
    return success;
  }
  device->DecodeRegisterValues(dpmPointer-2);
  return success;
}

template <class X> int acquire_data::AcquireDeviceData(X *frame, croc *crocTrial, 
                                                       channels *channelTrial, int length) {
  /*! \fn template <class X> int acquire_data::AcquireDeviceData(X *frame, croc *crocTrial,
 *                                                        channels *channelTrial, int length) 
 *
 *  A function used for executing the read/write sequences during data acquisition.
 *
 *  \param X *frame a pointer to the generic frame being processed
 *  \param croc *crocTrial a pointer to a croc object
 *  \param channels *channelTrial a pointer to the croc channel object
 *  \param int length an integer which tells the size of the data block in bytes
 *
 *  Returns a status integer.
 *
 */
  #if THREAD_ME
    lock lock_send(send_lock);
  #endif
  #if DEBUG_ME
    std::cout<<"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"<<std::endl;
    std::cout<<"Acquiring Device Data"<<std::endl;
    std::cout<<"CROC Number: "<<crocTrial->GetCrocID()<<std::endl;
    std::cout<<"Channel Number: "<<channelTrial->GetChannelNumber()<<std::endl;
    std::cout.setf(std::ios::hex,std::ios::basefield);
    std::cout<<"Device: "<<frame->GetDeviceType()<<std::endl;
    std::cout.setf(std::ios::dec,std::ios::basefield);
  #endif
  CVAddressModifier AM = daqController->GetAddressModifier();
  CVDataWidth DWS = crocTrial->GetDataWidthSwapped();
  int success = 0;
  try { //try to add this frame's data to the DPM
    success=FillDPM(crocTrial,channelTrial,frame,frame->GetIncomingMessageLength(),length);
    if (!success) throw success; 
    unsigned short dpmPointer;
    unsigned char status[2];
    daqAcquire->ReadCycle(daqController->handle,status,channelTrial->GetDPMPointerAddress(), AM,DWS);
    dpmPointer = (unsigned short)(status[0] | status[1]<<0x08);
    frame->SetIncomingMessageLength(dpmPointer-2);
    #if DEBUG_ME
       std::cout<<"AcquireDeviceData, dpmPointer: "<<dpmPointer<<std::endl;
       std::cout<<"Message Length: "<<frame->GetIncomingMessageLength()<<std::endl;
       std::cout<<"status[0]: "<<(int)status[0]<<" status[1]: "<<(int)status[1]<<std::endl;
    #endif 
    success = GetBlockRAM(crocTrial, channelTrial); //Now Go get it!
    frame->message = new unsigned char [frame->GetIncomingMessageLength()];
    for (int index=0;index<frame->GetIncomingMessageLength();index++) {
      frame->message[index] = channelTrial->GetBuffer()[index];
    }
    frame->DecodeRegisterValues(frame->GetIncomingMessageLength());
    delete [] frame->message;
    #if DEBUG_ME
      std::cout<<"Reurned from GetBlockRAM"<<std::endl;
      std::cout<<"AcquireAllData success: "<<success<<std::endl;
    #endif
    if (success) throw success; 
  } catch (bool e) { //if unsuccessful, the DPM doesn't have enough memory, and we need to process what is there
    std::cout<<"DPM Fill Failure!  DPM Should have been reset before tyring to use!"<<std::endl;
    exit(-4001);
/*    GetBlockRAM(crocTrial, channelTrial); //read off the DPM and assign it to the channel
    //Do stuff that processes data here.
    memory_reset = ResetDPM(crocTrial, channelTrial); //reset the memory
    success=FillDPM(crocTrial,channelTrial,frame->GetOutgoingMessage(),frame->GetOutgoingMessageLength(),
                         frame->GetIncomingMessageLength(),length); //now add this frame's data to the DPM
    unsigned short dpmPointer;
    unsigned char status[2];
    daqAcquire->ReadCycle(daqController->handle,status,channelTrial->GetDPMAddress(), AM,DWS);
    dpmPointer =(unsigned short) (status[0] | status[1]<<0x08);
    frame->SetIncomingMessageLength(dpmPointer-2); */
  }

  #if DEBUG_ME
    std::cout<<"AcquireAllData success: "<<success<<std::endl;
    std::cout<<"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"<<std::endl;
  #endif
  return success;
}

void acquire_data::TriggerDAQ(int a) {

/*! \fn void acquire_data::TriggerDAQ(int a)
 *
 * A function which sets up the acquisition trigger indexed by parameter a.
 *
 * Currently, there's the one-shot trigger (0)
 *
 * \param int a the index of the trigger to be set up 
 *
 */
  CVAddressModifier AM = daqController->GetAddressModifier();
  CVDataWidth DW = daqController->GetDataWidth();
  int error=-1;
  switch (a) { //which type of trigger are we using
    case 0: //the one-shot trigger
      daqController->GetCrim()->SetupOneShot(); //set all of the one shot register values
        unsigned char crim_send[2];
       //send the timing setup request
       crim_send[0]=daqController->GetCrim()->GetTimingSetup() & 0xff;
       crim_send[1]=(daqController->GetCrim()->GetTimingSetup()>>0x08) & 0xff;
       try {
         error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
             daqController->GetCrim()->GetTimingRegister(), AM,DW); //send it
         if (error) throw error;
       } catch (int e) {
           std::cout<<"Unable to set timing register"<<std::endl;
           exit(-2002);
       }

       #if DEBUG_ME
         std::cout<<"Sent Timing Request"<<std::endl;
       #endif
       //send the trigger width
       crim_send[0]=daqController->GetCrim()->GetGateWidth() & 0xff;
       crim_send[1]=(daqController->GetCrim()->GetGateWidth()>>0x08) & 0xff;
       try {
         error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
                          daqController->GetCrim()->GetGateRegister(), AM,DW); //send it
         if (error) throw error;
       } catch (int e) {
           std::cout<<"Unable to set trigger width register"<<std::endl;
           exit(-2003);
       }
       #if DEBUG_ME
         std::cout<<"Sent Trigger Width"<<std::endl;
       #endif
       //Pulse delay
       crim_send[0]=daqController->GetCrim()->GetTcalbPulse() & 0xff;
       crim_send[1]=(daqController->GetCrim()->GetTcalbPulse()<<0x08) & 0xff;
       try {
         error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
                daqController->GetCrim()->GetTCalbRegister(), AM,DW); //send it
         if (error) throw error;
       } catch (int e) {
           std::cout<<"Unable to set pulse delay register"<<std::endl;
           exit(-2004);
       }

       #if DEBUG_ME
         std::cout<<"Sent Pulse Delay"<<std::endl;
       #endif
       //send triggering CNRST software pulse
       try {
         unsigned char send_pulse[2];
         send_pulse[0]=daqController->GetCrim()->GetSoftCNRST() & 0xff;
         send_pulse[1]=(daqController->GetCrim()->GetSoftCNRST()>>0x08)&0xff;
         error =daqAcquire->WriteCycle(daqController->handle,2,send_pulse,
            daqController->GetCrim()->GetCNRSTRegister(), AM,DW); //send it
         if (error) throw error;
       } catch (int e) {
           std::cout<<"Unable to set pulse delay register"<<std::endl;
           exit(-2005);
       }
      break;

      #if DEBUG_ME
        std::cout<<"Sent CNRST"<<std::endl;
      #endif
    default:
      std::cout<<"We don't have that trigger yet!"<<std::endl;
      exit(-2001);
  }  
}

void acquire_data::WaitOnIRQ() {

/*! \fn void acquire_data::WaitOnIRQ() 
 *
 * A function which waits on the interrupt handler to set an interrupt.
 *
 * Two options exist, one can wait for the CAEN interrupt handler to Wait on IRQ, or 
 * the status register can be polled until the interrupt bits are driven high.
 *
 */
  int error;
  #if DEBUG_ME
    std::cout<<"level: "<<daqController->GetCrim()->GetIRQLevel()<<std::endl;
  #endif
  #if ASSERT_INTERRUPT
    try {
      error = CAENVME_IRQWait(daqController->handle, daqController->GetCrim()->GetIRQLevel(), 1); //a 1000 ms timeout
      if (error!=-5) {
        if (error) throw error;
      } else {
        error = CAENVME_IRQWait(daqController->handle, daqController->GetCrim()->GetIRQLevel(), 1); //a 1000 ms timeout
        if (error) throw error;
      }
    } catch (int e) {
      std::cout<<"The IRQ Wait probably timedout..."<<e<<std::endl;
      exit(-3000);  
    }
  #endif

  #if POLL_INTERRUPT
    unsigned short interrupt_status = 0;
    unsigned char crim_send[2];
    while (!(interrupt_status&0x04)) { //0x04 is the IRQ Line of interest
      try {
        crim_send[0]=0; crim_send[1]=0; //reinitialize 
        error=daqAcquire->ReadCycle(daqController->handle,crim_send,
            daqController->GetCrim()->GetInterruptStatusAddress(), daqController->GetAddressModifier(),
            daqController->GetDataWidth()); //send it 
        if (error) throw error;
        interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08));
      } catch (int e) {
        std::cout<<"Error getting crim interrupt status"<<std::endl;
        exit(-5);
      }
    }
    /* clear the interrupt after acknowledging it */
    crim_send[0]=daqController->GetCrim()->GetClearInterrupts() & 0xff;
    crim_send[1]=(daqController->GetCrim()->GetClearInterrupts()>>0x08) & 0xff;
    try {
      error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
              daqController->GetCrim()->GetClearInterruptsAddress(), daqController->GetAddressModifier(),
              daqController->GetDataWidth()); //send it  
      if (error) throw error;
    } catch (int e) {
       std::cout<<"Error clearing crim interrupts "<<e<<std::endl;
       exit(-6);
    }
  #endif

}

void acquire_data::AcknowledgeIRQ() {

/*! \fn void acquire_data::AcknowledgeIRQ() 
 *
 * A function which acknowledges and resets the interrupt handler.
 *
 */
  CVDataWidth DW = daqController->GetDataWidth();
  int error;
  try {
    unsigned short vec;
    error = CAENVME_IACKCycle(daqController->handle,daqController->GetCrim()->GetIRQLevel(),&vec,DW);
    #if DEBUG_ME
      std::cout<<"IRQ LEVEL: "<<daqController->GetCrim()->GetIRQLevel()<<" VEC: "<<vec<<std::endl;
    #endif
    unsigned short interrupt_status;
    unsigned char crim_send[2];
    crim_send[0]=0; crim_send[1]=0; //reinitialize 
    error=daqAcquire->ReadCycle(daqController->handle,crim_send,
    daqController->GetCrim()->GetInterruptStatusAddress(), daqController->GetAddressModifier(),
    daqController->GetDataWidth()); //send it 
    interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08)); 

    while (interrupt_status) {
      try {
        crim_send[0]=0; crim_send[1]=0; //reinitialize 
        error=daqAcquire->ReadCycle(daqController->handle,crim_send,
            daqController->GetCrim()->GetInterruptStatusAddress(), daqController->GetAddressModifier(),
            daqController->GetDataWidth()); //send it 
        if (error) throw error;
        interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08)); 

       /* clear the interrupt after acknowledging it */
        crim_send[0]=daqController->GetCrim()->GetClearInterrupts() & 0xff;
        crim_send[1]=(daqController->GetCrim()->GetClearInterrupts()>>0x08) & 0xff;
        try {
          error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
                  daqController->GetCrim()->GetClearInterruptsAddress(), daqController->GetAddressModifier(),
                  daqController->GetDataWidth()); //send it  
          /* re-read the status register */
          crim_send[0]=0; crim_send[1]=0; //reinitialize 
          error=daqAcquire->ReadCycle(daqController->handle,crim_send,
              daqController->GetCrim()->GetInterruptStatusAddress(), daqController->GetAddressModifier(),
              daqController->GetDataWidth()); //send it
          if (error) throw error;
          interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08)); 
        } catch (int e) {
          std::cout<<"Error clearing crim interrupts "<<e<<std::endl;
          exit(-6);
        } 
      } catch (int e) {
        std::cout<<"Error getting crim interrupt status"<<std::endl;
      exit(-5);
      }
    }
    if (error) throw error;
    try {
       CVIRQLevels irqLevel=daqController->GetCrim()->GetIRQLevel();
       #if DEBUG_ME
         std::cout<<"Set IRQ LEVEL: "<<irqLevel<<" Returned IRQ LEVEL: "<<vec<<std::endl;
       #endif
      if (vec!=0x0A) throw (int)vec; //for SGATEFall
    } catch (int e) {
      std::cout<<"IRQ LEVEL returned did not match IRQ LINE Vector" <<std::endl;
    }
  } catch (int e) {
      std::cout<<"The IRQ Wait probably timedout..."<<e<<std::endl;
      exit(-3000);  
  }
}

void acquire_data::ContactEventBuilder(event_handler *evt, int thread, et_att_id  attach, 
                                       et_sys_id  sys_id) {


/*! \fn void acquire_data::ContactEventBuilder(event_handler *evt, int thread, et_att_id  attach,
 *                                        et_sys_id  sys_id)
 *
 *  A function which sends raw data to the event builder via Event Transfer for processing into the 
 *  event model and final output file.  
 *
 *  \param event_handler *evt a pointer to the event structure holding raw data
 *  \param int thread an integer thread number
 *  \param et_att_id  attach the ET attachment to which this data will be sent
 *  \param et_sys_id  sys_id the ET system id for data handling
 *
 */

  std::ofstream contact_thread;
  std::string filename;
  std::stringstream thread_no;
  thread_no<<thread;
  filename = "contact_eb_"+thread_no.str();
  contact_thread.open(filename.c_str());
  #if DEBUG_ME
    contact_thread<<"Contacting the Event Builder"<<std::endl;
    contact_thread<<"In Event Builder the Bank Being Sent Is: "<<evt->feb_info[4]<<std::endl;
  #endif


    /* now for the data buffer */
  #if DEBUG_ME
     contact_thread<<"bank? "<<evt->feb_info[4]<<std::endl;
     contact_thread<<"Length: "<<evt->feb_info[5]<<std::endl;
  #endif
  int length = 0;
  switch (evt->feb_info[4]) {
    case 0:
      length = (int)(FEB_HITS_SIZE - 8);
      break;
    case 1:
      length = (int)(FEB_DISC_SIZE - 8);
      break;
    case 2:
      length = (int)(FEB_INFO_SIZE - 8);
      break;
    case 3:
      length = (int)(DAQ_HEADER);
  }
    

  #if REPORT_EVENT
     std::cout<<"********************************************************************************"<<std::endl;
     std::cout<<"Sending Data to ET System:"<<std::endl;
  #endif
  /*send event to ET for storage */
  while (et_alive(sys_id)) {
    #if DEBUG_ME
       std::cout<<"ET Alive?"<<std::endl;
    #endif
    et_event *pe; //the event
    //void *pdata; //the data for the event
    event_handler *pdata; //the data for the event
    #if THREAD_ME
      lock eb_lock(eb_mutex);
    #endif
    int status = et_event_new(sys_id, attach, &pe, ET_SLEEP, NULL, sizeof(struct event_handler)); //gimme an event
    #if THREAD_ME
      eb_lock.unlock();
    #endif
    if (status == ET_ERROR_DEAD) {
      printf("ET system is dead\n");
      break;
    } else if (status == ET_ERROR_TIMEOUT) {
      printf("got timeout\n");
      break;
    } else if (status == ET_ERROR_EMPTY) {
      printf("no events\n");
      break;
    } else if (status == ET_ERROR_BUSY) {
      printf("grandcentral is busy\n");
      break;
    } else if (status == ET_ERROR_WAKEUP) {
      printf("someone told me to wake up\n");
      break;
    } else if ((status == ET_ERROR_WRITE) || (status == ET_ERROR_READ)) {
      printf("socket communication error\n");
      break;
    } if (status != ET_OK) {
      printf("et_producer: error in et_event_new\n");
      exit(0);
    } 
    /* put data into the event here */
    if (status == ET_OK) {
      #if REPORT_EVENT
        std::cout<<"********************************************************************************"<<std::endl;
        std::cout<<"Putting Event on ET System:"<<std::endl;
      #endif
      switch (evt->feb_info[4]) {
        case 0:
          length = FEB_HITS_SIZE;
          break;
        case 1:
          length = FEB_DISC_SIZE;
          break;
        case 2:
          length = FEB_INFO_SIZE;
          break;
        case 3:
          length = DAQ_HEADER;
          break;
      }
      #if THREAD_ME
        eb_lock.lock();
      #endif
      et_event_getdata(pe, (void **)&pdata); //get the event ready 
      std::cout<<"event_handler_size: "<<sizeof(struct event_handler)<<std::endl;
      std::cout<<"evt_size: "<<sizeof(evt)<<std::endl;
      
      #if REPORT_EVENT
         std::cout<<"********************************************************************************"<<std::endl; 
         std::cout<<"Finished Processing Event Data:"<<std::endl;
         std::cout<<"GATE: "<<evt->gate_info[1]<<std::endl;
         std::cout<<"CROC: "<<evt->feb_info[2]<<std::endl;
         std::cout<<"CHAN: "<<evt->feb_info[3]<<std::endl;
         std::cout<<"BANK: "<<evt->feb_info[4]<<std::endl;
         std::cout<<"DETECT: "<<evt->run_info[0]<<std::endl; 
         std::cout<<"CONFIG: "<<evt->run_info[1]<<std::endl; 
         std::cout<<"RUN: "<<evt->run_info[2]<<std::endl;
         std::cout<<"SUB-RUN: "<<evt->run_info[3]<<std::endl;
         std::cout<<"TRIGGER: "<< evt->run_info[4]<<std::endl;
         std::cout<<"GLOBAL GATE: "<<evt->gate_info[0]<<std::endl;
         std::cout<<"TRIG TIME: "<<evt->gate_info[2]<<std::endl;
         std::cout<<"ERROR: "<<evt->gate_info[3]<<std::endl;
         std::cout<<"MINOS: "<<evt->gate_info[4]<<std::endl;
         std::cout<<"BUFFER_LENGTH: "<<evt->feb_info[5]<<std::endl;
         std::cout<<"FIRMWARE: "<<evt->feb_info[7]<<std::endl;
         std::cout<<"FRAME DATA: "<<std::endl;
         for (int index=0;index<length;index++) {
           std::cout<<"byte: "<<index<<" "<<(unsigned int)evt->event_data[index]<<std::endl;
         }
      #endif
      //memcpy (pdata, (void *) evt, sizeof(struct event_handler));
      memcpy (pdata, evt, sizeof(struct event_handler));
      //pdata = new event_handler;
      //pdata = evt;
      et_event_setlength(pe,sizeof(struct event_handler));
      #if THREAD_ME
        eb_lock.unlock();
      #endif  
    } 
    /* put event back into the ET system */
    #if THREAD_ME
      eb_lock.lock();
    #endif
    status = et_event_put(sys_id, attach, pe); //put the event away
    #if THREAD_ME
      eb_lock.unlock();
    #endif
    if (status != ET_OK) {
      printf("et_producer: put error\n");
      exit (0);
    } 
    if (!et_alive(sys_id)) {
        et_wait_for_alive(sys_id);
    }
    break; //done processing the event */
  } //while alive 
}

template <class X> void acquire_data::FillEventStructure(event_handler *evt, int bank, X *frame, channels *channelTrial) {


/*! \fn template <class X> void acquire_data::FillEventStructure(event_handler *evt, int bank, X *frame, channels *channelTrial)
 *
 * A templated function which takes a raw frame and puts it into the raw event structure for 
 * data processing by the event builder.
 *
 * \param event_handler *evt a pointer to the event handler structure
 * \param int bank an index for this data bank type
 * \param X *frame  the generic "frame" being processed
 * \param channels *channelTrial a pointer to the croc channel object being processed.
 *
 */
  #if DEBUG_ME
    std::cout<<"filling event structure: "<<bank<<" "<<frame->GetIncomingMessageLength()<<std::endl;
  #endif
  evt->feb_info[1]=daqController->GetID();
  evt->feb_info[4]=bank; //the bank type
  evt->feb_info[5]=frame->GetIncomingMessageLength(); //buffer length
  unsigned char tmp_buffer[(const unsigned int)evt->feb_info[5]]; //set the buffer size
  #if DEBUG_ME
    std::cout<<"Getting Data"<<std::endl;
  #endif
  for (unsigned int index=0;index<(evt->feb_info[5]);index++) {
    tmp_buffer[index] = channelTrial->GetBuffer()[index];
  }
  for (int i=0;i<evt->feb_info[5];i++) {
    evt->event_data[i] = tmp_buffer[i]; //load the event data
  }
  #if DEBUG_ME
    std::cout<<"Got Data"<<std::endl;
  #endif
  
  #if DEBUG_ME
    std::cout<<"Length: "<<frame->GetIncomingMessageLength()<<std::endl;
    std::cout<<"Length: "<<evt->feb_info[5]<<std::endl;
    for (int index=0;index<(frame->GetIncomingMessageLength());index++) {
      std::cout<<"FillStructure data: "<<(unsigned int)evt->event_data[index]<<std::endl;
    }
  #endif
}

#endif
