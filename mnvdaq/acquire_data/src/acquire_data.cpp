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

const int acquire_data::numberOfHits = 1;

void acquire_data::InitializeDaq(int id, RunningModes runningMode) 
{
/*! \fn void acquire_data::InitializeDaq()
 *
 * Executes the functions needed to fill the vectors with the numbers of 
 * CRIM's, CROC's, and FEB's which will need to be serviced during the
 * acquisition cycle.
 *
 * \param int id is the controller ID (used to build the sourceID later).
 * \param RunningModes runningMode describes the run mode and therfore sets CRIM timing mode.
 *
 */
#if DEBUG_ME
	std::cout << "\n\n\n" << std::endl;
	std::cout << "~~~~~ ENTERING InitializeDaq() ~~~~~~~~~~" << std::endl;
#endif
#if TIME_ME
	struct timeval start_time, stop_time;
	gettimeofday(&start_time, NULL);
#endif

	// Get the VME read/write access functions.
	daqAcquire = new acquire(); 

	// We need a controller to control the VME bus.
	daqController = new controller(0x00, id); 
	try {
		int error = daqController->ContactController();
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error contacting the VME controller!" << std::endl;
		exit(-1);
	} 

	// Then we need the cards which can read the data.
	/*! \note {Please note: for right now, the addresses of the cards have been 
	hard coded in.  This should be changed at some point, but for 
	the next few weeks, hard coding is the name of the game.} */
#if THREAD_ME
	boost::thread crim_thread(boost::bind(&acquire_data::InitializeCrim, this,0xE00000,1,runningMode)); 
	boost::thread croc_thread(boost::bind(&acquire_data::InitializeCroc,this, 0x010000,1)); 
#endif

	// Add look-up functions here - one for file content look-up and one by address scanning 
#if NO_THREAD
	InitializeCrim(0xE00000,1,runningMode);
	InitializeCroc(0x010000,1);
#endif

#if THREAD_ME
	crim_thread.join(); // Wait for the crim thread to return.
#if DEBUG_THREAD
	std::cout<<"Crim Thread Complete"<<std::endl;
#endif
	croc_thread.join(); // Wait for the croc thread to return.
#if DEBUG_THREAD
	std::cout<<"Croc Thread Complete"<<std::endl;
#endif
#endif
// endif THREAD_ME

	// Set the flag that tells us how many crocs are on this controller.
	daqController->SetCrocVectorLength(); 

	// Enable the CAEN IRQ handler.
	try {
		unsigned short bitmask = daqController->GetCrim()->GetInterruptMask();
		int error = CAENVME_IRQEnable(daqController->handle,~bitmask );
		if (error) throw error;
	} catch (int e) {
		std::cout<<"Error enabling CAEN VME IRQ handler"<<std::endl;
		exit(-8);
	}    

	// Done with VME card initialization procedures!
#if TIME_ME
	gettimeofday(&stop_time,NULL);
	double duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
		(start_time.tv_sec*1e6+start_time.tv_usec);
	std::cout << "******************************************************************************"
		<< std::endl; 
	std::cout << "Start Time: " << (start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
		<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
	std::cout << "******************************************************************************"
		<< std::endl; 
#endif
}


void acquire_data::InitializeCrim(int address, int index, RunningModes runningMode) 
{
/*! \fn void acquire_data::InitializeCrim(int address)
 *
 * This function checks the CRIM addressed by "address" is available by reading a register.  
 * Then the interrupt handler is set up.
 *
 * \param address an integer VME addres for the CRIM.
 * \param index an integer index used for internal bookkeeping.
 * \param runningMode an integer specifying what sort of run the DAQ is taking.
 */
#if DEBUG_ME
	std::cout << "\nInitializing CRIM " << (address>>16) << " for running mode " << runningMode << std::endl;
#endif
#if DEBUG_THREAD
	std::ofstream crim_thread;
	std::stringstream thread_number;
	thread_number<<address;
	std::string filename;
	filename = "crim_thread_"+thread_number.str();
	crim_thread.open(filename.c_str());
	crim_thread << "Initializing CRIM, Start" << std::endl;
#endif

	// Make a CRIM object on this controller.
	daqController->MakeCrim(address, index); 

	// Make sure that we can actually talk to the cards.
	try {
		int status = daqController->GetCrimStatus(index); 
		if (status) throw status;
	} catch (int e)  {
		std::cout << "Unable to read the status register for CRIM " << 
			((daqController->GetCrim(index)->GetCrimAddress())>>16) << std::endl;
		exit(-3);
	} 

	// Check running mode and perform appropriate initialization.
	switch (runningMode) {
		case Pedestal:
			std::cout << "Running Mode is Pedestal." << std::endl;
			// Initialize CRIM here.
			break;
		default:
			std::cout << "ERROR! No Running Mode defined!" << std::endl;
			exit(-4);
	}

	// Now set up the IRQ handler, initializing the global enable bit for the first go-around.
	SetupIRQ();

#if DEBUG_THREAD
	crim_thread << "In InitializeCrim, Done" << std::endl;
	crim_thread.close();
#endif

#if DEBUG_ME
	std::cout << "Finished initializing CRIM " << 
		(daqController->GetCrim(index)->GetCrimAddress()>>16) << std::endl;
#endif
}


void acquire_data::InitializeCroc(int address, int crocNo) 
{
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
	std::cout << "\nInitializing CROC " << (address>>16) << std::endl;
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

	// Make a CROC object on this controller.
	daqController->MakeCroc(address,crocNo); 

	// Make sure that we can actually talk to the cards.
	try {
		int status = daqController->GetCardStatus(crocNo);  
		if (status) throw status;
	} catch (int e)  {
		exit(-2);
	}

	// Now make threads which will search all channels on the croc to 
	// find which ones have FEB's on them.  Then set up the FEB's. 
#if THREAD_ME
	boost::thread *chan_thread[4];
#endif

	// Build the FEB list for each channel.
#if DEBUG_ME
	std::cout << "Building FEB List" << std::endl;
#endif
	for (int i=0;i<4;i++) {
		// Now set up the channels and FEB's.
		croc *tmpCroc = daqController->GetCroc(crocNo);
		bool avail = false;
		avail = tmpCroc->GetChannelAvailable(i);
		if (avail) {
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
	// If we are working in multi-threaded operation we need  
	// to wait for the each thread we launched to complete.
	for (int i=0;i<4;i++) {
		chan_thread[i]->join(); // Wait for all the threads to finish up before moving on.
#if DEBUG_THREAD
		croc_thread<<"Build FEB List: channel "<<i<<" thread completed"<<std::endl;
		croc_thread.close();
#endif
		delete chan_thread[i];
	}  
#endif

#if DEBUG
	std::cout << "RETURNED FROM BUILD FEB LIST" << std::endl;
#endif
}


// Please don't call this funciton...
int acquire_data::SetHV(feb *febTrial, croc *tmpCroc, channels *tmpChan,
	int newHV, int newPulse, int hvEnable) 
{
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

	// Compose a WRITE frame.
	Devices dev = FPGA;
	Broadcasts b = None;
	Directions d = MasterToSlave;
	FPGAFunctions f = Write;
	unsigned char val[1] = {2};
	febTrial->SetHVNumAve(val); 
	val[0] = 0;
	febTrial->SetHVManual(val); 
	febTrial->SetHVTarget(newHV); 
	val[0] = newPulse & 0xFF; 
	febTrial->SetHVPulseWidth(val);
	val[0] = hvEnable & 0xFF; 
	// char set_hv[2]; // unneeded?
	febTrial->SetHVEnabled(val);
	febTrial->SetGateLength(1702); 

	febTrial->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) febTrial->GetBoardNumber());
	febTrial->MakeMessage();

	// Send the message.
	try {
		int success = SendMessage(febTrial,tmpCroc, tmpChan,true); 
		if (success) throw success;
	} catch (int e) {
		std::cout<<"Unable to set HV on FEB: "<<febTrial->GetBoardNumber()<<" on channel: "
			<<tmpChan->GetChannelNumber()<<std::endl;
		exit(-12);
	}

	return 0;
}


// Please don't call this funciton...
int acquire_data::MonitorHV(feb *febTrial, croc *tmpCroc, channels *tmpChan) 
{
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

	// Compose a READ frame.
	Devices dev = FPGA;
	Broadcasts b = None;
	Directions d = MasterToSlave;
	FPGAFunctions f = Read;

	febTrial->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) febTrial->GetBoardNumber());
	febTrial->MakeMessage();
	// Send the frame.
	try {
		int success = SendMessage(febTrial, tmpCroc, tmpChan, true); 
		if (success) throw (success);
	} catch (int e) {
		std::cout<<"Unable to set HV on FEB: "<<febTrial->GetBoardNumber()<<" on channel: "
			<<tmpChan->GetChannelNumber()<<std::endl;
		exit(-12);
	}

	// Read data in the DPM.
	try {
		int success = ReceiveMessage(febTrial,tmpCroc, tmpChan);
		if (success) throw success;
	} catch (int e) {
		std::cout<<"Unable to monitor HV on FEB: "<<febTrial->GetBoardNumber()<<" on channel: "
			<<tmpChan->GetChannelNumber()<<std::endl;
		exit(-13);
	}

	// Extract the FEB's HV.
	int hv_value = febTrial->GetHVActual(); 

	// Return the value.
	return hv_value;
}


int acquire_data::SetupIRQ() 
{
/*!\fn int acquire_data::SetupIRQ()
 *
 * These are the steps to setting the IRQ:
 *  1) Select an IRQ LINE on which the system will wait for an assert.  
 *
 *  2) Set the Interrupt mask on the crim.
 *
 *  3) Check the interrupt status & clear any pending interrupts.  
 *
 *  4) Set the IRQ LEVEl which is asserted on the LINE.  We have set this to IRQ5, or 5 in the register
 *  when the CRIM is created.  (This also happens to be the power on default.)
 *
 *  5) Set the Global IRQ Enable bit.
 *
 *  6) Send this bitmask to the CRIM.
 *
 *  7) Enable the IRQ LINE on the CAEN controller to be the NOT of the IRQ LINE sent to the CRIM.
 *
 * Returns a status value.
 * To-Do: Update this function to work with more than one crim in the crate! 
 */

	int error = 0; 

	// Set up the crim interrupt mask.
	daqController->GetCrim()->SetInterruptMask(); 
	unsigned char crim_send[2] = {0,0};
	crim_send[0] = (daqController->GetCrim()->GetInterruptMask()) & 0xff;
	crim_send[1] = ((daqController->GetCrim()->GetInterruptMask())>>0x08) & 0xff;
	try {
		error = daqAcquire->WriteCycle( daqController->handle, 2, crim_send,
			daqController->GetCrim()->GetInterruptMaskAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth() );
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error setting crim IRQ mask in acquire_data::SetupIRQ!" << std::endl;
		daqController->ReportError(e);
		exit(-4);
	}

	// Check the interrupt status.
	try {
		crim_send[0] = 0; crim_send[1] = 0; 
		error = daqAcquire->ReadCycle( daqController->handle, crim_send,
			daqController->GetCrim()->GetInterruptStatusAddress(), daqController->GetAddressModifier(),
			daqController->GetDataWidth() ); 
		if (error) throw error;

		// Clear any pending interrupts.
		unsigned short interrupt_status = 0;
		interrupt_status = (unsigned short) (crim_send[0]|(crim_send[1]<<0x08));
		if (interrupt_status!=0) { 
			// Clear the pending interrupts.
			crim_send[0] = daqController->GetCrim()->GetClearInterrupts() & 0xff;
			crim_send[1] = (daqController->GetCrim()->GetClearInterrupts()>>0x08) & 0xff;
			try {
				error=daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
					daqController->GetCrim()->GetClearInterruptsAddress(), 
					daqController->GetAddressModifier(),
					daqController->GetDataWidth() ); 
				if (error) throw error;
			} catch (int e) {
				std::cout << "Error clearing crim interrupts in acquire_data::SetupIRQ: " << e << std::endl;
				daqController->ReportError(e);
				exit(-6);
			}
		}
	} catch (int e) {
		std::cout << "Error getting crim interrupt status in acquire_data::SetupIRQ!" << std::endl;
		daqController->ReportError(e);
		exit(-5);
	}

	// Now set the IRQ LEVEL.
	ResetGlobalIRQEnable();
	crim_send[0] = (daqController->GetCrim()->GetInterruptConfig()) & 0xff;
	crim_send[1] = ((daqController->GetCrim()->GetInterruptConfig())>>0x08) & 0xff;
#if DEBUG_ME
	std::cout.setf(std::ios::hex,std::ios::basefield);
	std::cout << "IRQ CONFIG = 0x" << daqController->GetCrim()->GetInterruptConfig() << std::endl;
	std::cout << "IRQ ADDR   = 0x" << daqController->GetCrim()->GetInterruptsConfigAddress() << std::endl;
	std::cout.setf(std::ios::dec,std::ios::basefield);
#endif
	try {
		error = daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
			daqController->GetCrim()->GetInterruptsConfigAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth() ); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error setting crim IRQ mask in acquire_data::SetupIRQ!" << std::endl;
		daqController->ReportError(e);
		exit(-4);
	}

	// Now enable the line on the CAEN controller.
	error = CAENVME_IRQEnable(daqController->handle,~daqController->GetCrim()->GetInterruptMask());

	return 0;
}


int acquire_data::ResetGlobalIRQEnable() 
{
/*!  \fn int acquire_data::ResetGlobalIRQEnable()
 *
 * Sets the global enable bit on the CRIM interrupt handler
 *
 * Returns a status value.
 *
 */

	// Set the global enable bit.
	daqController->GetCrim()->SetInterruptGlobalEnable(true);
	
	unsigned char crim_send[2];
	crim_send[0] = ((daqController->GetCrim()->GetInterruptConfig()) & 0xff);
	crim_send[1] = (((daqController->GetCrim()->GetInterruptConfig())>>0x08) & 0xff);
	try { 
		int error = daqAcquire->WriteCycle( daqController->handle, 2, crim_send,
			daqController->GetCrim()->GetInterruptsConfigAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth() );
		if (error) throw error;
	} catch (int e) {
		std::cout<<"Error setting IRQ Global Enable Bit "<<e<<std::endl;
		exit(-7);
	}
	return 0;
}


int acquire_data::BuildFEBList(int i, int croc_id) 
{
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
#if DEBUG_ME
	std::cout << "\nEntering BuildFEBList for Channel " << i << std::endl;
#endif
#if DEBUG_THREAD
	std::ofstream build_feb_thread;
	std::stringstream thread_number;
	thread_number << i << "_" << croc_id;
	std::string filename;
	filename = "FEB_list_"+thread_number.str();
	build_feb_thread.open(filename.c_str());
	build_feb_thread << "Called BuildFEBList" << std::endl;
#endif

	// Exract the CROC object and Channel object from the controller 
	// and assign them to a tmp of each type for ease of use.
	croc *tmpCroc = daqController->GetCroc(croc_id);
	channels *tmpChan = daqController->GetCroc(croc_id)->GetChannel(i);

	// This is a dynamic look-up of the FEB's on the channel.
	// Addresses numbers range from 1 to 15 and we'll loop
	// over all of them and look for S2M message headers.
	for (int j=1;j<16;j++) { 
		{ // Debug messages:
#if DEBUG_ME
			std::cout << " Making FEB: " << j << std::endl;
#endif
#if DEBUG_THREAD
			build_feb_thread << " Making FEB: " << j << std::endl;
#endif
		}

		// Make a "trial" FEB for the current address.
		feb *tmpFEB = tmpChan->MakeTrialFEB(j, numberOfHits); 
		{ // Debug messages:
#if DEBUG_ME
			std::cout << "  Made FEB:        " << i << std::endl;
			std::cout << "  Making Message:  " << i << std::endl;
#endif
#if DEBUG_THREAD
			build_feb_thread << "  Made FEB      : " << i << std::endl;
			build_feb_thread << "  Making Message: " << i << std::endl;
			build_feb_thread << "  New FEB Number: " << tmpFEB->GetBoardNumber() << std::endl;
#endif
		}
		
		// Build an outgoing message to test if an FEB of this address is available on this channel.
		tmpFEB->MakeMessage(); 
		{ // Debug messages:
#if DEBUG_ME
			std::cout << "  Made Message:     " << i << std::endl;
			std::cout << "  Sending Message:  " << i << std::endl;
#endif
#if DEBUG_THREAD
			build_feb_thread << "  Made Message:     " << i << std::endl;
			build_feb_thread << "  Sending Message:  " << i << std::endl;
#endif
		}

		// Send the message & delete the outgoingMessage.
		int success = SendMessage(tmpFEB, tmpCroc, tmpChan, true); 
		tmpFEB->DeleteOutgoingMessage();

		// Read the DPM & delete the message shell (?)
		success = ReceiveMessage(tmpFEB, tmpCroc, tmpChan);
		delete [] tmpFEB->message;
		{ // Debug messages:
#if DEBUG_THREAD
			build_feb_thread << "  BoardNumber--Receive: " << tmpFEB->GetBoardNumber() << std::endl;
			build_feb_thread << "  FEBNumber--Receive:   " << (int)tmpFEB->GetFEBNumber() << std::endl;
			build_feb_thread << "  HV?                   " << tmpFEB->GetHVActual() << std::endl;
#endif
		}

		// If the FEB is available, load it into the channel's FEB list and initialize the TriPs. 
		if (!success) {
#if DEBUG_ME
			std::cout<<"FEB: "<<tmpFEB->GetBoardNumber()<<" is available on this channel "
				<<tmpChan->GetChannelNumber()<<" "<<tmpFEB->GetInit()<<std::endl;
#endif
#if DEBUG_THREAD
			build_feb_thread<<"FEB: "<<tmpFEB->GetBoardNumber()<<" is available on this channel "
				<<tmpChan->GetChannelNumber()<<" "<<tmpFEB->GetInit()<<std::endl;
#endif
			// Add the FEB to the list.
			tmpChan->SetFEBs(j, numberOfHits); 

			// Set the FEB available flag.
			tmpChan->SetHasFebs(true);

			// Initialize the TriPs.
			//InitializeTrips(tmpFEB, tmpCroc, tmpChan);

			// Clean up the memory.
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
			// Clean up the memory.
			delete tmpFEB; 
		}  
	}

#if DEBUG_ME
	std::cout << "RETURNING FROM BUILD FEB LIST!" << std::endl;
#endif
#if DEBUG_THREAD
	build_feb_thread << "RETURNING FROM BUILD FEB LIST!" << std::endl;
	build_feb_thread.close();
#endif
	return 0;
}


// Please don't call this function.
int acquire_data::InitializeTrips(feb *tmpFEB, croc *tmpCroc, channels *tmpChan) 
{
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

	// Compose a read frame.
	tmpFEB->SetFEBDefaultValues();
	tmpFEB->MakeMessage();
	for (int index=0;index<tmpFEB->GetOutgoingMessageLength();index++) {
		std::cout << "Outgoing Message before send: " << (int)tmpFEB->GetOutgoingMessage()[index]
			<< std::endl;
	}
	try {
		// Send the message.
		int success = SendMessage(tmpFEB, tmpCroc, tmpChan, true);
		if (success) throw success;
	} catch (int e) {
		std::cout << "Unable to access already listed FEB: " << tmpFEB->GetBoardNumber()
			<< " on channel: " << tmpChan->GetChannelNumber() << std::endl;
		exit(-9);
	}
	for (int index=0;index<tmpFEB->GetOutgoingMessageLength();index++) {
		std::cout << "Outgoing Message after send: " << (int)tmpFEB->GetOutgoingMessage()[index]
			<< std::endl;
	}
	tmpFEB->DeleteOutgoingMessage();

	// Read the DPM.
	try {
		int success = ReceiveMessage(tmpFEB, tmpCroc, tmpChan);
		if (success) throw (success);
	} catch (int e) {
		std::cout<<"Unable to read message from FEB: "<<tmpFEB->GetBoardNumber()
			<<" on channel: "<<tmpChan->GetChannelNumber()<<std::endl;
		exit(-10);
	}
	delete [] tmpFEB->message;

	// Turn on the TriP power
	if (tmpFEB->GetTripPowerOff()) {
		unsigned char val[1] = {0}; // Zero -> All TriPs power on.
		tmpFEB->SetTripPowerOff(val);
		// Compose a write frame.
		Devices dev = FPGA;
		Broadcasts b = None;
		Directions d = MasterToSlave;
		FPGAFunctions f = Write;
		tmpFEB->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) tmpFEB->GetBoardNumber());
		tmpFEB->MakeMessage(); 
#if DEBUG_ME
		std::cout << "Turning on the TriPs!" << std::endl;
#endif
		// Send the frame.
		try {
			int success = SendMessage(tmpFEB, tmpCroc, tmpChan, true); 
			if (success) throw success;
		} catch (int e) {
			std::cout << "Unable to access already listed FEB: " << tmpFEB->GetBoardNumber()
				<< " on channel: " << tmpChan->GetChannelNumber() << std::endl;
			exit(-9);
		}
		// Read the DPM.
		try {
			int success = ReceiveMessage(tmpFEB,tmpCroc, tmpChan);
			if (success) throw (success);
		} catch (int e) {
			std::cout<<"Unable to read message from FEB: "<<tmpFEB->GetBoardNumber()
				<<" on channel: "<<tmpChan->GetChannelNumber()<<std::endl;
			exit(-10);
		}
#if DEBUG_ME
		std::cout << "Done turning on the TriPs." << std::endl;
#endif
	}
 
	for (int qq=0;qq<6;qq++) {
		tmpFEB->GetTrip(qq)->MakeMessage();
#if DEBUG_ME
		std::cout << "Init Trip Message Length: " << tmpFEB->GetTrip(qq)->GetOutgoingMessageLength()
			<< std::endl;
#endif
		// Send the frame.
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
	tmpFEB->SetInitialized(true); // Now the FEB is intitialzed and we're ready to go!

	//Done with the initialization procedures.
	return 0;
}


// This function has a very misleading name!
int acquire_data::GetBlockRAM(croc *crocTrial, channels *channelTrial) 
{
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
	std::cout << "   Entering acquire_data::GetBlockRAM." << std::endl;
#endif
	CVAddressModifier AM     = daqController->GetAddressModifier();
	CVAddressModifier AM_BLT = channelTrial->GetBLTModifier(); 
	CVDataWidth DWS          = crocTrial->GetDataWidthSwapped();

	unsigned short dpmPointer;
	unsigned char status[2];
	try {
		int error = daqAcquire->ReadCycle(daqController->handle, status, 
			channelTrial->GetDPMPointerAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error reading DPM pointer in acquire_data::GetBlockRAM!" << std::endl;
		daqController->ReportError(e);
		return (-e);
	} 
	dpmPointer = (int) (status[0] | status[1]<<0x08);
#if DEBUG_ME
	std::cout << "    dpmPointer: " << dpmPointer << std::endl;
#endif
	if (dpmPointer%2) { // Must read an even number of bytes.
		DPMData = new unsigned char [dpmPointer+1];
	} else {
		DPMData = new unsigned char [dpmPointer];
	}
	
	try {
		int success = daqAcquire->ReadBLT(daqController->handle, DPMData, dpmPointer, 
			channelTrial->GetDPMAddress(), AM_BLT, DWS);
		if (success) throw success;
	} catch (int e) {
		std::cout << "Error in acquire_data::GetBlockRAM!" << std::endl;
		daqController->ReportError(e);
		exit(-12);
	}
#if DEBUG_ME
	std::cout << "    Moving to SetBuffer..." << std::endl;
#endif
	channelTrial->SetDPMPointer(dpmPointer);
	channelTrial->SetBuffer(DPMData);
#if DEBUG_ME
	std::cout << "    Returned from SetBuffer." << std::endl;
	for (int index = 0; index < dpmPointer; index++) {
		printf("      Data Byte %02d = 0x%02X\n", index, DPMData[index]);
	}
	std::cout << "    Returning from acquire_data::GetBlockRAM." << std::endl;
#endif
	// Clean-up and return.
	delete [] DPMData;
	return 0;
}


template <class X> bool acquire_data::FillDPM(croc *crocTrial, channels *channelTrial, X *frame, 
	int outgoing_length, int incoming_length) 
{
/*! \fn template <class X> bool acquire_data::FillDPM(croc *crocTrial, channels *channelTrial, X *frame,
 *                            int outgoing_length, int incoming_length)
 *
 * A templated function for filling a CROC channel's DPM.  This function is always used; however, 
 * the DPM is not always filled before moving on to the next processing step.  This allows for a 
 * single block transfer of data from a channel's DPM to a buffer assigned to that channel for 
 * later processing.
 *
 * Currently, only one device's data is written to the DPM and is then processed.
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
	CVDataWidth DWS      = crocTrial->GetDataWidthSwapped();
	unsigned short dpmPointer;
	unsigned char status[2];

	try {
		int error = daqAcquire->ReadCycle(daqController->handle, status, 
			channelTrial->GetDPMAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Unable to read DPM Pointer in acquire_data::FillDPM!" << std::cout;
		daqController->ReportError(e);
		return false;
	}
	dpmPointer = (unsigned short) (status[0] | (status[1]<<0x08));

	if ( (dpmPointer<dpmMax) && ((dpmMax-incoming_length)>incoming_length) ) {
		SendMessage(frame, crocTrial, channelTrial, true);
		return true; 
	}
	return false;
}


bool acquire_data::TakeAllData(feb *febTrial, channels *channelTrial, croc *crocTrial, 
	event_handler *evt, int thread, et_att_id attach, et_sys_id sys_id) 
{
/*! \fn bool acquire_data::TakeAllData(feb *febTrial, channels *channelTrial, croc *crocTrial,
 *                                event_handler *evt, int thread, et_att_id  attach, et_sys_id sys_id)
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
 */

#if TIME_ME
	// Setup an output file if we're going to estimate execution timing.
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
	std::cout << "\n----------------Entering acquire_data::TakeAllData----------------------" << std::endl;
#endif
#if THREAD_ME
	// Set up some threads for using the event builder.
	boost::thread *eb_threads[3];
#endif

	// Execution Status Vars.
	int success       = 0;
	bool memory_reset = false;
	int hits          = -1;

	// Fill entries in the event_handler structure for this event -> The sourceID.
	evt->new_event   = false; // We are always processing an existing event with this function!!!
	evt->feb_info[0] = 0;     // We need to sort this out later (link number) -> *Probably* ALWAYS 0.
	evt->feb_info[1] = 0;     // Crate number (make later). TODO, give this the CONTROLLER_ID
	evt->feb_info[2] = crocTrial->GetCrocID();
	evt->feb_info[3] = channelTrial->GetChannelNumber();
	evt->feb_info[6] = febTrial->GetFEBNumber();

	// Make sure the DPM is reset for taking the FEB INFO Frames.
	memory_reset = ResetDPM(crocTrial, channelTrial);

	// Begin reading FEB frame information.
	try {
		if (!memory_reset) throw memory_reset;

#if TIME_ME
		struct timeval start_time, stop_time;
		gettimeofday(&start_time, NULL);
#endif
		// Compose an FPGA read frame.
		Devices dev = FPGA;
		Broadcasts b = None;
		Directions d = MasterToSlave;
		FPGAFunctions f = Read;
		febTrial->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int) febTrial->GetBoardNumber());
		febTrial->MakeMessage();
		try {
			success = AcquireDeviceData(febTrial, crocTrial, channelTrial, FEB_INFO_SIZE);
			if (success) throw success;
		} catch (bool e) {
			std::cout << "Error adding FEB Information to DPM." << std::endl;
			exit(-1001);
		}
#if SHOW_REGISTERS
		febTrial->message = new unsigned char [FEB_INFO_SIZE];
		for (int debug_index=0; debug_index<febTrial->GetIncomingMessageLength(); debug_index++) {
			febTrial->message[debug_index] = channelTrial->GetBuffer()[debug_index];
		}
		febTrial->DecodeRegisterValues(febTrial->GetIncomingMessageLength());
		febTrial->ShowValues();
		febTrial->DeleteOutgoingMessage(); // Required after MakeMessage()
		delete [] febTrial->message;
#endif
#if TIME_ME
		lock.lock();
		gettimeofday(&stop_time,NULL);
		duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
			(start_time.tv_sec*1e6+start_time.tv_usec);
		take_data_log << "******************FEB FRAMES*********************************" << std::endl; 
		take_data_log << "Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec) << " Stop Time: "
			<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
		take_data_log << "*************************************************************" << std::endl; 
		frame_acquire_log << evt->gate_info[1] << "\t" << thread << "\t" << "2" << "\t" << 
			(start_time.tv_sec*1000000+start_time.tv_usec) << "\t" << 
			(stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
		lock.unlock();
#endif
#if DEBUG_ME
		std::cout << "  Acquired FEB data for" << std::endl;
		std::cout << "    CROC:    " << (crocTrial->GetCrocAddress()>>16) << std::endl;
		std::cout << "    Channel: " << channelTrial->GetChannelNumber() << std::endl;
		std::cout << "    FEB:     " << febTrial->GetBoardNumber() << std::endl;
		std::cout << "------------------------------------------------------------" << std::endl;
#endif
#if TIME_ME
		gettimeofday(&start_time, NULL);
#endif
		// Fill the event_handler structure with the newly acquired data
		FillEventStructure(evt, 2, febTrial, channelTrial);
#if TIME_ME
		lock.lock();
		gettimeofday(&stop_time,NULL);
		duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
			(start_time.tv_sec*1e6+start_time.tv_usec);
		take_data_log << "******************FEB FILL EVENT STRUCTURE********************" << std::endl; 
		take_data_log << "Start Time: " << (start_time.tv_sec*1e6+start_time.tv_usec) << " Stop Time: "
			<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
		take_data_log << "**************************************************************" << std::endl; 
		frame_acquire_log << evt->gate_info[1] << "\t" << thread << "\t" << "10" << "\t"
			<< (start_time.tv_sec*1000000+start_time.tv_usec) << "\t"
			<< (stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
		lock.unlock();
#endif
		evt->feb_info[7]=(int)febTrial->GetFirmwareVersion();
#if DEBUG_ME
		std::cout << "  Firmware Version (header val): " << (int)evt->feb_info[7] << std::endl;
		std::cout << "  Data Length (header val)     : " << evt->feb_info[5] << std::endl;
		std::cout << "  Bank Type (header val)       : " << evt->feb_info[4] << std::endl;
#endif

		// Send the data to the EB via ET.
#if DEBUG_ME
		std::cout << " Contacting the Event Builder Service" << std::endl;
		std::cout << "  Bank  : " << evt->feb_info[4] << std::endl;
		std::cout << "  Thread: " << thread << std::endl;
#endif
#if TIME_ME
		gettimeofday(&start_time, NULL);
#endif
#if NO_THREAD
		ContactEventBuilder(evt, thread, attach, sys_id); 
		channelTrial->DeleteBuffer();
#elif THREAD_ME
		eb_threads[0] = new boost::thread((boost::bind(&acquire_data::ContactEventBuilder,this,
			boost::ref(evt),thread,attach,sys_id)));
		channelTrial->DeleteBuffer();
#endif
#if TIME_ME
		lock.lock();
		gettimeofday(&stop_time,NULL);
		duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
			(start_time.tv_sec*1e6+start_time.tv_usec);
		take_data_log << "******************FEB FRAMES: CONTACT_EB****************************" << std::endl; 
		take_data_log << "Start Time: " << (start_time.tv_sec*1e6+start_time.tv_usec) << " Stop Time: "
			<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
		take_data_log << "********************************************************************" << std::endl; 
		frame_acquire_log << evt->gate_info[1] << "\t" << thread << "\t" << "20" << "\t"
			<< (start_time.tv_sec*1000000+start_time.tv_usec) << "\t"
			<< (stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
		lock.unlock();
#endif 
#if DEBUG_ME
		std::cout << "Back from EB..." << std::endl;
#endif

		// Read a discriminator frame.
#if DEBUG_ME
		std::cout << "---------------------------------------------------------------------" << std::endl;
		std::cout << "  DISC FRAMES" << std::endl;
#endif
		// TODO, Probably want to just leave this on by default, the DAQ won't have read the 
		// actual TriP programming registers at this point unless we decide to for a special 
		// first event (or zeroth) event readout.
		// ----
		// First, decide if the discriminators are on.
		bool disc_set = false;
		for (int trip_index = 0; trip_index < 6; trip_index++) {
			int vth = febTrial->GetTrip(trip_index)->GetTripValue(9);
#if DEBUG_ME
			std::cout << "   febTrial vth == " << vth << std::endl;
#endif 
			if (vth) {
				disc_set=true;
				break;
			}
		}

		if (disc_set) { 
			memory_reset = ResetDPM(crocTrial, channelTrial); 
#if TIME_ME
			gettimeofday(&start_time, NULL);
#endif
			try {
				success = AcquireDeviceData(febTrial->GetDisc(), crocTrial, channelTrial, FEB_DISC_SIZE);
				if ((success)||(!memory_reset)) throw success;
			} catch (bool e) {
				std::cout<<"Error adding DISC Information to DPM"<<std::endl;
				exit(-1002);
			}
#if TIME_ME
			lock.lock();
			gettimeofday(&stop_time,NULL);
			duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
				(start_time.tv_sec*1e6+start_time.tv_usec);
			take_data_log << "*************************DISC FRAMES**************************" << std::endl; 
			take_data_log << "Start Time: " << (start_time.tv_sec*1e6+start_time.tv_usec) << " Stop Time: "
				<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
			take_data_log << "**************************************************************" << std::endl; 
			frame_acquire_log << evt->gate_info[1] << "\t" << thread << "\t" << "1" << "\t" << 
				(start_time.tv_sec*1000000+start_time.tv_usec) << "\t" << 
				(stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
			lock.unlock();
			gettimeofday(&start_time, NULL);
#endif
			// Fill the event_handler structure.
			FillEventStructure(evt, 1, febTrial->GetDisc(), channelTrial);
#if TIME_ME
			lock.lock();
			gettimeofday(&stop_time,NULL);
			duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
				(start_time.tv_sec*1e6+start_time.tv_usec);
			take_data_log << "*************************DISC FILL EVENT STRUCTURE*****************" << std::endl; 
			take_data_log << "Start Time: " << (start_time.tv_sec*1e6+start_time.tv_usec) << " Stop Time: "
				<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
			take_data_log << "*******************************************************************" < <std::endl; 
			frame_acquire_log << evt->gate_info[1] << "\t" << thread << "\t" << "11" << "\t"
				<< (start_time.tv_sec*1000000+start_time.tv_usec) << "\t"
				<< (stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
			lock.unlock();
#endif
#if DEBUG_ME
			std::cout << "  Acquired DISC data for " << std::endl;
			std::cout << "    CROC:    " << crocTrial->GetCrocID() << std::endl;
			std::cout << "    Channel: " << channelTrial->GetChannelNumber() << std::endl;
			std::cout << "    FEB:     " << febTrial->GetBoardNumber() << std::endl;
			std::cout << "-------------------------------------------------------------------" << std::endl;
#endif
#if NO_THREAD
			// Contact the EB via ET.
			ContactEventBuilder(evt, thread, attach, sys_id); 
			channelTrial->DeleteBuffer();
#elif THREAD_ME
			eb_threads[0] = new boost::thread((boost::bind(&acquire_data::ContactEventBuilder,this,
				boost::ref(evt),thread,attach,sys_id)));
			channelTrial->DeleteBuffer();
#endif
			// Calculate the hits variable so we can read the correct number of ADC Frames. 
			hits = evt->feb_info[8];
			// We need to add a readout for the end-of-gate "hit."
			hits++; 
			// Should add a check here on equality of pairs?
		} // End discriminators-on check.

		// Now read the ADC Frames.
#if DEBUG_ME
		std::cout << "------------------------------------------------------------" << std::endl;
		std::cout << "     ADC FRAMES  " << std::endl;
#endif
		if (hits == -1) hits = 1; 
		// Actually want to do ReadHit5 first, need to fix this...
		for (int i=0; i<hits; i++) {
			if (!(memory_reset = ResetDPM(crocTrial, channelTrial))) {
				std::cout<<"Unable to reset DPM!"<<std::endl;
				exit(-1004);
			} //reset the DPM
			try {
				success = AcquireDeviceData(febTrial->GetADC(i), crocTrial, channelTrial,FEB_HITS_SIZE);
				if (success) throw success;
			} catch (bool e) {
				std::cout<<"Error adding ADC Information to the DPM"<<std::endl;
				exit(-1003);
			}
#if TIME_ME
			gettimeofday(&start_time, NULL);
			lock.lock();
			gettimeofday(&stop_time,NULL);
			duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
				(start_time.tv_sec*1e6+start_time.tv_usec);
			take_data_log << "********************ADC FRAMES****************************" << std::endl; 
			take_data_log << "Start Time: " << (start_time.tv_sec*1e6+start_time.tv_usec) << 
				" Stop Time: " << (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << 
				(duration/1e6) << std::endl;
			take_data_log << "**********************************************************" << std::endl; 
			frame_acquire_log << evt->gate_info[1] << "\t" << thread << "\t" << "0" << "\t" << 
				(start_time.tv_sec*1000000+start_time.tv_usec) << "\t" << 
				(stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
			lock.unlock();
			gettimeofday(&start_time, NULL);
#endif
#if DEBUG_ME
			std::cout << "------------------------------------------------------------" << std::endl;
#endif
			// Fill the event_handler structure with data.
			FillEventStructure(evt, 0, febTrial->GetADC(i), channelTrial);
#if TIME_ME
			lock.lock();
			gettimeofday(&stop_time,NULL);
			duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
				(start_time.tv_sec*1e6+start_time.tv_usec);
			take_data_log << "********************ADC FILL EVENT STRUCTURE********************" < <std::endl; 
			take_data_log << "Start Time: " << (start_time.tv_sec*1e6+start_time.tv_usec) << " Stop Time: "
				<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
			take_data_log << "****************************************************************" << std::endl; 
			frame_acquire_log << evt->gate_info[1] << "\t" << thread << "\t" << "12" << "\t"
				<< (start_time.tv_sec*1000000+start_time.tv_usec) << "\t"
				<< (stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
			lock.unlock();
#endif
			// Contact the EB via ET.
#if NO_THREAD
			ContactEventBuilder(evt, thread, attach, sys_id); 
			channelTrial->DeleteBuffer();
#elif THREAD_ME
			eb_threads[2] = new boost::thread((boost::bind(&acquire_data::ContactEventBuilder,this,
				boost::ref(evt),thread,attach,sys_id)));
			channelTrial->DeleteBuffer();
#endif
#if DEBUG_ME
			std::cout << "  Acquired ADC data for" << std::endl;
			std::cout << "    CROC:    " << crocTrial->GetCrocID() << std::endl;
			std::cout << "    Channel: " << channelTrial->GetChannelNumber() << std::endl;
			std::cout << "    FEB:     " << febTrial->GetBoardNumber() << std::endl;
#endif
		} //end of hits loop

	} catch (bool e)  {
		std::cout<<"The DPM wasn't reset! If you'd done this right, it wouldn't have happened!"<<std::endl;
		exit(-1000);
	}

	// Wait for threads to join if nedessary.
#if THREAD_ME
	eb_threads[0]->join();
	eb_threads[2]->join();
#endif 

#if DEBUG_ME
	std::cout << "--------Returning from TakeAllData--------" << std::endl;
#endif
	return success;
}


bool acquire_data::ResetDPM(croc *crocTrial, channels *channelTrial) 
{
/*! \fn bool acquire_data::ResetDPM(croc *crocTrial, channels *channelTrial)
 *
 * A function which clears the status register & resets the DPM pointer on a CROC channel.
 *
 * \param croc *crocTrial  a pointer to a croc object
 * \param channels *channelTrial a pointer to a channel object
 *
 * Returns a status bit.
 */
#if DEBUG_ME
	std::cout << "    acquire_data::ResetDPM for CROC " << (crocTrial->GetCrocAddress()>>16) << " Channel " << channelTrial->GetChannelNumber() << std::endl;
#endif
	bool reset = false;
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth DW = daqController->GetDataWidth();
	CVDataWidth DWS = crocTrial->GetDataWidthSwapped();
	unsigned char message[2]={0x0A, 0x0A}; // 0202 + 0808 for clear status AND reset.
	 // Clear the status & reset the pointer.
	daqAcquire->WriteCycle(daqController->handle, 2, message, 
		channelTrial->GetClearStatusAddress(), AM, DW);
	// Check the value of the pointer.  Don't actually need to do 
	// this every time, better would be checking the status register.
	daqAcquire->ReadCycle(daqController->handle,message, 
		channelTrial->GetDPMPointerAddress(), AM, DWS); 
	unsigned short dpmPointer = (unsigned short) (message[0] | (message[1]<<0x08));
#if DEBUG_ME
	std::cout << "     dpmPointer after reset: " << dpmPointer << std::endl;
	// std::cout << "  message[0]: " << (int) message[0] <<std::endl;
	// std::cout << "  message[1]: " << (int) message[1] <<std::endl;
#endif
	// Need to check status register too!!
	if (dpmPointer==2) reset = true; // Not enough!
#if DEBUG_ME
	std::cout << "     Exiting ResetDPM." << std::endl;
#endif
	return reset;
}


template <class X> int acquire_data::SendMessage(X *device, croc *crocTrial, 
	channels *channelTrial, bool singleton) 
{
/*! \fn template <class X> int acquire_data::SendMessage(X *device, croc *crocTrial, channels *channelTrial, bool singleton)
 *
 * A templated function for sending messages to a generic device.  This function is used throughout the 
 * acquisition sequence.
 *
 * \param X *device the "frame" being processed
 * \param croc *crocTrial a pointer to the croc object 
 * \param channels *channelTrial a pointer to a croc channel object
 * \param bool singleton a flag telling us whether we are going to do one or more than one send (for fill DPM)
 *
 * Returns a status integer.
 *
 */
	int success = 1; // Flag for finding an feb on the channel.
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth DW       = daqController->GetDataWidth();
	CVDataWidth DWS      = crocTrial->GetDataWidthSwapped();

	unsigned char send_message[2] ={0x01, 0x01}; // Send message mask.
	unsigned short status;
	unsigned char reset_status[2];
	if (singleton) {
		int error;
		unsigned char reset_message[2] ={0x0A, 0x0A}; // Clear status & Reset DPM Pointer mask.
		// Read the status register... why?... This seems like an uneeded step...
		/*
		try {
			int error = daqAcquire->ReadCycle(daqController->handle, reset_status, 
				channelTrial->GetStatusAddress(), AM, DW);
			if (error) throw error;
		} catch (int e) {
			daqController->ReportError(e);
			std::cout << "Unable to Read the Status Register in acquire_data::SendMessage!" << std::endl;
		}
		// Check for errors?  Why read if we aren't error checking?
		*/
		// Clear status & Reset DPM Pointer
		try {
			error = daqAcquire->WriteCycle(daqController->handle, 2, reset_message, 
				channelTrial->GetClearStatusAddress(), AM, DW);
			if (error) throw error;
		} catch (int e) {
			daqController->ReportError(e);
			std::cout << "Unable to Clear the Status & Reset DPM Pointer in acquire_data::SendMessage!" 
				<< std::endl;
		}
		// Read the status register.
		try {
			error = daqAcquire->ReadCycle(daqController->handle, reset_status, 
				channelTrial->GetStatusAddress(), AM, DW);
			if (error) throw error;
		} catch (int e) {
			daqController->ReportError(e);
			std::cout << "Unable to Read the Status Register in acquire_data::SendMessage!" << std::endl;
		}
		status = (unsigned short) (reset_status[0] | reset_status[1]<<0x08);
#if DEBUG_ME
		std::cout.setf(std::ios::hex,std::ios::basefield);
		std::cout << " Channel " << channelTrial->GetChannelNumber() << " Status: 0x" << status << std::endl;
		std::cout.setf(std::ios::dec,std::ios::basefield);
#endif
		channelTrial->SetChannelStatus(status);
		// Check for errors.  May want to use a different function / condition eventually...
		try {
			if (status!=0x3700) throw (1);
		} catch (int e) {
			std::cout.setf(std::ios::hex,std::ios::basefield);
			std::cout << "Unable to reset!  Status = 0x" << status << std::endl;
			std::cout << " Channel Number: " << channelTrial->GetChannelNumber() << std::endl;
#if DEBUG_ME
			std::cout << " Checked the status from an error condition!" << std::endl;
#endif
			channelTrial->DecodeStatusMessage();
			exit(-103);
		}
	}

	int synch, deserializer;
	deserializer = status & 0x0400;
	synch        = status & 0x0200;
	if ((deserializer) && (synch)) {
		// Write the message to the channel FIFO.
		try {
			int error = daqAcquire->WriteCycle(daqController->handle, device->GetOutgoingMessageLength(), 
				device->GetOutgoingMessage(), channelTrial->GetFIFOAddress(), AM, DWS);
			if (error) throw error; 
		} catch (int e) {
			std::cout << " Error in acquire_data::SendMessage while writing to the FIFO!" << std::endl;
			daqController->ReportError(e);
			exit(-e);
		}
		//
		// // FIFO BLT is a bit funky for a general class function...
		// int count;
		// CAENVME_FIFOBLTWriteCycle(daqController->handle, channelTrial->GetFIFOAddress(), 
		// 	device->GetOutgoingMessage(), device->GetOutgoingMessageLength(), 
		// 	AM, DWS, &count);   
		//
		// Send the message.
		daqAcquire->WriteCycle(daqController->handle, 2, send_message, 
			channelTrial->GetSendMessageAddress(), AM, DW); 
		while (success) {
			// Wait for the message to be sent and recieved.
			daqAcquire->ReadCycle(daqController->handle, reset_status, 
				channelTrial->GetStatusAddress(), AM, DW); 
			status = (unsigned short) (reset_status[0] | reset_status[1]<<0x08);
			channelTrial->SetChannelStatus(status);
			success = channelTrial->DecodeStatusMessage();
		}
	}  
	return success;
}


template <class X> int acquire_data::ReceiveMessage(X *device, croc *crocTrial, channels *channelTrial) 
{
/*! \fn template <class X> int acquire_data::ReceiveMessage(X *device, croc *crocTrial, channels *channelTrial)
 *
 * A templated function for receiving messages to a generic device.  This function is used throughout the 
 * acquisition sequence.
 *
 * \param X *device the "frame" being processed
 * \param croc *crocTrial a pointer to the croc object 
 * \param channels *channelTrial a pointer to a croc channel object
 *
 * Returns a status bit.
 *
 */
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVAddressModifier AM_BLT = channelTrial->GetBLTModifier();
	CVDataWidth DWS = crocTrial->GetDataWidthSwapped();

	unsigned short dpmPointer;
	unsigned char status[2];
	daqAcquire->ReadCycle(daqController->handle, status, channelTrial->GetDPMPointerAddress(), AM, DWS);
	dpmPointer = (unsigned short) (status[0] | status[1]<<0x08);
#if DEBUG_ME
	std::cout << "DPM Pointer (ReceiveMessage): " << dpmPointer << std::endl;
#endif
	device->SetIncomingMessageLength(dpmPointer-2);
	// We must read an even number of bytes.
	if (dpmPointer%2) {
		device->message = new unsigned char [dpmPointer+1];
	} else {
		device->message = new unsigned char [dpmPointer];
	}
	daqAcquire->ReadBLT(daqController->handle, device->message, dpmPointer, 
		channelTrial->GetDPMAddress(), AM_BLT, DWS);
	bool success = device->CheckForErrors();
	if (success) {
		return success; // There were errors.
	}
	device->DecodeRegisterValues(dpmPointer-2);
	return success;
}


template <class X> int acquire_data::AcquireDeviceData(X *frame, croc *crocTrial, 
	channels *channelTrial, int length) 
{
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
	std::cout << "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" << std::endl;
	std::cout << " Entering acquire_data::AcquireDeviceData" << std::endl;
	std::cout << "  CROC Address:   " << (crocTrial->GetCrocAddress()>>16) << std::endl;
	std::cout << "  Channel Number: " << channelTrial->GetChannelNumber() << std::endl;
	std::cout.setf(std::ios::hex,std::ios::basefield);
	std::cout << "  Device:         0x" << frame->GetDeviceType() << std::endl;
	std::cout.setf(std::ios::dec,std::ios::basefield);
#endif
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth DWS      = crocTrial->GetDataWidthSwapped();
	int success          = 0;
	// Try to add this frame's data to the DPM.
	try { 
		success = FillDPM(crocTrial, channelTrial, frame, frame->GetIncomingMessageLength(), length);
		if (!success) throw success; 
		unsigned short dpmPointer;
		unsigned char status[2];
		daqAcquire->ReadCycle(daqController->handle, status, 
			channelTrial->GetDPMPointerAddress(), AM, DWS);
		dpmPointer = (unsigned short)(status[0] | status[1]<<0x08);
		frame->SetIncomingMessageLength(dpmPointer-2);
#if DEBUG_ME
		std::cout << "  acquire_data::AcquireDeviceData dpmPointer = " << dpmPointer << std::endl;
		std::cout << "  Message Length: " << frame->GetIncomingMessageLength() << std::endl;
#endif 
		success = GetBlockRAM(crocTrial, channelTrial); 
		frame->message = new unsigned char [frame->GetIncomingMessageLength()];
		for (int index=0;index<frame->GetIncomingMessageLength();index++) {
			frame->message[index] = channelTrial->GetBuffer()[index];
		}
		frame->DecodeRegisterValues(frame->GetIncomingMessageLength());
		delete [] frame->message;
		if (success) throw success; 
	} catch (bool e) { 
		// If unsuccessful, the DPM doesn't have enough memory, and we need to process what is there (?)
		std::cout << "DPM Fill Failure!  DPM Should have been reset before tyring to use!" << std::endl;
		exit(-4001);
	}
#if DEBUG_ME
	std::cout << "  AcquireDeviceData success: " << success << std::endl;
	std::cout << "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" << std::endl;
#endif
	return success;
}


void acquire_data::TriggerDAQ(int a) 
{
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
			daqController->GetCrim()->SetupOneShot(); // Prep a shot (software only).
			unsigned char crim_send[2];
			// Send the timing setup request.
			crim_send[0] = daqController->GetCrim()->GetTimingSetup() & 0xff;
			crim_send[1] = (daqController->GetCrim()->GetTimingSetup()>>0x08) & 0xff;
			try {
				error = daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
					daqController->GetCrim()->GetTimingRegister(), AM, DW); 
				if (error) throw error;
			} catch (int e) {
				std::cout << "Unable to set the CRIM Timing Mode!" << std::endl;
				daqController->ReportError(e);
				exit(-2002);
			}
#if DEBUG_ME
			std::cout<<"  Sent Timing Request"<<std::endl;
#endif
			// Send the gate width!  NONONONONO not here!
			crim_send[0] = daqController->GetCrim()->GetGateWidth() & 0xff;
			crim_send[1] = (daqController->GetCrim()->GetGateWidth()>>0x08) & 0xff;
			try {
				error=daqAcquire->WriteCycle(daqController->handle,2,crim_send,
					daqController->GetCrim()->GetGateRegister(), AM,DW); //send it
				if (error) throw error;
			} catch (int e) {
				std::cout << "Unable to set trigger width register!" << std::endl;
				daqController->ReportError(e);
				exit(-2003);
			}
#if DEBUG_ME
			std::cout << "  Sent Gate Width" << std::endl;
#endif
			// Pulse delay! Also not here!
			crim_send[0] = daqController->GetCrim()->GetTcalbPulse() & 0xff;
			crim_send[1] = (daqController->GetCrim()->GetTcalbPulse()<<0x08) & 0xff;
			try {
				error=daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
					daqController->GetCrim()->GetTCalbRegister(), AM, DW);
				if (error) throw error;
			} catch (int e) {
				std::cout << "Unable to set pulse delay register!" << std::endl;
				daqController->ReportError(e);
				exit(-2004);
			}
#if DEBUG_ME
			std::cout << "  Sent TCALB Delay" << std::endl;
#endif
			// Start the sequencer (trigger CNRST software pulse)
			try {
				unsigned char send_pulse[2];
				send_pulse[0] = daqController->GetCrim()->GetSoftCNRST() & 0xff;
				send_pulse[1] = (daqController->GetCrim()->GetSoftCNRST()>>0x08)&0xff;
				error = daqAcquire->WriteCycle(daqController->handle, 2, send_pulse,
					daqController->GetCrim()->GetCNRSTRegister(), AM, DW); //send it
				if (error) throw error;
			} catch (int e) {
				std::cout<<"Unable to set pulse delay register"<<std::endl;
				exit(-2005);
			}
#if DEBUG_ME
			std::cout << "-->Sent Sequencer Init. Signal!" << std::endl;
#endif
			break;
		default:
			std::cout << "We don't have that trigger mode coded up yet!" << std::endl;
			exit(-2001);
	}  
}


void acquire_data::WaitOnIRQ() 
{
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
	std::cout << "  Entering acquire_data::WaitOnIRQ: IRQLevel = " << daqController->GetCrim()->GetIRQLevel() << std::endl;
#endif
#if ASSERT_INTERRUPT
#if DEBUG_ME
	std::cout << "  Asserting Interrupt!" << std::endl;
#endif
	try {
		// A 1000 ms timeout.
		error = CAENVME_IRQWait(daqController->handle, daqController->GetCrim()->GetIRQLevel(), 1); 
		if (error!=-5) {
			if (error) throw error;
		} else {
			error = CAENVME_IRQWait(daqController->handle, daqController->GetCrim()->GetIRQLevel(), 1); 
			if (error) throw error;
		}
	} catch (int e) {
		std::cout << "The IRQ Wait probably timedout..." << e << std::endl;
		exit(-3000);  
	}
#endif

#if POLL_INTERRUPT
#if DEBUG_ME
	std::cout << "  Polling Interrupt!" << std::endl;
#endif
	unsigned short interrupt_status = 0;
	unsigned char crim_send[2];
	while (!(interrupt_status&0x04)) { //0x04 is the IRQ Line of interest
		try {
			crim_send[0] = 0; crim_send[1] = 0;
			error=daqAcquire->ReadCycle(daqController->handle, crim_send,
				daqController->GetCrim()->GetInterruptStatusAddress(), 
				daqController->GetAddressModifier(),
				daqController->GetDataWidth()); //send it 
			if (error) throw error;
			interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08));
		} catch (int e) {
			std::cout << "Error getting crim interrupt status!" << std::endl;
			daqController->ReportError(e);
			exit(-5);
		}
	}
	// Clear the interrupt after acknowledging it.
	crim_send[0] = daqController->GetCrim()->GetClearInterrupts() & 0xff;
	crim_send[1] = (daqController->GetCrim()->GetClearInterrupts()>>0x08) & 0xff;
	try {
		error=daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
			daqController->GetCrim()->GetClearInterruptsAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth()); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error clearing crim interrupts!" << std::endl;
		daqController->ReportError(e);
		exit(-6);
	}
#endif
}


void acquire_data::AcknowledgeIRQ() 
{
/*! \fn void acquire_data::AcknowledgeIRQ() 
 *
 * A function which acknowledges and resets the interrupt handler.
 *
 */
	CVDataWidth DW = daqController->GetDataWidth();
	int error;
	try {
		unsigned short vec;
		error = CAENVME_IACKCycle(daqController->handle, daqController->GetCrim()->GetIRQLevel(), 
			&vec, DW);
#if DEBUG_ME
		std::cout << "IRQ LEVEL: " << daqController->GetCrim()->GetIRQLevel() << " VEC: " << vec << std::endl;
#endif
		unsigned short interrupt_status;
		unsigned char crim_send[2];
		crim_send[0] = 0; crim_send[1] = 0;  
		error=daqAcquire->ReadCycle(daqController->handle, crim_send,
			daqController->GetCrim()->GetInterruptStatusAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth()); 
		interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08)); 

		while (interrupt_status) {
			try {
				crim_send[0] = 0; crim_send[1] = 0;
				error=daqAcquire->ReadCycle(daqController->handle, crim_send,
					daqController->GetCrim()->GetInterruptStatusAddress(), 
					daqController->GetAddressModifier(),
					daqController->GetDataWidth()); 
				if (error) throw error;
				interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08)); 

				// Clear the interrupt after acknowledging it.
				crim_send[0] = daqController->GetCrim()->GetClearInterrupts() & 0xff;
				crim_send[1] = (daqController->GetCrim()->GetClearInterrupts()>>0x08) & 0xff;
				try {
					error=daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
						daqController->GetCrim()->GetClearInterruptsAddress(), 
						daqController->GetAddressModifier(),
						daqController->GetDataWidth()); 
					// Read the status register 
					crim_send[0] = 0; crim_send[1] = 0; 
					error=daqAcquire->ReadCycle(daqController->handle, crim_send,
						daqController->GetCrim()->GetInterruptStatusAddress(), 
						daqController->GetAddressModifier(),
						daqController->GetDataWidth()); 
					if (error) throw error;
					interrupt_status = (crim_send[0]|(crim_send[1]<<0x08)); 
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
			CVIRQLevels irqLevel = daqController->GetCrim()->GetIRQLevel();
#if DEBUG_ME
			std::cout << "Set IRQ LEVEL: " << irqLevel << " Returned IRQ LEVEL: " << vec << std::endl;
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


void acquire_data::ContactEventBuilder(event_handler *evt, int thread, 
	et_att_id attach, et_sys_id sys_id) 
{
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
	{ // Debug statements
#if DEBUG_THREAD
		std::ofstream contact_thread;
		std::string filename;
		std::stringstream thread_no;
		thread_no<<thread;
		filename = "contact_eb_"+thread_no.str();
		contact_thread.open(filename.c_str());
		contact_thread << "Entering acquire_data::ContactEventBuilder..." << std::endl;
		contact_thread << " In Event Builder the bank tpye is: " << evt->feb_info[4] << std::endl;
		contact_thread << " The bank length is:                " << evt->feb_info[5] << std::endl;
#endif
#if DEBUG_ME
		std::cout << "Entering acquire_data::ContactEventBuilder..." << std::endl;
		std::cout << " In Event Builder the bank type is: " << evt->feb_info[4] << std::endl;
		std::cout << " The bank length is:                " << evt->feb_info[5] << std::endl;
#endif
	}

	// Now for the data buffer.
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
			break;
		case 4:
			std::cout << "TriP-T Programming Frames not supported for writing to disk!" << std::endl;
			exit(-100);
		default:
			std::cout << "Invalid Frame Type in acquire_data::ContactEventBuilder!" << std::endl;
			exit(-100);
	}
#if REPORT_EVENT
	std::cout << "************************************************************************" << std::endl;
	std::cout << "  Sending Data to ET System:" << std::endl;
#endif
	// Send event to ET for storage.
	while (et_alive(sys_id)) {
#if DEBUG_ME
		std::cout << "->ET is Alive!" << std::endl;
#endif
		et_event *pe; // The event.
		event_handler *pdata; // The data for the event.
#if THREAD_ME
		lock eb_lock(eb_mutex);
#endif
		int status = et_event_new(sys_id, attach, &pe, ET_SLEEP, NULL, 
			sizeof(struct event_handler)); // Get an event.
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
		// Put data into the event.
		if (status == ET_OK) {
#if REPORT_EVENT
			std::cout << "******************************************************************" << std::endl;
			std::cout << "    Putting Event on ET System:" << std::endl;
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
				case 4:
					std::cout << "TriP-T Programming Frames not supported for writing to disk!" << std::endl;
					exit(-100);
				default:
					std::cout << "Invalid Frame Type in acquire_data::ContactEventBuilder!" << std::endl;
					exit(-100);
			}
#if THREAD_ME
			eb_lock.lock();
#endif
			et_event_getdata(pe, (void **)&pdata); // Get the event ready.
#if DEBUG_ME
			std::cout << " event_handler_size: " << sizeof(struct event_handler) << std::endl;
			std::cout << " evt_size:           " << sizeof(evt) << std::endl;
#endif
#if REPORT_EVENT
			{ // Report_event print statements...
				std::cout << "*******************************************************************" << std::endl; 
				std::cout << "Finished Processing Event Data:" << std::endl;
				std::cout << " GATE---------: " << evt->gate_info[1] << std::endl;
				std::cout << " CROC---------: " << evt->feb_info[2] << std::endl;
				std::cout << " CHANNEL------: " << evt->feb_info[3] << std::endl;
				std::cout << " BANK---------: " << evt->feb_info[4] << std::endl;
				std::cout << " DETECT-------: " << evt->run_info[0] << std::endl; 
				std::cout << " CONFIG-------: " << evt->run_info[1] << std::endl; 
				std::cout << " RUN----------: " << evt->run_info[2] << std::endl;
				std::cout << " SUB-RUN------: " << evt->run_info[3] << std::endl;
				std::cout << " TRIGGER------: " << evt->run_info[4] << std::endl;
				std::cout << " GLOBAL GATE--: " << evt->gate_info[0] << std::endl;
				std::cout << " TRIG TIME----: " << evt->gate_info[2] << std::endl;
				std::cout << " ERROR--------: " << evt->gate_info[3] << std::endl;
				std::cout << " MINOS--------: " << evt->gate_info[4] << std::endl;
				std::cout << " BUFFER_LENGTH: " << evt->feb_info[5] << std::endl;
				std::cout << " FIRMWARE-----: " << evt->feb_info[7] << std::endl;
				std::cout << " FRAME DATA---: " << std::endl;
				// Print Bank Header? No...
				// printf("     Bytes: 3 2 1 0 = (0x) %02X %02X %02X %02X\n",
				// 	(unsigned int)evt->event_data[3], (unsigned int)evt->event_data[2],
				// 	(unsigned int)evt->event_data[1], (unsigned int)evt->event_data[0]
				// 	); 					
				// printf("     Bytes: 7 6 5 4 = (0x) %02X %02X %02X %02X\n",
				// 	(unsigned int)evt->event_data[7], (unsigned int)evt->event_data[6],
				// 	(unsigned int)evt->event_data[5], (unsigned int)evt->event_data[4]
				// 	); 					
				for (int index = 0; index < length; index++) {
					printf("     Data Byte %02d = 0x%02X\n",index,(unsigned int)evt->event_data[index]); 
				}
			}
#endif
			memcpy (pdata, evt, sizeof(struct event_handler));
			et_event_setlength(pe,sizeof(struct event_handler));
#if THREAD_ME
			eb_lock.unlock();
#endif  
		} // end if status == ET_OK
		// Put the event back into the ET system.
#if THREAD_ME
		eb_lock.lock();
#endif
		status = et_event_put(sys_id, attach, pe); // Put the event away.
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
		break; // Done processing the event. 
	} // while alive 
#if DEBUG_ME
		std::cout << "Exiting acquire_data::ContactEventBuilder..." << std::endl;
#endif

}


template <class X> void acquire_data::FillEventStructure(event_handler *evt, int bank, X *frame, 
	channels *channelTrial) 
{
/*! \fn template <class X> void acquire_data::FillEventStructure(event_handler *evt, int bank, X *frame, 
 * channels *channelTrial)
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
	std::cout << "  Entering acquire_data::FillEventStructure with bank type " << bank << " and message length " << frame->GetIncomingMessageLength() << std::endl;
#endif
	// Build sourceID
	evt->feb_info[1] = daqController->GetID(); // Crate ID
	evt->feb_info[4] = bank;                   // 0==ADC, 1==TDC, 2==FPGA, 3==DAQ Header, 4==TriP-T
	evt->feb_info[5] = frame->GetIncomingMessageLength();           // Buffer length
	unsigned char tmp_buffer[(const unsigned int)evt->feb_info[5]]; // Set the buffer size.
#if DEBUG_ME
	std::cout << "   Getting Data..." << std::endl;
	for (int i = 0; i < 9; i++) {
		std::cout << "     evt->feb_info[" << i << "] = " <<  
			(unsigned int)evt->feb_info[i] << std::endl;
	}
#endif
	for (unsigned int index = 0; index < (evt->feb_info[5]); index++) {
		tmp_buffer[index] = channelTrial->GetBuffer()[index];
	}
	for (unsigned int i = 0; i < evt->feb_info[5]; i++) {
		evt->event_data[i] = tmp_buffer[i]; // Load the event data.
	}
#if DEBUG_ME
	std::cout << "   Got Data" << std::endl;
	std::cout << "    IncomingMessageLength: " << frame->GetIncomingMessageLength() << std::endl;
	for (int index = 0; index < (frame->GetIncomingMessageLength()); index++) {
		printf("     FillStructure data byte %02d = 0x%02X\n", index, 
			(unsigned int)evt->event_data[index]); 
	}
#endif
}

#endif
