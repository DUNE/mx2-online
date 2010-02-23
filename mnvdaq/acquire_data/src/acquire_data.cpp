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

const int acquire_data::dpmMax       = 1024*6; //we have only 6 Kb of space in the DPM Memory per channel
const int acquire_data::numberOfHits = 6;

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
 */
#if TIME_ME
	struct timeval start_time, stop_time;
	gettimeofday(&start_time, NULL);
#endif
	std::cout << "\nEntering acquire_data::InitializeDaq()." << std::endl;
	acqData.infoStream() << "Entering acquire_data::InitializeDaq().";

	// Get the VME read/write access functions.
	daqAcquire = new acquire(); 

	// We need a controller to control the VME bus.
	daqController = new controller(0x00, id, acqAppender); 
	try {
		int error = daqController->ContactController();
		if (error) throw error;
	} catch (int e) {
		std::cout << "acquire_data::InitializeDaq(): Error contacting the VME controller!" << std::endl;
		acqData.fatalStream() << "acquire_data::InitializeDaq(): Error contacting the VME controller!";
		exit(e);
	} 

	// TODO - Add VME card lookup by file here...

	// Then we need the cards which can read the data - hardcoded for now....
#if THREAD_ME
	boost::thread crim_thread(boost::bind(&acquire_data::InitializeCrim, this, 0xE00000, 1, runningMode)); 
	boost::thread croc_thread(boost::bind(&acquire_data::InitializeCroc, this, 0x010000, 1)); 
	crim_thread.join(); // Wait for the crim thread to return.
	croc_thread.join(); // Wait for the croc thread to return.
#endif

	// Add look-up functions here - one for file content look-up and one by address scanning 
#if NO_THREAD
#if PMTTEST
	InitializeCrim(0xE00000, 1, runningMode);
	InitializeCroc(0x030000, 1, 4, 0, 0, 0);
#endif
#if WH14
	InitializeCrim(0xE00000, 1, runningMode);
	//InitializeCrim(0xF00000, 2, runningMode);
	InitializeCroc(0x010000, 1, 4, 4, 0, 0);
	//InitializeCroc(0x020000, 2, 4, 5, 6, 7);
#endif
#if NUMIUS
	InitializeCrim(0xE00000, 1, runningMode);
	//InitializeCrim(0xF00000, 2, runningMode);
	//InitializeCroc(0x010000, 1,  0,  0,  0,  0); // MS01W, MS02W, MS03W, MS04W
	//InitializeCroc(0x020000, 2,  0,  0,  0,  0); // MS01E, MS02E, MS03E, MS04E
	InitializeCroc(0x030000, 1, 10, 10, 10, 10); // MS05W, MS06W, MS07W, MS08W
	InitializeCroc(0x040000, 2,  9,  9,  9,  9); // MS05E, MS06E, MS07E, MS08E
	InitializeCroc(0x050000, 3, 10, 10, 10,  0); // MS09W, MS10W, MS11W, Loopback
	InitializeCroc(0x060000, 4,  9,  9,  9,  0); // MS09E, MS10E, MS11E, Loopback
#endif
#endif

	// Set the flags that tells us how many VME cards are installed for this controller.
	daqController->SetCrocVectorLength(); 
	daqController->SetCrimVectorLength();
	acqData.infoStream() << " Total Number of Initialized CRIMs attached to this controller = " << 
		daqController->GetCrimVectorLength(); 
	acqData.infoStream() << " Total Number of Initialized CROCs attached to this controller = " << 
		daqController->GetCrocVectorLength(); 
	acqData.infoStream() << " Master CRIM address = " <<
			(daqController->GetCrim()->GetCrimAddress()>>16);

	// Enable the CAEN IRQ handler.
	// Only the MASTER (first) CRIM should be the interrupt handler!
	try {
		unsigned short bitmask = daqController->GetCrim()->GetInterruptMask();
		acqData.info("Enabling the IRQ Handler on CRIM %d with bimask 0x%04X",
			(daqController->GetCrim()->GetCrimAddress()>>16),bitmask);
		int error = CAENVME_IRQEnable(daqController->handle,~bitmask);
		acqData.infoStream() << " Returned from IRQEnable for CRIM " << 
			(daqController->GetCrim()->GetCrimAddress()>>16);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::InitializeDaq() enabling CAEN VME IRQ handler!" << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Error in acquire_data::InitializeDaq() enabling CAEN VME IRQ handler!";
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
	std::cout << "Finished Initialization!  Exiting acquire_data::InitializeDaq().\n" << std::endl;
	acqData.infoStream() << "Finished Initialization!  Exiting acquire_data::InitializeDaq().";
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
// TODO - Make InitializeCrim return a value!
// TODO - Really, InitializeCrim should take a flag to allow it to just instantiate the software 
// objects without touching the actual hardware registers - we would like any actual configuration 
// done with the SlowControl.  The one exception to this philosophy might be interrupt configuration 
// (certainly interrupt resets must be handled by the DAQ).
	std::cout << "\nEntering acquire_data::InitializeCrim for address " << (address>>16) << std::endl;
	acqData.infoStream() << "Entering acquire_data::InitializeCrim for address " << (address>>16);
#if DEBUG_THREAD
	std::ofstream crim_thread;
	std::stringstream thread_number;
	thread_number<<address;
	std::string filename;
	filename = "crim_thread_"+thread_number.str();
	crim_thread.open(filename.c_str());
	crim_thread << "Initializing CRIM, Start" << std::endl;
#endif

	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth       DW = daqController->GetDataWidth();

	// Make a CRIM object on this controller.
	daqController->MakeCrim(address, index); 

	// Make sure that we can actually talk to the card.
	try {
		int status = daqController->GetCrimStatus(index); 
		if (status) throw status;
	} catch (int e)  {
		std::cout << "Unable to read the status register for CRIM with Address " << 
			((daqController->GetCrim(index)->GetCrimAddress())>>16) << std::endl;
		acqData.fatalStream() << "Unable to read the status register for CRIM with Address " << 
			((daqController->GetCrim(index)->GetCrimAddress())>>16);
		exit(-3);
	} 

	// Note IRQLine is set in the CRIM constructor.  The default is SGATEFall, 
        // which is the correct choice for every running mode but Cosmics.
	unsigned short GateWidth    = 0x1;       // GetWidth must never be zero!
	unsigned short TCALBDelay   = 0x1;       // Delay should also be non-zero.
	unsigned short TCALBEnable  = 0x1;       // Enable pulse delay.
	crimTimingFrequencies Frequency  = ZeroFreq; // Used to set ONE frequency bit!  ZeroFreq ~no Frequency.
	crimTimingModes       TimingMode = MTM;      // Default to MTM.

	// Check running mode and perform appropriate initialization.  We are needlessly 
        // repetitious with setting the gate width and tcalb delay (0x7F & 0x3FF will probably 
        // always be fine for any running mode), but this is to "build in" some flexibility 
        // if we decide we need it (as a reminder).  
	switch (runningMode) {
		// "OneShot" is the casual name for CRIM internal timing with software gates.
		case OneShot:
			std::cout << " Running Mode is OneShot." << std::endl;
			acqData.infoStream() << " Running Mode is OneShot.";
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = ZeroFreq;
			TimingMode   = crimInternal; 
			TCALBEnable  = 0x1;
			break;
		// All of the NuMI and dedicated LI modes use MTM timing.
		case NuMIBeam:
			std::cout << " Running Mode is NuMI Beam." << std::endl;
			acqData.infoStream() << " Running Mode is NuMI Beam.";
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = ZeroFreq;
			TimingMode   = MTM; 
			TCALBEnable  = 0x1;
			break;
		case PureLightInjection:
			std::cout << " Running Mode is PureLightInjection." << std::endl;
			acqData.infoStream() << " Running Mode is PureLightInjection.";
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = ZeroFreq;
			TimingMode   = MTM; 
			TCALBEnable  = 0x1;
			break;
		case MixedBeamPedestal:
			std::cout << " Running Mode is MixedBeamPedestal." << std::endl;
			acqData.infoStream() << " Running Mode is MixedBeamPedestal.";
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = ZeroFreq;
			TimingMode   = MTM; 
			TCALBEnable  = 0x1;
			break;
		case MixedBeamLightInjection:
			std::cout << " Running Mode is MixedBeamLightInjection." << std::endl;
			acqData.infoStream() << " Running Mode is MixedBeamLightInjection.";
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = ZeroFreq;
			TimingMode   = MTM; 
			TCALBEnable  = 0x1;
			break;
		// Cosmics use CRIM internal timing with gates send at a set frequency.
		case Cosmics:
			std::cout << " Running Mode is Cosmic." << std::endl;
			acqData.infoStream() << " Running Mode is Cosmic.";
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = F4; // The fastest setting is a function of FEB firmware.
			TimingMode   = crimInternal; 
			TCALBEnable  = 0x1;
			daqController->GetCrim(index)->SetIRQLine((crimInterrupts)0x01); // Trigger
			break;
		default:
			std::cout << "Error in acquire_data::InitializeCrim()! No Running Mode defined!" << std::endl;
			acqData.fatalStream() << "Error in acquire_data::InitializeCrim()! No Running Mode defined!";
			exit(-4);
	}

	// Build Register Settings (this does not write to hardware, it only configures software objects).
	daqController->GetCrim(index)->SetupTiming(TimingMode, Frequency);
	daqController->GetCrim(index)->SetupGateWidth(TCALBEnable, GateWidth);
	daqController->GetCrim(index)->SetupTCALBPulse(TCALBDelay);
	acqData.info("  CRIM Timing Setup    = 0x%04X", daqController->GetCrim(index)->GetTimingSetup());
	acqData.info("  CRIM GateWidth Setup = 0x%04X", daqController->GetCrim(index)->GetGateWidthSetup());
	acqData.info("  CRIM TCALB Setup     = 0x%04X", daqController->GetCrim(index)->GetTCALBPulse());

	// Now write settings to hardware.
	// TODO - This part should be something we can do or not do according to a flag...
	unsigned char crim_message[2];
	// Set GateWidth.
	try {
		crim_message[0] = daqController->GetCrim(index)->GetGateWidthSetup() & 0xFF;
		crim_message[1] = (daqController->GetCrim(index)->GetGateWidthSetup()>>8) & 0xFF;
		int error = daqAcquire->WriteCycle(daqController->handle, 2, crim_message,
			daqController->GetCrim(index)->GetSGATEWidthRegister(), AM, DW); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::InitializeCrim!  Cannot write to the Gate Width register!" << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Error in acquire_data::InitializeCrim!  Cannot write to the Gate Width register!";
		exit (e);
	}
	// Setup TCALB Delay.
	try {
		crim_message[0] = daqController->GetCrim(index)->GetTCALBPulse() & 0xFF;
		crim_message[1] = (daqController->GetCrim(index)->GetTCALBPulse()>>8) & 0xFF;
		int error = daqAcquire->WriteCycle(daqController->handle, 2, crim_message,
			daqController->GetCrim(index)->GetTCALBRegister(), AM, DW); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::InitializeCrim!  Cannot write to the TCALB register!" << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Error in acquire_data::InitializeCrim!  Cannot write to the TCALB register!";
		exit (e);
	}
	// Setup Timing register.
	try {
		crim_message[0] = daqController->GetCrim(index)->GetTimingSetup() & 0xFF;
		crim_message[1] = (daqController->GetCrim(index)->GetTimingSetup()>>8) & 0xFF;
		int error = daqAcquire->WriteCycle(daqController->handle, 2, crim_message,
			daqController->GetCrim(index)->GetTimingRegister(), AM, DW); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::InitializeCrim!  Cannot write to the Timing Setup register!" << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Error in acquire_data::InitializeCrim!  Cannot write to the Timing Setup register!";
		exit (e);
	}

	// Now set up the IRQ handler, initializing the global enable bit for the first go-around.
	// TODO - Be sure only the Master CRIM is our interrupt handler...
	try {
		int error = SetupIRQ(index);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::InitializeCrim for CRIM with address = " << (address>>16) << std::endl;
		std::cout << "Cannot SetupIRQ!" << std::endl;
		acqData.fatalStream() << "Error in acquire_data::InitializeCrim for CRIM with address = " << (address>>16);
		acqData.fatalStream() << "Cannot SetupIRQ!";
		exit (e);
	}
#if DEBUG_THREAD
	crim_thread << "In InitializeCrim, finished initializing CRIM " << (address>>16) << std::endl;
	crim_thread.close();
#endif
	std::cout << "Finished initializing CRIM " << (address>>16) << std::endl;
	acqData.infoStream() << "Finished initializing CRIM " << (address>>16);
}


void acquire_data::InitializeCroc(int address, int crocNo, int nFEBchain0, int nFEBchain1, int nFEBchain2, int nFEBchain3) 
{
/*! \fn void acquire_data::InitializeCroc(int address, int crocNo, int crocNo, int nFEBchain0, int nFEBchain1, int nFEBchain2, int nFEBchain3)
 *
 * This function checks the CROC addressed by "address"
 * is available by reading the status register.  
 *
 * The CROC is then assigned the id crocNo.
 *
 * Then the FEB list for each channel on this croc is built.  We use this sort of wonky-looking 
 * set of arguments for the number of FEB's on each chain for formatting convenience.  
 *
 * \param address an integer VME addres for the CROC
 * \param crocNo an integer given this CROC for ID
 * \param nFEBchain0 an integer describing the number of FEB's on chain 0.  Defaults to 11.
 * \param nFEBchain1 an integer describing the number of FEB's on chain 1.  Defaults to 11.
 * \param nFEBchain2 an integer describing the number of FEB's on chain 2.  Defaults to 11.
 * \param nFEBchain3 an integer describing the number of FEB's on chain 3.  Defaults to 11.
 */
	std::cout << "\nEntering acquire_data::InitializeCroc for CROC " << (address>>16) << std::endl;
	acqData.infoStream() << "Entering acquire_data::InitializeCroc for CROC " << (address>>16);
#if DEBUG_THREAD
	std::ofstream croc_thread;
	std::stringstream thread_number;
	thread_number << address;
	std::string filename;
	filename = "croc_thread_"+thread_number.str();
	croc_thread.open(filename.c_str());
	croc_thread << "In InitializeCrroc, Starting" << std::endl;
#endif
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth       DW = daqController->GetDataWidth();

	// Make a CROC object on this controller.
	daqController->MakeCroc(address,crocNo); 
	int nChannels = 4; // # of CROC FE Channels - always fixed for the real detector...
	int nFEBsPerChain[] = { nFEBchain0, nFEBchain1, nFEBchain2, nFEBchain3 };

	// Make sure that we can actually talk to the cards.
	try {
		int status = daqController->GetCardStatus(crocNo);  
		if (status) throw status;
	} catch (int e)  {
		std::cout << "Error in acquire_data::InitializeCroc!  Cannot read the status register for CROC " <<
			(address>>16) << std::endl;
		acqData.fatalStream() << "Error in acquire_data::InitializeCroc!  Cannot read the status register for CROC " <<
			(address>>16);
		exit(-2);
	}

	// Set the timing mode to EXTERNAL: clock mode, test pulse enable, test pulse delay
	// Clock Mode set to External in CROC constructor.  TODO - Make these actions controlle by a flag.
	unsigned char croc_message[2];
	croc_message[0] = (unsigned char)(daqController->GetCroc(crocNo)->GetTimingRegister() & 0xFF);
	croc_message[1] = (unsigned char)( (daqController->GetCroc(crocNo)->GetTimingRegister()>>8) & 0xFF);
	acqData.info("  Timing Register Address  = 0x%X",daqController->GetCroc(crocNo)->GetTimingAddress());
	acqData.info("  Timing Register Message  = 0x%X",daqController->GetCroc(crocNo)->GetTimingRegister());
	acqData.info("  Timing Message (Sending) = 0x%02X%02X",croc_message[1],croc_message[0]);
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, 2, croc_message, 
			daqController->GetCroc(crocNo)->GetTimingAddress(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Unable to set the CROC timing mode!" << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Unable to set the CROC timing mode!";
		exit (e);
	}

	// Now make threads which will search all channels on the croc to 
	// find which ones have FEB's on them.  Then set up the FEB's. 
#if THREAD_ME
	boost::thread *chan_thread[4];
#endif

	// Build the FEB list for each channel.
	acqData.infoStream() << " Building FEB List:";
	for (int i = 0; i < nChannels; i++) {
		// Now set up the channels and FEB's.
		croc *tmpCroc = daqController->GetCroc(crocNo);
		bool avail = false;
		avail = tmpCroc->GetChannelAvailable(i);
		if (avail) {
#if THREAD_ME
#if DEBUG_THREAD
			croc_thread<<"Launching build FEB list thread "<<i<<std::endl;
#endif
			chan_thread[i] = new boost::thread(boost::bind(&acquire_data::BuildFEBList,this,i,crocNo,nFEBsPerChain[i]));
#else
			BuildFEBList(i, crocNo, nFEBsPerChain[i]);
#endif
		}
	}

#if THREAD_ME
	// If we are working in multi-threaded operation we need  
	// to wait for the each thread we launched to complete.
	for (int i = 0; i < nChannels; i++) {
		chan_thread[i]->join(); // Wait for all the threads to finish up before moving on.
#if DEBUG_THREAD
		croc_thread << "Build FEB List: chain " << i << " thread completed." << std::endl;
#endif
		croc_thread.close();
		delete chan_thread[i];
	}  
#endif
	std::cout << "Finished initialization for CROC " << 
		(daqController->GetCroc(crocNo)->GetCrocAddress()>>16) << std::endl;
	acqData.infoStream() << "Finished initialization for CROC " << 
		(daqController->GetCroc(crocNo)->GetCrocAddress()>>16);
}


int acquire_data::SetupIRQ(int index) 
{
/*!\fn int acquire_data::SetupIRQ(int index)
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
 *
 * \param index The CRIM index value in the interface module vector.
 */
#if DEBUG_IRQ
	acqData.debugStream() << "   Entering acquire_data::SetupIRQ for CRIM " << 
		(daqController->GetCrim(index)->GetCrimAddress()>>16) << " and index " << index;
	acqData.debugStream() << "    IRQ Line      = " << (int)daqController->GetCrim(index)->GetIRQLine();
#endif
	int error = 0; 

	// Set up the crim interrupt mask.  Note that we assume the irqLine was set during CRIM initialization.
	daqController->GetCrim(index)->SetInterruptMask(); 
#if DEBUG_IRQ
	acqData.debugStream() << "    InterruptMask = " << daqController->GetCrim(index)->GetInterruptMask();
#endif
	unsigned char crim_send[2] = {0,0};
	crim_send[0] = (daqController->GetCrim(index)->GetInterruptMask()) & 0xff;
	crim_send[1] = ((daqController->GetCrim(index)->GetInterruptMask())>>0x08) & 0xff;
#if DEBUG_IRQ
	acqData.debug("     Setting the interrupt mask with message: 0x%02X%02X", 
		crim_send[1],crim_send[0]);
#endif
	try {
		error = daqAcquire->WriteCycle( daqController->handle, 2, crim_send,
			daqController->GetCrim(index)->GetInterruptMaskAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth() );
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error setting crim IRQ mask in acquire_data::SetupIRQ for CRIM " 
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16) << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error setting crim IRQ mask in acquire_data::SetupIRQ for CRIM"
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16);
		return e;
	}

	// Check the interrupt status.
	try {
		crim_send[0] = 0; crim_send[1] = 0; 
		error = daqAcquire->ReadCycle( daqController->handle, crim_send,
			daqController->GetCrim(index)->GetInterruptStatusAddress(), daqController->GetAddressModifier(),
			daqController->GetDataWidth() ); 
		if (error) throw error;

		// Clear any pending interrupts.
		unsigned short interrupt_status = 0;
		interrupt_status = (unsigned short) (crim_send[0]|(crim_send[1]<<0x08));
#if DEBUG_IRQ
		acqData.debugStream() << "     Current interrupt status = " << interrupt_status;
#endif
		if (interrupt_status!=0) { 
			// Clear the pending interrupts.
			crim_send[0] = daqController->GetCrim(index)->GetClearInterrupts() & 0xff;
			crim_send[1] = (daqController->GetCrim(index)->GetClearInterrupts()>>0x08) & 0xff;
#if DEBUG_IRQ
			acqData.debug("     Clearing pending interrupts with message: 0x%02X%02X",
				crim_send[1], crim_send[0]);
#endif
			try {
				error = daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
					daqController->GetCrim(index)->GetClearInterruptsAddress(), 
					daqController->GetAddressModifier(),
					daqController->GetDataWidth() ); 
				if (error) throw error;
			} catch (int e) {
				std::cout << "Error clearing crim interrupts in acquire_data::SetupIRQ for CRIM " 
					<< (daqController->GetCrim(index)->GetCrimAddress()>>16) << std::endl;
				daqController->ReportError(e);
				acqData.critStream() << "Error clearing crim interrupts in acquire_data::SetupIRQ for CRIM "
					<< (daqController->GetCrim(index)->GetCrimAddress()>>16);
				return e;
			}
		}
	} catch (int e) {
		std::cout << "Error getting crim interrupt status in acquire_data::SetupIRQ for CRIM " 
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16) << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error getting crim interrupt status in acquire_data::SetupIRQ for CRIM "
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16);
		return e;
	}

	// Now set the IRQ LEVEL.
	try {
		error = ResetGlobalIRQEnable(index);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Failed to ResetGlobalIRQ for CRIM " 
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16) << ".  Status code = " << e << std::endl;
		acqData.critStream() << "Failed to ResetGlobalIRQ for CRIM "
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16) << ".  Status code = " << e;
		return e;
	}
	crim_send[0] = (daqController->GetCrim(index)->GetInterruptConfig()) & 0xff;
	crim_send[1] = ((daqController->GetCrim(index)->GetInterruptConfig())>>0x08) & 0xff;
#if DEBUG_IRQ
	acqData.debug("     IRQ CONFIG = 0x%04X\n",daqController->GetCrim(index)->GetInterruptConfig());
	acqData.debug("     IRQ ADDR   = 0x%04X\n",daqController->GetCrim(index)->GetInterruptsConfigAddress());
#endif
	try {
		error = daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
			daqController->GetCrim(index)->GetInterruptsConfigAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth() ); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error setting crim IRQ mask in acquire_data::SetupIRQ for CRIM " 
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16) << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error setting crim IRQ mask in acquire_data::SetupIRQ for CRIM "
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16);
		return e;
	}

	// Now enable the line on the CAEN controller.
#if DEBUG_IRQ
	acqData.debug("     IRQ LINE   = 0x%02X",daqController->GetCrim(index)->GetIRQLine());
	acqData.debug("     IRQ MASK   = 0x%04X",daqController->GetCrim(index)->GetInterruptMask());
#endif
	try {
		error = CAENVME_IRQEnable(daqController->handle,~daqController->GetCrim(index)->GetInterruptMask());
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::SetupIRQ!  Cannot execut IRQEnable for CRIM " 
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16) << std::endl;
                daqController->ReportError(e);
		acqData.critStream() << "Error in acquire_data::SetupIRQ!  Cannot execut IRQEnable for CRIM "
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16);
                return e;
	}
#if DEBUG_IRQ
	acqData.debugStream() << "   Exiting acquire_data::SetupIRQ().";
#endif 
	return 0;
}


int acquire_data::ResetGlobalIRQEnable(int index) 
{
/*!  \fn int acquire_data::ResetGlobalIRQEnable(int index)
 *
 * Sets the global enable bit on the CRIM interrupt handler for the CRIM with index value 
 * index in the interface module vector associated with the controller.
 *
 * Returns a status value.
 * \param index The index value of the CRIM in question in the interface module vector.
 */
#if DEBUG_IRQ
	acqData.debugStream() << "      Entering ResetGlobalIRQEnable for CRIM " << 
		(daqController->GetCrim(index)->GetCrimAddress()>>16) << " and index " << index; 
#endif	
	// Set the global enable bit.
	daqController->GetCrim(index)->SetInterruptGlobalEnable(true);
	
	unsigned char crim_send[2];
	crim_send[0] = ((daqController->GetCrim(index)->GetInterruptConfig()) & 0xff);
	crim_send[1] = (((daqController->GetCrim(index)->GetInterruptConfig())>>0x08) & 0xff);
#if DEBUG_IRQ
	acqData.debug("       Resetting Global IRQ Enable with message 0x%02X%02X",crim_send[1],crim_send[0]);
#endif
	try { 
		int error = daqAcquire->WriteCycle( daqController->handle, 2, crim_send,
			daqController->GetCrim(index)->GetInterruptsConfigAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth() );
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error setting IRQ Global Enable Bit for CRIM "
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16) << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error setting IRQ Global Enable Bit for CRIM "
			<< (daqController->GetCrim(index)->GetCrimAddress()>>16);
		return e;
	}
#if DEBUG_IRQ
	acqData.debugStream() << "Exiting acquire_data::ResetGlobalIRQEnable().";
#endif
	return 0;
}


int acquire_data::BuildFEBList(int i, int croc_id, int nFEBs) 
{
/*! \fn
 * int acquire_data::BuildFEBList(int i, int croc_id, int nFEBs)
 *
 *  Builds up the FEB list on each CROC channel.
 *
 *  Finds FEB's by sending a message to each 1 through nFEBs potential FEB's
 *  per channel.  Those channels which respond with "message received"
 *  for that FEB have and FEB of the corresponding number loaded into an 
 *  STL list containing objects of type feb.
 *
 *  \param i an integer for the *chain* number corresponding to a channel.
 *  \param croc_id an integer the ID number for the CROC
 *  \param nFEBs an integer for the number of FEB's to search through on the chain.
 *
 *  Returns a status value (0 for success).
 */
	acqData.infoStream() << "Entering BuildFEBList for CROC " << 
		(daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " << i;
	acqData.infoStream() << " Looking for " << nFEBs << " FEBs.";
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
	// Addresses numbers range from 1 to Max and we'll loop
	// over all of them and look for S2M message headers.
	for (int j = 1; j <= nFEBs; j++) { 
#if DEBUG_THREAD
		build_feb_thread << " Making FEB: " << j << std::endl;
#endif
		acqData.infoStream() << "    Trying to make FEB " << j << " on chain " << i;
		// Make a "trial" FEB for the current address.
		feb *tmpFEB = tmpChan->MakeTrialFEB(j, numberOfHits, acqAppender); 
#if DEBUG_THREAD
		build_feb_thread << "  Made FEB " << j << " on chain " << i << std::endl;
#endif
		
		// Build an outgoing message to test if an FEB of this address is available on this channel.
		tmpFEB->MakeMessage(); 
#if DEBUG_THREAD
		build_feb_thread << "  Made Message & Sending on chain: " << i << std::endl;
#endif

		// Send the message & delete the outgoingMessage.
		int success = SendMessage(tmpFEB, tmpCroc, tmpChan, true); 
		tmpFEB->DeleteOutgoingMessage();

		// Read the DPM & delete the message shell.
		success = ReceiveMessage(tmpFEB, tmpCroc, tmpChan);
		delete [] tmpFEB->message;

		// If the FEB is available, load it into the channel's FEB list and initialize the TriPs. 
		if (!success) {
			acqData.infoStream() << "FEB: " << tmpFEB->GetBoardNumber() << " is available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " 
				<< tmpChan->GetChainNumber() << " with init. level " << tmpFEB->GetInit();
#if DEBUG_THREAD
			build_feb_thread << "FEB: " << tmpFEB->GetBoardNumber() << " is available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " 
				<< tmpChan->GetChainNumber() << " with init. level" << tmpFEB->GetInit() << std::endl;
#endif
			// Add the FEB to the list.
			tmpChan->SetFEBs(j, numberOfHits, acqAppender); 

			// Set the FEB available flag.
			tmpChan->SetHasFebs(true);

			// Clean up the memory.
			delete tmpFEB;  
		} else {
		// TODO - Return an error code in this case?
			acqData.critStream() << "FEB: " << tmpFEB->GetBoardNumber() << " is NOT available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " 
				<< tmpChan->GetChainNumber();
			std::cout << "\nCRITICAL!  FEB: " << tmpFEB->GetBoardNumber() << " is NOT available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " 
				<< tmpChan->GetChainNumber() << "\n" << std::endl;
#if DEBUG_THREAD
			build_feb_thread << "FEB: " << tmpFEB->GetBoardNumber() << " is not available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " 
				<< tmpChan->GetChainNumber() << std::endl;
#endif
			// Clean up the memory.
			delete tmpFEB; 
		}  
	}

	acqData.infoStream() << "Returning from BuildFEBList.";
#if DEBUG_THREAD
	build_feb_thread << "Returning from BuildFEBList." << std::endl;
	build_feb_thread.close();
#endif
	return 0;
}


int acquire_data::WriteCROCFastCommand(int id, unsigned char command[])
{
#if DEBUG_FASTCOMMAND
	acqData.debugStream() << "Entering WriteCROCFastCommand for CROC " <<
		(daqController->GetCroc(id)->GetCrocAddress()>>16) << 
		" and " << sizeof(*command)/sizeof(unsigned char) << " command(s): "; 
	for (int i = 0; i<(sizeof(*command)/sizeof(unsigned char)); i++) { 
		acqData.debug("   0x%02X",command[i]);
	}
#endif
	int ml = sizeof(*command)/sizeof(unsigned char);
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, ml, command, 
			daqController->GetCroc(id)->GetFastCommandAddress(), 
			daqController->GetAddressModifier(), daqController->GetDataWidth()); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::WriteCROCFastCommand for CROC " <<
			(daqController->GetCroc(id)->GetCrocAddress()>>16) << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in acquire_data::WriteCROCFastCommand for CROC " <<
			(daqController->GetCroc(id)->GetCrocAddress()>>16);
		return e;
	}
	return 0;
}


// TODO - GetBlockRAM has sort of a misleading name, should fix this (should be GetDPMData or something).
int acquire_data::GetBlockRAM(croc *crocTrial, channels *channelTrial) 
{
/*! \fn int acquire_data::GetBlockRAM(croc *crocTrial, channels *channelTrial)
 * \param *crocTrial a pointer to a croc object
 * \param *channelTrial a pointer to a channel object
 *
 * This function retrieves any data in a CROC channel's DPM and puts it into the buffer
 * DPMBuffer. This buffer is then assinged to a channel buffer for later use.
 *
 * Returns a status integer (0 for success).
 */
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
		std::cout << " Error reading DPM pointer in acquire_data::GetBlockRAM for CROC " 
			<< (crocTrial->GetCrocAddress()>>16) << " Chain " << 
			(channelTrial->GetChainNumber()) << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error reading DPM pointer in acquire_data::GetBlockRAM for CROC "
			<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
			(channelTrial->GetChainNumber());
		return (-e);
	} 
	dpmPointer = (int) (status[0] | status[1]<<0x08);
	if (dpmPointer%2) { // Must read an even number of bytes.
		DPMData = new unsigned char [dpmPointer+1];
	} else {
		DPMData = new unsigned char [dpmPointer];
	}
	// Read the DPM.
	try {
		int success = daqAcquire->ReadBLT(daqController->handle, DPMData, dpmPointer, 
			channelTrial->GetDPMAddress(), AM_BLT, DWS);
		if (success) throw success;
	} catch (int e) {
		std::cout << "Error in acquire_data::GetBlockRAM!  Cannot read the DPM for CROC " << 
			(crocTrial->GetAddress()>>16) << " Chain " << channelTrial->GetChainNumber() << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in acquire_data::GetBlockRAM!  Cannot read the DPM for CROC " << 
			(crocTrial->GetAddress()>>16) << " Chain " << channelTrial->GetChainNumber();
		return (-e);
	}

	channelTrial->SetDPMPointer(dpmPointer);
	channelTrial->SetBuffer(DPMData);

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
 *  \param int incoming_length an integer value for the maximum incoming message length
 *
 *  Returns a status bit (true for success).
 */
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth DWS      = crocTrial->GetDataWidthSwapped();
	unsigned short dpmPointer;
	unsigned char status[2];
	int success;

	try {
		int error = daqAcquire->ReadCycle(daqController->handle, status, 
			channelTrial->GetDPMPointerAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Unable to read DPM Pointer in acquire_data::FillDPM for CROC " 
			<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
			(channelTrial->GetChainNumber()) << std::cout;
		daqController->ReportError(e);
		acqData.critStream() << "Unable to read DPM Pointer in acquire_data::FillDPM for CROC "
			<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
			(channelTrial->GetChainNumber());
		return false;
	}
	dpmPointer = (unsigned short) (status[0] | (status[1]<<0x08));

	// We have to check and see if the message could exceed the amount of space available 
	// in memory.  If it doesn't, it is safe to write the send-message command and add 
	// a new frame to the DPM.
	if ( (dpmPointer<dpmMax) && ((dpmMax-incoming_length)>incoming_length) ) {
		try {
			success = SendMessage(frame, crocTrial, channelTrial, true);
			if (success) throw success;
		} catch (int e) {
			std::cout << "      Error in acquire_data::FillDPM for CROC " 
				<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
				(channelTrial->GetChainNumber()) << std::endl;
			std::cout << "      SendMessage Error Level = " << success << std::endl;
			acqData.critStream() << "Error in acquire_data::FillDPM for CROC "
				<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
				(channelTrial->GetChainNumber());
			acqData.critStream() << "->SendMessage Error Level = " << success;
			return false; 
		}
		return true; 
	}
	acqData.critStream() << "Exiting acquire_data::FillDPM; DPM is full for CROC "
		<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
		(channelTrial->GetChainNumber());
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
#if DEBUG_VERBOSE
	acqData.debugStream() << "--Entering acquire_data::TakeAllData--" << std::endl;
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
	evt->feb_info[1] = 0;     // Crate number.  Assigned in minervadaq::main().
	evt->feb_info[2] = (crocTrial->GetCrocAddress()>>16);
	evt->feb_info[3] = channelTrial->GetChainNumber(); 
	evt->feb_info[6] = febTrial->GetFEBNumber();
#if DEBUG_VERBOSE 
	acqData.debugStream() << "    CROC  : " << evt->feb_info[2];
        acqData.debugStream() << "    CHAIN : " << evt->feb_info[3];
        acqData.debugStream() << "    FEB   : " << evt->feb_info[6];
#endif	
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
			std::cout << "Error adding FPGA Information to DPM in acquire_data::TakeAllData!" << std::endl;
			std::cout << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
				channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber() << std::endl;
			acqData.fatalStream() << "Error adding FPGA Information to DPM in acquire_data::TakeAllData!";
			acqData.fatalStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
				channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
			exit(-1001);
		}
		febTrial->message = new unsigned char [FEB_INFO_SIZE];
		for (int debug_index=0; debug_index<febTrial->GetIncomingMessageLength(); debug_index++) {
			febTrial->message[debug_index] = channelTrial->GetBuffer()[debug_index];
		}
		// TODO - Do we really need to decode the register values?... probably not.
		// TODO - Decoding does provide an error check of sorts, but this inefficient.
		febTrial->DecodeRegisterValues(febTrial->GetIncomingMessageLength());
#if SHOW_REGISTERS
		febTrial->ShowValues();
#endif
		delete [] febTrial->message;
		febTrial->DeleteOutgoingMessage(); // Required after MakeMessage()
#if TIME_ME
		lock.lock();
		gettimeofday(&stop_time,NULL);
		duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
			(start_time.tv_sec*1e6+start_time.tv_usec);
		take_data_log << "******************FEB FRAMES*********************************" << std::endl; 
		take_data_log << "Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec) << " Stop Time: "
			<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
		take_data_log << "*************************************************************" << std::endl; 
		frame_acquire_log << evt->gate << "\t" << thread << "\t" << "2" << "\t" << 
			(start_time.tv_sec*1000000+start_time.tv_usec) << "\t" << 
			(stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
		lock.unlock();
#endif
#if DEBUG_VERBOSE
		acqData.debugStream() << "  Acquired FPGA programming data for:";
		acqData.debugStream() << "    CROC:  " << (crocTrial->GetCrocAddress()>>16);
		acqData.debugStream() << "    CHAIN: " << channelTrial->GetChainNumber();
		acqData.debugStream() << "    FEB:   " << febTrial->GetBoardNumber();
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
		frame_acquire_log << evt->gate << "\t" << thread << "\t" << "10" << "\t"
			<< (start_time.tv_sec*1000000+start_time.tv_usec) << "\t"
			<< (stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
		lock.unlock();
#endif
		evt->feb_info[7]=(int)febTrial->GetFirmwareVersion();
#if DEBUG_VERBOSE
		acqData.debugStream() << "  Firmware Version (header val): " << (int)evt->feb_info[7];
		acqData.debugStream() << "  Data Length (header val)     : " << evt->feb_info[5];
		acqData.debugStream() << "  Bank Type (header val)       : " << evt->feb_info[4];
#endif

		// Send the data to the EB via ET.
#if DEBUG_VERBOSE
		acqData.debugStream() << "  Contacting the Event Builder Service.";
		acqData.debugStream() << "   Bank  : " << evt->feb_info[4];
		acqData.debugStream() << "   Thread: " << thread;
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
		frame_acquire_log << evt->gate << "\t" << thread << "\t" << "20" << "\t"
			<< (start_time.tv_sec*1000000+start_time.tv_usec) << "\t"
			<< (stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
		lock.unlock();
#endif 
#if DEBUG_VERBOSE
		acqData.debugStream() << "  Back from EB after FPGA read...";
#endif
		// Read a discriminator frame.
		// First, decide if the discriminators are on.
		bool disc_set = false;
#if READ_DISC
		disc_set = true;
#endif
		if (disc_set) { 
#if DEBUG_VERBOSE
			acqData.debugStream() << "--Discriminator Frame";
#endif
			if (!(memory_reset = ResetDPM(crocTrial, channelTrial))) {
				std::cout << "Unable to reset DPM in acquire_data::TakeAllData for DISC readout." << std::endl;
				std::cout << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber() << std::endl;
				acqData.fatalStream() << "Unable to reset DPM in acquire_data::TakeAllData for DISC readout";
				acqData.fatalStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
				exit(-1004);
			} 
#if TIME_ME
			gettimeofday(&start_time, NULL);
#endif
			try {
				success = AcquireDeviceData(febTrial->GetDisc(), crocTrial, channelTrial, FEB_DISC_SIZE);
				if ((success)||(!memory_reset)) throw success;
			} catch (bool e) {
				std::cout << "Error in acquire_data::TakeAllData adding DISC Information to DPM!" << std::endl;
				std::cout << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber() << std::endl;
				acqData.fatalStream()<< "Error in acquire_data::TakeAllData adding DISC Information to DPM!";
				acqData.fatalStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
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
			frame_acquire_log << evt->gate << "\t" << thread << "\t" << "1" << "\t" << 
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
			take_data_log << "*******************************************************************" << std::endl; 
			frame_acquire_log << evt->gate << "\t" << thread << "\t" << "11" << "\t"
				<< (start_time.tv_sec*1000000+start_time.tv_usec) << "\t"
				<< (stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
			lock.unlock();
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
#if DEBUG_VERBOSE
			acqData.debugStream() << "  Acquired DISC data for: ";
			acqData.debugStream() << "    CROC:  " << crocTrial->GetCrocID();
			acqData.debugStream() << "    Chain: " << channelTrial->GetChainNumber();
			acqData.debugStream() << "    FEB:   " << febTrial->GetBoardNumber();
			acqData.debug("    Hit Info words: [12]0x%02X [13]0x%02X",evt->event_data[12], evt->event_data[13]);
#endif
			// Hit Info in event_data for discriminator frames in indices 12 && 13.
			//  event_data[12] = 0xWX, event_data[13] = 0xYZ
			//  W = # of hits TriP 0, X = # of hits TriP 1, Y = # of hits TriP 2, Z = # of hits TriP 3
			//  (Possibly the byte assignment is wrong/flipped somehow...)
			//  Whether we are pushing in pairs or not, we always want to read a number of adc blocks
			//  corresponding to the largest number of hits between the four plus one (end of gate).
			// Calculate the hits variable so we can read the correct number of ADC Frames. 
			unsigned char maxHits = (evt->event_data[12] >= evt->event_data[13]) ? 
				evt->event_data[12] : evt->event_data[13];
			hits = ( (maxHits & 0x0F) >= ((maxHits & 0xF0)>>4) ) ? 
				((unsigned int)maxHits & 0x0F) : ((unsigned int)(maxHits & 0xF0)>>4);	
			// We need to add a readout for the end-of-gate "hit."
			hits++;
#if DEBUG_VERBOSE
			acqData.debugStream() << "    Will read " << hits << " ADC banks...";
#endif 
		} // End discriminators-on check.

		// Now read the ADC Frames.
#if READ_ADC
#if DEBUG_VERBOSE
		acqData.debugStream() << "--ADC Frames ";
#endif
		if (hits == -1) hits = 1; 
#else
		hits = -1; // Don't read the ADC's...
#endif		
		for (int i=0; i<hits; i++) {

			// Set the hit id... we read the last hit pushed first, so increment sourceID hit in reverse.
			evt->feb_info[8] = (unsigned int)(hits - 1 - i);

			// Reset the DPM pointer & clear the status.
			// TODO - Use a try-catch block here.
			if (!(memory_reset = ResetDPM(crocTrial, channelTrial))) {
				std::cout << "Unable to reset DPM in acquire_data::TakeAllData for ADC readout." << std::endl;
				std::cout << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber() << std::endl;
				acqData.fatalStream() << "Unable to reset DPM in acquire_data::TakeAllData for ADC readout";
				acqData.fatalStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
				exit(-1004);
			} 
			// Read an ADC block...
			try {
				success = AcquireDeviceData(febTrial->GetADC(i), crocTrial, channelTrial,FEB_HITS_SIZE);
				if (success) throw success;
			} catch (bool e) {
				std::cout << "Error adding ADC Information to the DPM in acquire_data::TakeAllData!" << std::endl;
				acqData.fatalStream() << "Error adding ADC Information to the DPM in acquire_data::TakeAllData!";
				acqData.fatalStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
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
			frame_acquire_log << evt->gate << "\t" << thread << "\t" << "0" << "\t" << 
				(start_time.tv_sec*1000000+start_time.tv_usec) << "\t" << 
				(stop_time.tv_sec*1000000+stop_time.tv_usec) << std::endl;
			lock.unlock();
			gettimeofday(&start_time, NULL);
#endif
			// Fill the event_handler structure with data.
			FillEventStructure(evt, 0, febTrial->GetADC(i), channelTrial);
#if TIME_ME
			lock.lock();
			gettimeofday(&stop_time,NULL);
			duration = (stop_time.tv_sec*1e6+stop_time.tv_usec)-
				(start_time.tv_sec*1e6+start_time.tv_usec);
			take_data_log << "********************ADC FILL EVENT STRUCTURE********************" << std::endl; 
			take_data_log << "Start Time: " << (start_time.tv_sec*1e6+start_time.tv_usec) << " Stop Time: "
				<< (stop_time.tv_sec*1e6+stop_time.tv_usec) << " Run Time: " << (duration/1e6) << std::endl;
			take_data_log << "****************************************************************" << std::endl; 
			frame_acquire_log << evt->gate << "\t" << thread << "\t" << "12" << "\t"
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
#if DEBUG_VERBOSE
			acqData.debugStream() << "  Acquired ADC data for:";
			acqData.debugStream() << "    CROC:  " << crocTrial->GetCrocID();
			acqData.debugStream() << "    Chain: " << channelTrial->GetChainNumber();
			acqData.debugStream() << "    FEB:   " << febTrial->GetBoardNumber();
#endif
		} //end of hits loop

	} catch (bool e)  {
		std::cout << "The DPM wasn't reset at the start of acquire_data::TakeAllData!" << std::endl;
		std::cout << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
			channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber() << std::endl;
		acqData.fatalStream() << "The DPM wasn't reset at the start of acquire_data::TakeAllData!";
		acqData.fatalStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
			channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
		exit(-1000);
	}

	// Wait for threads to join if nedessary.
#if THREAD_ME
	// TODO - eb_threads[1]?
	eb_threads[0]->join();
	eb_threads[2]->join();
#endif 

#if DEBUG_VERBOSE
	acqData.debugStream() << "--Exiting  acquire_data::TakeAllData--";
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
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debugStream() << "    Entering acquire_data::ResetDPM for CROC " << (crocTrial->GetCrocAddress()>>16) << 
		" Chain " << channelTrial->GetChainNumber();
#endif
	bool reset = false;
	CVAddressModifier AM  = daqController->GetAddressModifier();
	CVDataWidth       DW  = daqController->GetDataWidth();
	CVDataWidth       DWS = crocTrial->GetDataWidthSwapped();
	unsigned char message[2] = {0x0A, 0x0A}; // 0202 + 0808 for clear status AND reset.
	 // Clear the status & reset the pointer.
	try {
		int success = daqAcquire->WriteCycle(daqController->handle, 2, message, 
			channelTrial->GetClearStatusAddress(), AM, DW);
		if (success) throw success;
	} catch (int e) {
		std::cout << "Error in acquire_data::ResetDPM!  Cannot write to the status register!" << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in acquire_data::ResetDPM!  Cannot write to the status register!";
		acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) << 
			" Chain " << channelTrial->GetChainNumber();
		return false;
	}
	// Check the value of the pointer.  Probably better is reading the status register...
	try { 
		int success = daqAcquire->ReadCycle(daqController->handle, message, 
			channelTrial->GetDPMPointerAddress(), AM, DWS); 
		if (success) throw success;
	} catch (int e) {
		std::cout << "Error in acquire_data::ResetDPM!  Cannot read the dpm pointer value!" << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in acquire_data::ResetDPM!  Cannot read the dpm pointer value!";
		return false;
	}
	unsigned short dpmPointer = (unsigned short) (message[0] | (message[1]<<0x08));
	// Need to check status register too!!
	if (dpmPointer==2) reset = true; // Not enough! TODO - Check status register here too.
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debugStream() << "     Exiting acquire_data::ResetDPM.";
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
 * Returns a status integer, and 0 indicates success.
 */
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debugStream() << "      Entering acquire_data::SendMessage...";
#endif
	int success          = 1; // Flag for finding an feb on the channel.
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth DW       = daqController->GetDataWidth();
	CVDataWidth DWS      = crocTrial->GetDataWidthSwapped();

	unsigned char send_message[2] ={0x01, 0x01}; // Send message mask.
	unsigned short status, dpmPointer;
	unsigned char reset_status[2];
	if (singleton) {
		unsigned char reset_message[2] ={0x0A, 0x0A}; // Clear status & Reset DPM Pointer mask.
		// Clear status & Reset DPM Pointer
		// TODO - This makes no sense if we are coming from acquire_data::FillDPM... hence the singleton flag!
		try {
			int error = daqAcquire->WriteCycle(daqController->handle, 2, reset_message, 
				channelTrial->GetClearStatusAddress(), AM, DW);
			if (error) throw error;
		} catch (int e) {
			std::cout << "Unable to Clear the Status & Reset DPM Pointer in acquire_data::SendMessage!" 
				<< std::endl;
			daqController->ReportError(e);
			acqData.critStream() << "Unable to Clear the Status & Reset DPM Pointer in acquire_data::SendMessage!"; 
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) << 
				" Chain " << channelTrial->GetChainNumber();
			return e;
		}
	}
	// Read the DPM Pointer
	try {
               	int error = daqAcquire->ReadCycle(daqController->handle, reset_status,
			channelTrial->GetDPMPointerAddress(), AM, DWS);
		if (error) throw error;
        } catch (int e) {
               	std::cout << "Unable to read DPM Pointer in acquire_data::SendMessage!" << std::cout;
		daqController->ReportError(e);
               	acqData.critStream() << "Unable to read DPM Pointer in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
			" Chain " << channelTrial->GetChainNumber();
		return e;
	}
	dpmPointer = (unsigned short) (reset_status[0] | (reset_status[1]<<0x08));
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debug("       acquire_data::SendMessage - RESET - Channel %d dpmPointer = 0x%X",
		channelTrial->GetChainNumber(),dpmPointer);	
#endif
	// Read the status register.
	try {
		int error = daqAcquire->ReadCycle(daqController->handle, reset_status, 
			channelTrial->GetStatusAddress(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Unable to Read the Status Register in acquire_data::SendMessage!" << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Unable to Read the Status Register in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
			" Chain " << channelTrial->GetChainNumber();
		return e;
	}
	status = (unsigned short) (reset_status[0] | reset_status[1]<<0x08);
	channelTrial->SetChannelStatus(status);
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debug("       acquire_data::SendMessage - RESET - Chain %d Status = 0x%X",
		channelTrial->GetChainNumber(),status);	
#endif
	// Check for errors. 
	try {
		int error = channelTrial->DecodeStatusMessage();
		if (error) throw error;
	} catch (int e) {
		printf(" Chain %d Status = 0x%X\n",channelTrial->GetChainNumber(),status); 
		printf(" Error Code = %d\n",e);
		acqData.crit("Chain %d Status = 0x%X",channelTrial->GetChainNumber(),status); 
		acqData.crit("Error Code = %d",e);
		return e;
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
			acqData.critStream() << "Error in acquire_data::SendMessage while writing to the FIFO!";
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			return e;
		}
		// TODO - Investigate using FIFO BLT for FPGA programming frames though...
		// // FIFO BLT is a bit funky for a general class function...
		// int count;
		// CAENVME_FIFOBLTWriteCycle(daqController->handle, channelTrial->GetFIFOAddress(), 
		// 	device->GetOutgoingMessage(), device->GetOutgoingMessageLength(), 
		// 	AM, DWS, &count);   
		//
		// Send the message.
		try {
			int error = daqAcquire->WriteCycle(daqController->handle, 2, send_message, 
				channelTrial->GetSendMessageAddress(), AM, DW); 
			if (error) throw error;
		} catch (int e) {
			std::cout << " Error in acquire_data::SendMessage while writing to the SendMessage address!" << std::endl;
			daqController->ReportError(e);
			acqData.critStream() << "Error in acquire_data::SendMessage while writing to the SendMessage address!";
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			return e;
		}
		// TODO - Fix this and setup a more general status checker...
		do {
			try {
				int error = daqAcquire->ReadCycle(daqController->handle, reset_status, 
					channelTrial->GetStatusAddress(), AM, DW);
				if (error) throw error;
			} catch (int e) {
				std::cout << " Error in acquire_data::SendMessage while reading the status register!" 
					<< std::endl;
				daqController->ReportError(e);
				acqData.critStream() << "Error in acquire_data::SendMessage while reading the status register!";
				acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
					" Chain " << channelTrial->GetChainNumber();	
				return e;
			} 
                	status = (unsigned short)(reset_status[0] | reset_status[1]<<0x08);
			channelTrial->SetChannelStatus(status);
#if DEBUG_SENDMESSAGE
			acqData.debug("       acquire_data::SendMessage - SENDING - Chain %d status = 0x%04X",
				channelTrial->GetChainNumber(),status);
#endif
		} while ( !(status & MessageReceived) && !(status & CRCError) && !(status & TimeoutError) 
			&& (status & RFPresent) && (status & SerializerSynch) && (status & DeserializerLock) 
			&& (status & PLLLocked) );
		if ( (status & CRCError) ) { 
			std::cout << "CRC Error!\n";  
			acqData.critStream() << "CRC Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			return (-10); 
		}
		if ( (status & TimeoutError) ) { 
			std::cout << "Timeout Error!\n";       
			acqData.critStream() << "Timeout Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			return (-11); 
		}

		if ( (status & FIFONotEmpty) ) { 
			std::cout << "FIFO Not Empty!\n";       
			acqData.critStream() << "FIFO Not Empty Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			//return (-11); 
		}
		if ( (status & FIFOFull) ) { 
			std::cout << "FIFO Full!\n";       
			acqData.critStream() << "FIFO Full Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			//return (-11); 
		}
		if ( (status & DPMFull) ) { 
			std::cout << "DPM Full!\n";       
			acqData.critStream() << "DPM Full Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			//return (-11); 
		}
		if ( !(status & RFPresent) ) { 
			std::cout << "No RF Present!\n";       
			acqData.critStream() << "No RF Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			return (-12); 
		}
		if ( !(status & SerializerSynch) ) { 
			std::cout << "No SerializerSynch!\n";  
			acqData.critStream() << "No SerializerSynch Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			return (-13); 
		}
		if ( !(status & DeserializerLock) ) { 
			std::cout << "No DeserializerLock!\n"; 
			acqData.critStream() << "DeserializerLock Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			return (-14); 
		}
		if ( !(status & PLLLocked) ) { 
			std::cout << "No PLLLock!\n"; 
			acqData.critStream() << "PLLLock Error in acquire_data::SendMessage!";         
			acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
				" Chain " << channelTrial->GetChainNumber();	
			return (-15); 
		}
		success = 0;
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
 */
#if DEBUG_VERBOSE
	acqData.debugStream() << "   Entering acquire_data::ReceiveMessage...";
#endif
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVAddressModifier AM_BLT = channelTrial->GetBLTModifier();
	CVDataWidth DWS = crocTrial->GetDataWidthSwapped();

	unsigned short dpmPointer;
	unsigned char status[2];
	try {
		int error = daqAcquire->ReadCycle(daqController->handle, status, 
			channelTrial->GetDPMPointerAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::ReceiveMessage!  Cannot read the status register!" << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in acquire_data::ReceiveMessage!  Cannot read the status register!";
		return e;
	}
	dpmPointer = (unsigned short) (status[0] | status[1]<<0x08);
#if DEBUG_VERBOSE
	acqData.debugStream() << "    acquire_data::Receive Message DPM Pointer: " << dpmPointer;
#endif
	device->SetIncomingMessageLength(dpmPointer-2);
	// We must read an even number of bytes.
	if (dpmPointer%2) {
		device->message = new unsigned char [dpmPointer+1];
	} else {
		device->message = new unsigned char [dpmPointer];
	}
	try {
		int error = daqAcquire->ReadBLT(daqController->handle, device->message, dpmPointer, 
			channelTrial->GetDPMAddress(), AM_BLT, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::ReceiveMessage!  Cannot ReadBLT!" << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in acquire_data::ReceiveMessage!  Cannot ReadBLT!";
		acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
			" Chain " << channelTrial->GetChainNumber();	
		return e;
	}
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
 *  \param int length an integer which tells the maximum size of the data block in bytes
 *
 *  Returns a status integer.
 */
#if THREAD_ME
	lock lock_send(send_lock);
#endif
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debugStream() << " Entering acquire_data::AcquireDeviceData...";
	acqData.debugStream() << "  CROC Address:   " << (crocTrial->GetCrocAddress()>>16);
	acqData.debugStream() << "  Chain Number: " << channelTrial->GetChainNumber();
	acqData.debug("  Device:         0x%X",frame->GetDeviceType());
#endif
	CVAddressModifier AM  = daqController->GetAddressModifier();
	CVDataWidth       DWS = crocTrial->GetDataWidthSwapped();
	int success           = 0;
	// Try to add this frame's data to the DPM.
	// TODO - Reorganize & clean-up the try-catches here...
	try { 
		success = FillDPM(crocTrial, channelTrial, frame, frame->GetIncomingMessageLength(), length);
		if (!success) throw success; 
		unsigned short dpmPointer;
		unsigned char status[2];
		daqAcquire->ReadCycle(daqController->handle, status, 
			channelTrial->GetDPMPointerAddress(), AM, DWS);
		dpmPointer = (unsigned short)(status[0] | status[1]<<0x08);
		frame->SetIncomingMessageLength(dpmPointer-2);
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
		acqData.debugStream() << "    acquire_data::AcquireDeviceData dpmPointer     = " << dpmPointer;
		acqData.debugStream() << "    acquire_data::AcquireDeviceData Message Length = " << frame->GetIncomingMessageLength();
#endif 
		success = GetBlockRAM(crocTrial, channelTrial); 
		frame->message = new unsigned char [frame->GetIncomingMessageLength()];
		for (int index=0;index<frame->GetIncomingMessageLength();index++) {
			frame->message[index] = channelTrial->GetBuffer()[index];
		}
#if SHOW_REGISTERS
		acqData.debugStream() << "    Decoding Register Values in acquire_data::AcquireDeviceData...";
		frame->DecodeRegisterValues(frame->GetIncomingMessageLength());
#endif
		delete [] frame->message;
		if (success) throw success; 
	} catch (bool e) { 
		// If unsuccessful, the DPM doesn't have enough memory, and we need to process what is there (?)
		std::cout << "DPM Fill Failure!  DPM Should have been reset before tyring to use!" << std::endl;
		acqData.fatalStream() << "DPM Fill Failure!  DPM Should have been reset before tyring to use!";
		acqData.critStream() << "  Error on CROC " << (crocTrial->GetCrocAddress()>>16) <<
			" Chain " << channelTrial->GetChainNumber();
 		exit(-4001);
	}
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debugStream() << "   AcquireDeviceData success: " << success;
#endif
	return success;
}


int acquire_data::TriggerDAQ(unsigned short int triggerBit, int crimID) 
{
/*! \fn void acquire_data::TriggerDAQ(unsigned short int triggerBit, int crimID)
 *
 * A function which sets up the acquisition trigger indexed by parameter a.
 *
 * Currently, we have the following triggers defined as enumerated types in the DAQ Header (v5):
 *  TODO - Make sure trigger types and documentation stay current for new DAQ Header.
 *  Note the trigger does not depend on CRIM timing mode explicity, but there is occasionally an 
 *  implicit dependence (e.g., NuMI can only run in CRIM MTM mode).
 * UnknownTrigger  = 0x0000,
 * Pedestal        = 0x0001,
 * LightInjection  = 0x0002,
 * ChargeInjection = 0x0004,
 * Cosmic          = 0x0008,
 * NuMI            = 0x0010,
 * TGReserved6     = 0x0020,
 * TGReserved7     = 0x0040,
 * MonteCarlo      = 0x0080'
 *
 * \param unsigned short int triggerBit The trigger bit.
 * \param int crimID The CRIM we are "triggering." 
 *
 * Returns a status integer (0 for success).
 */
#if DEBUG_TRIGGER
	acqData.debug("   Entering acquire_data::TriggerDAQ with trigger bit 0x%02X",triggerBit);
	acqData.debug("   ->Preparing to address CRIM %d",(daqController->GetCrim(crimID)->GetCrimAddress()>>16));
#endif
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth       DW = daqController->GetDataWidth();
	int error     = -1;
	int errorCode =  1;
	switch (triggerBit) { 
		case UnknownTrigger: // Default to issuing a software trigger or exit?...
			acqData.warnStream() << "   WARNING! You have not set the triggerType somehow!";
			acqData.warnStream() << "   -> Defaulting to running the sequencer...";
			std::cout << "   WARNING! You have not set the triggerType somehow!" << std::endl;
			std::cout << "   -> Defaulting to running the sequencer..." << std::endl;
		case Pedestal: 
		case LightInjection:
		case ChargeInjection:
			// Start the sequencer (trigger CNRST software pulse)
#if DEBUG_TRIGGER
			acqData.debugStream() << "   Preparing to start the sequencer...";
#endif
			try {
				unsigned char send_pulse[2];
				send_pulse[0] = daqController->GetCrim(crimID)->GetSoftCNRSTSeq() & 0xFF;
				send_pulse[1] = (daqController->GetCrim(crimID)->GetSoftCNRSTSeq()>>0x08) & 0xFF;
#if DEBUG_TRIGGER
				acqData.debug("    send_pulse msg = 0x%02X%02X",send_pulse[1],send_pulse[0]);
				acqData.debug("    pulse address  = 0x%X",daqController->GetCrim(crimID)->GetSoftCNRSTRegister());
#endif
				error = daqAcquire->WriteCycle(daqController->handle, 2, send_pulse,
					daqController->GetCrim(crimID)->GetSoftCNRSTRegister(), AM, DW); 
				if (error) throw error;
			} catch (int e) {
				std::cout << "Unable to set the pulse delay register in acquire_data::TriggerDAQ!" << std::endl;
				daqController->ReportError(e);
				//acqData.fatalStream() << "Unable to set the pulse delay register in acquire_data::TriggerDAQ!";
				//exit(-2005);
				acqData.critStream() << "Unable to set the pulse delay register in acquire_data::TriggerDAQ!";
				return errorCode;
			}
#if DEBUG_TRIGGER
			acqData.debugStream() << "    ->Sent Sequencer Init. Signal!";
#endif
			break;
		// The NuMI Beam trigger is initiated via an external signal.
		case NuMI:
			break;
		case MonteCarlo:
			std::cout << "WHY ARE YOU TRYING TO WRITE A MC TRIGGER INTO THE DAQ HEADER!?" << std::endl;
			acqData.fatalStream() << "WHY ARE YOU TRYING TO WRITE A MC TRIGGER INTO THE DAQ HEADER!?";
			exit(-2000);
		default:
			std::cout << "Invalid trigger mode in acquire_data::TriggerDAQ!" << std::endl;
			acqData.fatalStream() << "Invalid trigger mode in acquire_data::TriggerDAQ!";
			exit(-2001);
	}  
	return 0;
}


int acquire_data::WaitOnIRQ() 
{
/*! \fn void acquire_data::WaitOnIRQ() 
 *
 * A function which waits on the interrupt handler to set an interrupt.  This function 
 * only checks the "master" CRIM.  The implicit assumption is that a trigger on any 
 * CRIM is a trigger on all CRIMs (this assumption is true by design).
 *
 * Two options exist, one can wait for the CAEN interrupt handler to Wait on IRQ, or 
 * the status register can be polled until the interrupt bits are driven high.
 *
 * Returns a status integer (0 for success);
 */
	int error;
	int errorCode = 2;
#if DEBUG_IRQ
	acqData.debugStream() << "  Entering acquire_data::WaitOnIRQ: IRQLevel = " << daqController->GetCrim()->GetIRQLevel();
#endif
#if ASSERT_INTERRUPT
#if DEBUG_IRQ
	acqData.debugStream() << "  Asserting Interrupt!";
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
		std::cout << "The IRQ Wait probably timed-out..." << e << std::endl;
		//acqData.fatalStream() << "The IRQ Wait probably timed-out..." << e;
		//exit(-3000);
		acqData.critStream() << "The IRQ Wait probably timed-out..." << e;  
		return errorCode;
	}
#endif
// endif - ASSERT_INTERRUPT

#if POLL_INTERRUPT
#if DEBUG_IRQ
	acqData.debugStream() << "  Polling Interrupt!";
	int intcounter = 0;
#endif
	unsigned short interrupt_status = 0;
	unsigned char crim_send[2];
	// TODO - Add a break condition to get out of the interrupt polling...
	while (!(interrupt_status&0x04)) { //0x04 is the IRQ Line of interest
		try {
			crim_send[0] = 0; crim_send[1] = 0;
			error = daqAcquire->ReadCycle(daqController->handle, crim_send,
				daqController->GetCrim()->GetInterruptStatusAddress(), 
				daqController->GetAddressModifier(),
				daqController->GetDataWidth());  
#if DEBUG_IRQ
			intcounter++;
			if (!(intcounter%10000)) {
				acqData.debug("    %06d - Interrrupt status = 0x%02X", intcounter, 
					(crim_send[0] + (crim_send[1]<<8)));  
			}
#endif
			if (error) throw error;
			interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08));
		} catch (int e) {
			std::cout << "Error getting crim interrupt status in acquire_data::WaitOnIRQ!" << std::endl;
			daqController->ReportError(e);
			//acqData.fatalStream() << "Error getting crim interrupt status in acquire_data::WaitOnIRQ!";
			//exit(-5);
			acqData.critStream() << "Error getting crim interrupt status in acquire_data::WaitOnIRQ!";
			return errorCode;
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
		std::cout << "Error clearing crim interrupts in acquire_data::WaitOnIRQ!" << std::endl;
		daqController->ReportError(e);
		//acqData.fatalStream() << "Error clearing crim interrupts in acquire_data::WaitOnIRQ!";
		//exit(-6);
		acqData.critStream() << "Error clearing crim interrupts in acquire_data::WaitOnIRQ!";
		return errorCode;
	}
#endif
// endif - POLL_INTERRUPT
	return 0;
}


int acquire_data::AcknowledgeIRQ() 
{
/*! \fn void acquire_data::AcknowledgeIRQ() 
 *
 * A function which acknowledges and resets the interrupt handler.
 *
 * Returns a status integer (0 for success).
 */
// TODO - AcknowledgeIRQ() needs a lot of try-catch polishing if we start using it...
#if DEBUG_IRQ
	acqData.debugStream() << "  Entering acquire_data::AcknowledgeIRQ...";
#endif
	CVDataWidth DW = daqController->GetDataWidth();
	int error;
	int errorCode = 3;
	try {
		unsigned short vec;
		error = CAENVME_IACKCycle(daqController->handle, daqController->GetCrim()->GetIRQLevel(), 
			&vec, DW);
#if DEBUG_IRQ
		acqData.debugStream() << "IRQ LEVEL: " << daqController->GetCrim()->GetIRQLevel() << " VEC: " << vec;
#endif
		unsigned short interrupt_status;
		unsigned char crim_send[2];
		crim_send[0] = 0; crim_send[1] = 0;  
		error = daqAcquire->ReadCycle(daqController->handle, crim_send,
			daqController->GetCrim()->GetInterruptStatusAddress(), 
			daqController->GetAddressModifier(),
			daqController->GetDataWidth()); 
		interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08)); 

		while (interrupt_status) {
			try {
				crim_send[0] = 0; crim_send[1] = 0;
				error = daqAcquire->ReadCycle(daqController->handle, crim_send,
					daqController->GetCrim()->GetInterruptStatusAddress(), 
					daqController->GetAddressModifier(),
					daqController->GetDataWidth()); 
				if (error) throw error;
				interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08)); 

				// Clear the interrupt after acknowledging it.
				crim_send[0] = daqController->GetCrim()->GetClearInterrupts() & 0xff;
				crim_send[1] = (daqController->GetCrim()->GetClearInterrupts()>>0x08) & 0xff;
				try {
					error = daqAcquire->WriteCycle(daqController->handle, 2, crim_send,
						daqController->GetCrim()->GetClearInterruptsAddress(), 
						daqController->GetAddressModifier(),
						daqController->GetDataWidth()); 
					// Read the status register 
					crim_send[0] = 0; crim_send[1] = 0; 
					error = daqAcquire->ReadCycle(daqController->handle, crim_send,
						daqController->GetCrim()->GetInterruptStatusAddress(), 
						daqController->GetAddressModifier(),
						daqController->GetDataWidth()); 
					if (error) throw error;
					interrupt_status = (crim_send[0]|(crim_send[1]<<0x08)); 
				} catch (int e) {
					std::cout << "Error clearing crim interrupts in acquire_data::AcknowledgeIRQ!" << std::endl;
					daqController->ReportError(e);
					acqData.fatalStream() <<"Error clearing crim interrupts in acquire_data::AcknowledgeIRQ!";
					exit(-6);
				} 
			} catch (int e) {
				std::cout << "Error getting crim interrupt status in acquire_data::AcknowledgeIRQ!" << std::endl;
				daqController->ReportError(e);
				acqData.fatalStream() << "Error getting crim interrupt status in acquire_data::AcknowledgeIRQ!";
				exit(-5);
			}
		}
		if (error) throw error;
		try {
			CVIRQLevels irqLevel = daqController->GetCrim()->GetIRQLevel();
#if DEBUG_IRQ
			acqData.debugStream() << "Set IRQ LEVEL: " << irqLevel << " Returned IRQ LEVEL: " << vec;
#endif
			if (vec!=0x0A) throw (int)vec; //for SGATEFall
		} catch (int e) {
			std::cout << "IRQ LEVEL returned did not match IRQ LINE Vector!" << std::endl;
			acqData.critStream() << "IRQ LEVEL returned did not match IRQ LINE Vector!";
		}
	} catch (int e) {
		std::cout << "The IRQ Wait probably timed-out in acquire_data::AcknowledgeIRQ!" << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "The IRQ Wait probably timed-out in acquire_data::AcknowledgeIRQ!";
		exit(-3000);  
	}
	return 0;
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
#if DEBUG_ET_REPORT_EVENT
		acqData.debugStream() << "Entering acquire_data::ContactEventBuilder...";
		acqData.debugStream() << " In Event Builder the bank type is: " << evt->feb_info[4];
		acqData.debugStream() << " The Header Data Length is:         " << evt->feb_info[5];
		if (evt->feb_info[4] != 3) {
			acqData.debugStream() << " Embedded Event Data Length is:     " << (unsigned int)evt->event_data[0] + 
				(unsigned int)(evt->event_data[1]<<8);
			for (int i = 0; i < 11; i++) {
				acqData.debugStream() << "  evt->event_data[" << i << "] = " << (unsigned int)evt->event_data[i]; 
			}
		}
#endif
	}

	// Now for the data buffer.  Use the embedded length!
	int length;
	if (evt->feb_info[4] == 3) {
		length = (int)(DAQ_HEADER);
	} else {
		length = evt->event_data[0] + (evt->event_data[1]<<8);
	}
#if DEBUG_ET_REPORT_EVENT
	acqData.debugStream() << "  Sending Data to ET System:";
#endif
	// Send event to ET for storage.
	while (et_alive(sys_id)) {
#if DEBUG_ET_REPORT_EVENT
		acqData.debugStream() << "  ->ET is Alive!";
#endif
		et_event *pe;         // The event.
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
			printf("ET system is dead in acquire_data::ContactEventBuilder!\n");
			acqData.crit("ET system is dead in acquire_data::ContactEventBuilder!");
			break;
		} else if (status == ET_ERROR_TIMEOUT) {
			printf("Got an ET timeout in acquire_data::ContactEventBuilder!\n");
			acqData.crit("Got an ET timeout in acquire_data::ContactEventBuilder!");
			break;
		} else if (status == ET_ERROR_EMPTY) {
			printf("No ET events in acquire_data::ContactEventBuilder!\n");
			acqData.crit("No ET events in acquire_data::ContactEventBuilder!");
			break;
		} else if (status == ET_ERROR_BUSY) {
			printf("ET Grandcentral is busy in acquire_data::ContactEventBuilder!\n");
			acqData.crit("ET Grandcentral is busy in acquire_data::ContactEventBuilder!");
			break;
		} else if (status == ET_ERROR_WAKEUP) {
			printf("ET wakeup error in acquire_data::ContactEventBuilder!\n");
			acqData.crit("ET wakeup error in acquire_data::ContactEventBuilder!");
			break;
		} else if ((status == ET_ERROR_WRITE) || (status == ET_ERROR_READ)) {
			printf("ET socket communication error in acquire_data::ContactEventBuilder!\n");
			acqData.crit("ET socket communication error in acquire_data::ContactEventBuilder!");
			break;
		} if (status != ET_OK) {
			printf("ET et_producer: error in et_event_new in acquire_data::ContactEventBuilder!\n");
			acqData.fatal("ET et_producer: error in et_event_new in acquire_data::ContactEventBuilder!");
			exit(0);
		} 
		// Put data into the event.
		if (status == ET_OK) {
#if DEBUG_ET_REPORT_EVENT
			acqData.debugStream() << "    Putting Event on ET System:";
#endif
#if THREAD_ME
			eb_lock.lock();
#endif
			et_event_getdata(pe, (void **)&pdata); // Get the event ready.
#if DEBUG_ET_REPORT_EVENT
			{ // Report_event print statements...
				acqData.debugStream() << "-----------------------------------------------"; 
				acqData.debugStream() << "      event_handler_size: " << sizeof(struct event_handler);
				acqData.debugStream() << "      evt_size:           " << sizeof(evt);
				acqData.debugStream() << "Finished Processing Event Data:";
				acqData.debugStream() << " GATE---------: " << evt->gate;
				acqData.debugStream() << " CROC---------: " << evt->feb_info[2];
				acqData.debugStream() << " CHANNEL------: " << evt->feb_info[3];
				acqData.debugStream() << " BANK---------: " << evt->feb_info[4];
				acqData.debugStream() << " DETECT-------: " << (int)evt->detectorType; 
				acqData.debugStream() << " CONFIG-------: " << evt->detectorConfig; 
				acqData.debugStream() << " RUN----------: " << evt->runNumber;
				acqData.debugStream() << " SUB-RUN------: " << evt->subRunNumber;
				acqData.debugStream() << " TRIGGER------: " << evt->triggerType;
				acqData.debugStream() << " GLOBAL GATE--: " << evt->globalGate;
				acqData.debugStream() << " TRIG TIME----: " << evt->triggerTime;
				acqData.debugStream() << " ERROR--------: " << evt->readoutInfo;
				acqData.debugStream() << " MINOS--------: " << evt->minosSGATE;
				acqData.debugStream() << " BUFFER_LENGTH: " << evt->feb_info[5];
				acqData.debugStream() << " FIRMWARE-----: " << evt->feb_info[7];
				acqData.debugStream() << " FRAME DATA---: " << std::endl;
#if SHOW_DATABYTES
				for (int index = 0; index < length; index++) {
					acqData.debug("     Data Byte %02d = 0x%02X",
						index,(unsigned int)evt->event_data[index]); 
				}
#endif
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
			printf("et_producer: put error in acquire_data::ContactEventBuilder!\n");
			acqData.fatal("et_producer: put error in acquire_data::ContactEventBuilder!");
			exit (0);
		} 
		if (!et_alive(sys_id)) {
			et_wait_for_alive(sys_id);
		}
		break; // Done processing the event. 
	} // while alive 
#if DEBUG_ET_REPORT_EVENT
	acqData.debugStream() << "  Exiting acquire_data::ContactEventBuilder...";
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
 */
#if DEBUG_VERBOSE
	acqData.debugStream() << "  Entering acquire_data::FillEventStructure with bank type " << bank 
		<< " and message length " << frame->GetIncomingMessageLength();
#endif
	// Build sourceID
	evt->feb_info[1] = daqController->GetID(); // Crate ID
	evt->feb_info[4] = bank;                   // 0==ADC, 1==TDC, 2==FPGA, 3==DAQ Header, 4==TriP-T
	const unsigned int dataLength = frame->GetIncomingMessageLength(); // Data length in the buffer.  
	const unsigned int buffLength = dataLength + 2; // Data + Frame CRC;
	evt->feb_info[5] = dataLength;
	// unsigned char tmp_buffer[buffLength]; // Set the buffer size. // Commented out with the double loop below...
#if DEBUG_VERBOSE
	acqData.debugStream() << "   Getting Data...";
	acqData.debugStream() << "     Link      (evt->feb_info[0]) = " << evt->feb_info[0];
	acqData.debugStream() << "     Crate     (evt->feb_info[1]) = " << evt->feb_info[1];
	acqData.debugStream() << "     CROC      (evt->feb_info[2]) = " << evt->feb_info[2];
	acqData.debugStream() << "     Chain     (evt->feb_info[3]) = " << evt->feb_info[3];
	acqData.debugStream() << "     Bank Type (evt->feb_info[4]) = " << evt->feb_info[4];
	acqData.debugStream() << "     Frame L.  (evt->feb_info[5]) = " << evt->feb_info[5];
	acqData.debugStream() << "     FEB Num.  (evt->feb_info[6]) = " << evt->feb_info[6];
	acqData.debugStream() << "     Firmware  (evt->feb_info[7]) = " << evt->feb_info[7];
	acqData.debugStream() << "     Hits      (evt->feb_info[8]) = " << evt->feb_info[8];
#endif
	for (unsigned int i = 0; i < buffLength; i++) { 
		evt->event_data[i] = channelTrial->GetBuffer()[i];   
	}
#if DEBUG_VERBOSE
	acqData.debugStream() << "   Got Data";
	acqData.debugStream() << "    Embedded (Data) Length      = " << (int)evt->event_data[0] + 
		(int)(evt->event_data[1]<<8);
	acqData.debugStream() << "    frame->IncomingMessageLength: " << frame->GetIncomingMessageLength();
	acqData.debugStream() << "    Total buffer length         = " << buffLength; 
#if SHOW_DATABYTES
	for (unsigned int index = 0; index < buffLength; index++) {
		acqData.debug("     FillStructure data byte %02d = 0x%02X", index, 
			(unsigned int)evt->event_data[index]); 
	}
#endif
#endif
}


unsigned int acquire_data::GetMINOSSGATE()
{
/*! \fn int acquire_data::GetMINOSSGATE()
 *
 * Read the logged value of the MINOS SGATE signal in their timing coordinates.
 */
	// Check only the master CRIM.
	unsigned char gatelo[2];
	unsigned char gatehi[2];
	unsigned int gatetime = 0;
	try {
		int error = daqAcquire->ReadCycle(daqController->handle, gatelo,
			daqController->GetCrim()->GetGateTimeWordLowAddress(),
			daqController->GetAddressModifier(),
			daqController->GetDataWidth());
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::GetMINOSSGATE()!  Cannot read MINOSSGATE!" << std::endl;
		acqData.critStream() << "Error in acquire_data::GetMINOSSGATE()!  Cannot read MINOSSGATE!";
		return 0;
	}
	try {
		int error = daqAcquire->ReadCycle(daqController->handle, gatehi,
			daqController->GetCrim()->GetGateTimeWordHighAddress(),
			daqController->GetAddressModifier(),
			daqController->GetDataWidth());
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::GetMINOSSGATE()!  Cannot read MINOSSGATE!" << std::endl;
		acqData.critStream() << "Error in acquire_data::GetMINOSSGATE()!  Cannot read MINOSSGATE!";
		return 0;
	}
	unsigned short hiword = (unsigned short)( gatehi[0]|(gatehi[1]<<0x08) & 0x0FFF ); 
	unsigned short loword = (unsigned short)( gatelo[0]|(gatelo[1]<<0x08) ); 
	gatetime = (unsigned int)( loword|(hiword<<0x10) ); 
	
	return gatetime;
}


#endif
