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

const int acquire_data::dpmMax                  = 1024*6; // we have only 6 Kb of space in the DPM Memory per channel
const unsigned int acquire_data::timeOutSec     = 3600;   // be careful shortening this w.r.t. multi-PC sync issues
const bool acquire_data::checkForMessRecvd      = true;   // fixed flag
const bool acquire_data::doNotCheckForMessRecvd = false;  // fixed flag

void acquire_data::InitializeDaq(int id, RunningModes runningMode, std::list<readoutObject*> *readoutObjs) 
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
	std::cout << "\nEntering acquire_data::InitializeDaq()." << std::endl;
	acqData.infoStream() << "Entering acquire_data::InitializeDaq().";
	acqData.infoStream() << "  FEB Firmware Version     = " << firmwareVersion;
	acqData.infoStream() << "  Number of Hits (disc+1)  = " << (numberOfHits-1) << "+1";
	acqData.infoStream() << "  HW (VME Card) Init Level = " << hwInitLevel;
#if V9CRIM
	acqData.infoStream() << "  Assuming V9 CRIM Firmware.";
#endif
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

	// Hardware configurations.
	std::string detectorString = "Unknown Detector.";
	int maxFebs = 11;
#if PMTTEST
	detectorString        = "LabF PMT X-talk Stand.";
	std::cout            << "Initializing hardware for the " << detectorString << std::endl; 
	acqData.infoStream() << "Initializing hardware for the " << detectorString; 
	InitializeCrim(0xE00000, 1, runningMode);
	InitializeCroc(0x030000, 1, 4, 0, 0, 0);
	maxFebs = 4;
#endif
#if MTEST
	detectorString        = "MTest.";
	std::cout            << "Initializing hardware for " << detectorString << std::endl; 
	acqData.infoStream() << "Initializing hardware for " << detectorString; 
	InitializeCrim(0xE00000, 1, runningMode);
	InitializeCroc(0x010000, 1, 4, 4, 4, 4);
	InitializeCroc(0x020000, 2, 4, 4, 5, 4); // 4,4,4,4 before end of day July 3, 2010.
	InitializeCroc(0x030000, 3, 4, 5, 0, 0);
	maxFebs = 5;
#endif
#if WH14T
	detectorString        = "WH14 Top Crate.";
	std::cout            << "Initializing hardware for the " << detectorString << std::endl; 
	acqData.infoStream() << "Initializing hardware for the " << detectorString; 
	InitializeCrim(0xE00000, 1, runningMode);
	InitializeCroc(0x010000, 1, 1, 1, 1, 0);
	maxFebs = 1;
#endif
#if WH14B
	detectorString        = "WH14 Bottom Crate.";
	std::cout            << "Initializing hardware for the " << detectorString << std::endl; 
	acqData.infoStream() << "Initializing hardware for the " << detectorString; 
	InitializeCrim(0xE00000, 1, runningMode);
	InitializeCroc(0x010000, 1, 1, 2, 1, 0);
	InitializeCroc(0x050000, 2, 0, 0, 0, 2);
	maxFebs = 2;
#endif
#if CRATE0 // Current as of March 22 Begin-Of-Run  
	detectorString        = "NuMI Crate 0.";
	std::cout            << "Initializing hardware for " << detectorString << std::endl; 
	acqData.infoStream() << "Initializing hardware for " << detectorString; 
	InitializeCrim(0xE00000, 1, runningMode);
	InitializeCrim(0xF00000, 2, runningMode);
	InitializeCroc(0x010000, 1, 10, 10, 10,  6); // MS01W, MS02W, MS03W, MS04W	036
	InitializeCroc(0x020000, 2, 10, 10,  9,  5); // MS01E, MS02E, MS03E, MS04E	034
	InitializeCroc(0x030000, 3, 10, 10, 10, 10); // MS05W, MS06W, MS07W, MS08W	040
	InitializeCroc(0x040000, 4,  9,  9,  9,  9); // MS05E, MS06E, MS07E, MS08E	036
	InitializeCroc(0x050000, 5, 10, 10, 10, 10); // MS09W, MS10W, MS11W, MS12W	040
	InitializeCroc(0x060000, 6,  9,  9,  9,  9); // MS09E, MS10E, MS11E, MS12E	036
	InitializeCroc(0x070000, 7, 10, 10, 10, 10); // MS13W, MS14W, MS15W, MS16W	040
	InitializeCroc(0x080000, 8,  9,  9,  9,  9); // MS13E, MS14E, MS15E, MS16E	036
	maxFebs = 10;					//				---298
#endif
#if CRATE1 // Current as of March 22 Begin-Of-Run 
	detectorString        = "NuMI Crate 1.";
	std::cout            << "Initializing hardware for " << detectorString << std::endl; 
	acqData.infoStream() << "Initializing hardware for " << detectorString; 
	InitializeCrim(0xE00000, 1, runningMode);
	InitializeCrim(0xF00000, 2, runningMode);
	InitializeCroc(0x010000, 1, 10, 10, 10, 10); // MS17W, MS18W, MS19W, MS20W	040
	InitializeCroc(0x020000, 2,  9,  9,  9,  9); // MS17E, MS18E, MS19E, MS20E	036
	InitializeCroc(0x030000, 3, 10, 10,  6,  6); // MS21W, MS22W, MS23W, MS24W	032
	InitializeCroc(0x040000, 4,  9,  9,  5,  5); // MS21E, MS22E, MS23E, MS24E	028
	InitializeCroc(0x050000, 5,  6,  6,  6,  2); // MS25W, MS26W, MS27W, Veto Wall 	020
	InitializeCroc(0x060000, 6,  5,  5,  5,  0); // MS25E, MS26E, MS27E, Loopback	015
	InitializeCroc(0x070000, 7, 10, 10, 10, 10); // MS00W, MS00E, MS-1W, MS-1E	040
	maxFebs = 10;					//				---211
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
	acqData.infoStream() << " Max Number of FEB's on a chain = " << maxFebs; 

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

	// Initialize readoutObjects list for data acquisition.
#if NEWREADOUT
	for (int i=1; i<=maxFebs; i++) {
		readoutObjs->push_back(new readoutObject(i));
	}
	InitializeReadoutObjects(readoutObjs);
#endif

	// Done with VME card initialization procedures!
	std::cout << "Finished Initialization!  Exiting acquire_data::InitializeDaq().\n" << std::endl;
	acqData.infoStream() << "Finished Initialization!  Exiting acquire_data::InitializeDaq().";
}


void acquire_data::InitializeCrim(int address, int index, RunningModes runningMode) 
{
/*! \fn void acquire_data::InitializeCrim(int address)
 *
 * This function checks the CRIM addressed by "address" is available by reading a register.  
 * Then the interrupt handler is set up.  In case of a failure, the DAQ exits hard.
 *
 * \param address an integer VME addres for the CRIM.
 * \param index an integer index used for internal bookkeeping.
 * \param runningMode an integer specifying what sort of run the DAQ is taking.
 */
	std::cout << "\nEntering acquire_data::InitializeCrim for address " << (address>>16) << std::endl;
	acqData.infoStream() << "Entering acquire_data::InitializeCrim for address " << (address>>16);
	acqData.infoStream() << "  HW (VME Card) Init Level = " << hwInitLevel;

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
		exit(e);
	} 

	// Note IRQLine is set in the CRIM constructor.  The default is SGATEFall, 
        // which is the correct choice for every running mode but Cosmics.  Also 
	// note the CRIM will ignore the SequencerEnable instruction in firmware 
	// before v9.
	unsigned short GateWidth         = 0x1;      // GetWidth must never be zero!
	unsigned short TCALBDelay        = 0x1;      // Delay should also be non-zero.
	unsigned short TCALBEnable       = 0x1;      // Enable pulse delay.
	unsigned short SequencerEnable   = 0x1;      // Sequencer control (0 means always send gates, 1 for rearms).
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
		// Because no MTM is available at MTest, LI there will use
		// the internal timing mode.
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
#if MTEST
			TimingMode   = crimInternal;
			acqData.infoStream() << " ->Using MTest timing (CRIM Internal).";
#else
			TimingMode   = MTM; 
			acqData.infoStream() << " ->Using normal timing (CRIM MTM).";
#endif
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
			//TCALBDelay   = 0x258; //Testing on 14
			Frequency    = F2; 
			TimingMode   = crimInternal; 
			TCALBEnable  = 0x1;
			daqController->GetCrim(index)->SetIRQLine(Trigger); //crimInterrupts type
			break;
		// Beam-Muon mode is equivalent to cosmic mode under the hood for the DAQ.  
		case MTBFBeamMuon:
			std::cout << " Running Mode is MTBFBeamMuon." << std::endl;
			acqData.infoStream() << " Running Mode is MTBFBeamMuon.";
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = F2; 
			TimingMode   = crimInternal; 
			TCALBEnable  = 0x1;
			daqController->GetCrim(index)->SetIRQLine(Trigger); //crimInterrupts type
			break;
		// Beam-Only mode is equivalent to cosmic mode under the hood for the DAQ.  
		case MTBFBeamOnly:
			std::cout << " Running Mode is MTBFBeamOnly." << std::endl;
			acqData.infoStream() << " Running Mode is MTBFBeamOnly.";
			GateWidth    = 0x7F;
			TCALBDelay   = 0x3FF;
			Frequency    = F2; 
			TimingMode   = crimInternal; 
			TCALBEnable  = 0x1;
			daqController->GetCrim(index)->SetIRQLine(Trigger); //crimInterrupts type
			break;
		default:
			std::cout << "Error in acquire_data::InitializeCrim()! No Running Mode defined!" << std::endl;
			acqData.fatalStream() << "Error in acquire_data::InitializeCrim()! No Running Mode defined!";
			exit(-4);
	}


	// Now write settings to hardware.
	if (hwInitLevel) {
		// Build Register Settings (this does not write to hardware, it only configures software objects).
		daqController->GetCrim(index)->SetupTiming(TimingMode, Frequency);
#if V9CRIM
		daqController->GetCrim(index)->SetupGateWidth(TCALBEnable, GateWidth, SequencerEnable);
#else 
		daqController->GetCrim(index)->SetupGateWidth(TCALBEnable, GateWidth);
#endif
		daqController->GetCrim(index)->SetupTCALBPulse(TCALBDelay);
		acqData.info("  CRIM Timing Setup    = 0x%04X", daqController->GetCrim(index)->GetTimingSetup());
		acqData.info("  CRIM GateWidth Setup = 0x%04X", daqController->GetCrim(index)->GetGateWidthSetup());
		acqData.info("  CRIM TCALB Setup     = 0x%04X", daqController->GetCrim(index)->GetTCALBPulse());

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
	} // endif hwInitLevel

	// Now set up the IRQ handler, initializing the global enable bit for the first go-around.
	// Only the "Master" (first) CRIM should be our interrupt handler...
	acqData.infoStream() << "Setting up IRQ handler on CRIM " << (address>>16);
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

	// Now make sure sequencer latch is set.
#if V9CRIM
	acqData.infoStream() << "Resetting sequencer control latch on CRIM " << (address>>16);
	try {
		int error = ResetSequencerControlLatch(index);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::InitializeCrim for CRIM with address = " << (address>>16) << std::endl;
		std::cout << "Cannot reset sequencer latch!" << std::endl;
		acqData.fatalStream() << "Error in acquire_data::InitializeCrim for CRIM with address = " << (address>>16);
		acqData.fatalStream() << "Cannot reset sequencer latch!";
		exit (e);
	}
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
// TODO - Pass HW Init Flag here too?
	std::cout << "\nEntering acquire_data::InitializeCroc for CROC " << (address>>16) << std::endl;
	acqData.infoStream() << "Entering acquire_data::InitializeCroc for CROC " << (address>>16);
	acqData.infoStream() << "  HW (VME Card) Init Level = " << hwInitLevel;
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth       DW = daqController->GetDataWidth();

	// Make a CROC object on this controller.
	daqController->MakeCroc(address,crocNo); 
	int nChains         = 4; // # of CROC FE Channels - always fixed for the real detector...
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
		exit(e);
	}

	// Set the timing mode to EXTERNAL: clock mode, test pulse enable, test pulse delay
	// Clock Mode set to External in CROC constructor.  
	if (hwInitLevel) {
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
	} // endif hwInitLevel

	// Build the FEB list for each channel.
	acqData.infoStream() << " Building FEB List:";
	for (int i = 0; i < nChains; i++) {
		// Now set up the channels and FEB's.
		croc *tmpCroc = daqController->GetCroc(crocNo);
		bool avail = false;
		avail = tmpCroc->GetChannelAvailable(i);
		if (avail) {
			try {
				int error = BuildFEBList(i, crocNo, nFEBsPerChain[i]);
				if (error) throw error;
			} catch (int e) {
				std::cout << "Cannot locate all FEB's on CROC " <<
					(daqController->GetCroc(crocNo)->GetCrocAddress()>>16) << 
					" Chain " << i << std::endl;
				acqData.fatalStream() << "Cannot locate all FEB's on CROC " <<
					(daqController->GetCroc(crocNo)->GetCrocAddress()>>16) << 
					" Chain " << i;
				exit(e);	
			}
		}
	}

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
	acqData.debug("     IRQ CONFIG = 0x%04X",daqController->GetCrim(index)->GetInterruptConfig());
	acqData.debug("     IRQ ADDR   = 0x%04X",daqController->GetCrim(index)->GetInterruptsConfigAddress());
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
	// Exract the CROC object and Channel object from the controller 
	// and assign them to a tmp of each type for ease of use.
	croc *tmpCroc = daqController->GetCroc(croc_id);
	channels *tmpChan = daqController->GetCroc(croc_id)->GetChannel(i);

	// This is a dynamic look-up of the FEB's on the channel.
	// Addresses numbers range from 1 to Max and we'll loop
	// over all of them and look for S2M message headers.
	for (int j = 1; j <= nFEBs; j++) { 
		acqData.debugStream() << "    Trying to make FEB " << j << " on chain " << i;
		// Make a "trial" FEB for the current address.
		feb *tmpFEB = tmpChan->MakeTrialFEB(j, numberOfHits, acqAppender); 
		
		// Build an outgoing message to test if an FEB of this address is available on this channel.
		tmpFEB->MakeMessage(); 

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

			// Add the FEB to the list.
			tmpChan->SetFEBs(j, numberOfHits, acqAppender); 

			// Set the FEB available flag.
			tmpChan->SetHasFebs(true);

			// Clean up the memory.
			delete tmpFEB;  
		} else {
			acqData.critStream() << "FEB: " << tmpFEB->GetBoardNumber() << " is NOT available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " 
				<< tmpChan->GetChainNumber();
			std::cout << "\nCRITICAL!  FEB: " << tmpFEB->GetBoardNumber() << " is NOT available on CROC "
				<< (daqController->GetCroc(croc_id)->GetCrocAddress()>>16) << " Chain " 
				<< tmpChan->GetChainNumber() << "\n" << std::endl;
			// Clean up the memory.
			delete tmpFEB; 
			// Return an error, stop!
			return 1;
		}  
	}
#if NEWREADOUT
	tmpChan->VectorizeFEBList();
#endif
	acqData.infoStream() << "Returning from BuildFEBList.";
	return 0;
}


int acquire_data::WriteCROCFastCommand(int id, unsigned char command[])
{
/*! \fn acquire_data::WriteCROCFastCommand(int id, unsigned char command[])
 *  \param int id - the CROC index
 *  \param unsigned char command[] - array containing the fast command to be executed
 *
 * This function writes a message to the CROC fast command register.  Be careful!  Only 
 * certain messages are allowed and only a subset of those will be interpreted.  Please 
 * consult B. Baldin and C. Gingu for details.
 */
#if (DEBUG_FASTCOMMAND)||(DEBUG_COSMICS)
	acqData.debugStream() << "Entering WriteCROCFastCommand for CROC " <<
		(daqController->GetCroc(id)->GetCrocAddress()>>16) << 
		" and " << sizeof(*command)/sizeof(unsigned char) << " command(s): "; 
	for (int i = 0; i<(sizeof(*command)/sizeof(unsigned char)); i++) { 
		acqData.debug("   0x%02X",command[i]);
	}
	//acqData.debug("  Write address is 0x%06X",
	//	daqController->GetCroc(id)->GetFastCommandAddress());
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


int acquire_data::ResetCRIMSequencerLatch(int id)
{
/*! \fn int acquire_data::ResetCRIMSequencerLatch(int id)
 *  \param int id - the CRIM index
 *
 * This function resets the CRIM sequencer latch in cosmic mode to restart the seqeuncer in 
 * internal timing mode.  This only affects CRIMs with v5 firmware.
 */
#if DEBUG_COSMICS
	acqData.debugStream() << "Entering ResetCRIMSequencerLatch for CRIM " <<
		(daqController->GetCrim(id)->GetCrimAddress()>>16);
#endif
	unsigned char message[] = { 0x02, 0x02 };
	try {
#if DEBUG_COSMICS
		acqData.debug(" Trying to write to address: 0x%06X", 
			daqController->GetCrim(id)->GetSequencerResetRegister());
#endif
		int error = daqAcquire->WriteCycle(daqController->handle, 2, message, 
			daqController->GetCrim(id)->GetSequencerResetRegister(),
			daqController->GetAddressModifier(), daqController->GetDataWidth());
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in acquire_data::ResetCRIMSequencerLatch for CRIM " << 
			(daqController->GetCrim(id)->GetCrimAddress()>>16) << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in acquire_data::ResetCRIMSequencerLatch for CRIM " << 
			(daqController->GetCrim(id)->GetCrimAddress()>>16);
		return e;
	}
#if DEBUG_COSMICS
	acqData.debugStream() << "Exiting ResetCRIMSequencerLatch for CRIM " <<
		(daqController->GetCrim(id)->GetCrimAddress()>>16);
#endif
	return 0;
}


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


template <class X> int acquire_data::FillDPM(croc *crocTrial, channels *channelTrial, X *frame, 
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
 *  Returns a status integer (0 for success).
 */
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth DWS      = crocTrial->GetDataWidthSwapped();
	unsigned short dpmPointer;
	unsigned char  status[2];

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
		return e;
	}
	dpmPointer = (unsigned short) (status[0] | (status[1]<<0x08));

	// We have to check and see if the message could exceed the amount of space available 
	// in memory.  If it doesn't, it is safe to write the send-message command and add 
	// a new frame to the DPM.
	if ( (dpmPointer<dpmMax) && ((dpmMax-incoming_length)>incoming_length) ) {
		try {
			int error = SendMessage(frame, crocTrial, channelTrial, true);
			if (error) throw error;
		} catch (int e) {
			std::cout << "      Error sending message in acquire_data::FillDPM for CROC " 
				<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
				(channelTrial->GetChainNumber()) << std::endl;
			std::cout << "      SendMessage Error Level = " << e << std::endl;
			acqData.critStream() << "Error sending message in acquire_data::FillDPM for CROC "
				<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
				(channelTrial->GetChainNumber());
			acqData.critStream() << "->SendMessage Error Level = " << e;
			return e; 
		}
		return 0; 
	}
	acqData.critStream() << "Exiting acquire_data::FillDPM; DPM is full for CROC "
		<< (crocTrial->GetCrocAddress()>>16) << " Chain " <<
		(channelTrial->GetChainNumber());
	return 100;
}


bool acquire_data::TakeAllData(feb *febTrial, channels *channelTrial, croc *crocTrial, 
	event_handler *evt, int thread, et_att_id attach, et_sys_id sys_id, 
	bool readFPGA, int nReadoutADC) 
{
/*! \fn bool acquire_data::TakeAllData(feb *febTrial, channels *channelTrial, croc *crocTrial,
 *		event_handler *evt, int thread, et_att_id  attach, et_sys_id sys_id, 
 *		bool readFPGA, int nReadoutADC)
 *
 *  The main acquisition sequence.  This function organizes all of the incoming and outgoing 
 *  messages to the data acquisition electronics, collects those messages, fills a structure
 *  for future data handling, and sends the data on to the event builder.
 *
 *  This function is used by the "old" readout model (FEB sequential).
 *
 *  \param feb *febTrial  a pointer to the feb being accessed
 *  \param channels *channelTrial  a pointer to the CROC channel which olds the FEB
 *  \param croc *crocTrial  a pointer to the CROC that has the FEB/Channel being accessed
 *  \param event_handler *evt  a pointer to an event_handler structure for data processing
 *  \param int thread   an integer value for the thread executing
 *  \param et_att_id  attach the ET attachemnt to which the data will be sent
 *  \param et_sys_id  sys_id the system ID for ET which will handle the data
 *  \param bool readFPGA a flag that determines whether we read the FPGA programming registers data
 *  \param int nReadoutADC sets the maximum number of ADC frames to read (deepest first)
 *
 *  Returns a status bit - 0 for success.
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
	struct timeval start_time, stop_time;
#endif
#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS
	acqData.debugStream() << "--Entering acquire_data::TakeAllData--";
#endif
#if THREAD_ME
	// Set up some threads for using the event builder.
	boost::thread *eb_threads[3];
#endif

	// Execution Status Vars.
	int success       = 0;
	bool memory_reset = false;
	int hits          = -1;
	// If !READ_ADC, deepestRead > hits-1 always.	
	int deepestRead   = numberOfHits; // 6>ReadHit5, 8>ReadHit7 

	// Fill entries in the event_handler structure for this event -> The sourceID.
	evt->new_event   = false; // We are always processing an existing event with this function!!!
	evt->feb_info[0] = 0;     // We need to sort this out later (link number) -> *Probably* ALWAYS 0.
	evt->feb_info[1] = 0;     // Crate number.  Assigned in minervadaq::main().
	evt->feb_info[2] = (crocTrial->GetCrocAddress()>>16);
	evt->feb_info[3] = channelTrial->GetChainNumber(); 
	evt->feb_info[6] = febTrial->GetFEBNumber();
#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS 
	acqData.debugStream() << "    CROC  : " << evt->feb_info[2];
        acqData.debugStream() << "    CHAIN : " << evt->feb_info[3];
        acqData.debugStream() << "    FEB   : " << evt->feb_info[6];
#endif	
	// Make sure the DPM is reset for taking the FEB INFO Frames.
	memory_reset = ResetDPM(crocTrial, channelTrial);

	// Read all the data.
	try {
		if (!memory_reset) throw memory_reset;

		// Begin reading FEB frame information.
		if (readFPGA) {
#if TIME_ME
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
				return 1; // Failure!
			}
			febTrial->message = new unsigned char [FEB_INFO_SIZE];
			for (int debug_index=0; debug_index<febTrial->GetIncomingMessageLength(); debug_index++) {
				febTrial->message[debug_index] = channelTrial->GetBuffer()[debug_index];
			}
			// DecodeRegisterValues does provide an error check of sorts, but this inefficient...
			try {
				int error = febTrial->DecodeRegisterValues(febTrial->GetIncomingMessageLength());
				if (error) throw error;
			} catch (int e) {
				std::cout << "Error in FPGA Frame in acquire_data::TakeAllData!" << std::endl;
				std::cout << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber() << std::endl;
				acqData.fatalStream() << "Error in FPGA Frame in acquire_data::TakeAllData!";
				acqData.fatalStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
				return 1; // Failure!
			}
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
#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS
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
		} // End if readFPGA

		// Read a discriminator frame.
		// First, decide if the discriminators are on.
		bool disc_set = false;
#if READ_DISC
		disc_set = true;
#endif
		if (disc_set) { 
#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS
			acqData.debugStream() << "--Discriminator Frame";
#endif
			if (!(memory_reset = ResetDPM(crocTrial, channelTrial))) {
				std::cout << "Unable to reset DPM in acquire_data::TakeAllData for DISC readout." << std::endl;
				std::cout << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber() << std::endl;
				acqData.critStream() << "Unable to reset DPM in acquire_data::TakeAllData for DISC readout";
				acqData.critStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
				return 1; // Failure!
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
				acqData.critStream()<< "Error in acquire_data::TakeAllData adding DISC Information to DPM!";
				acqData.critStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
				return 1;
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
#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS
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
		if (hits == -1) hits = 1; // If we did not read the Discriminators.
#if READ_ADC
		// If !READ_ADC, deepestRead > hits-1 always.
		deepestRead = (hits-nReadoutADC) >= 0 ? (hits-nReadoutADC) : 0; 
#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS
		acqData.debugStream() << "--ADC Frames ";
		acqData.debugStream() << " deepestRead   = " << deepestRead;
#endif
#endif		
		for (int i=hits-1; i>=deepestRead; i--) {
			// Set the hit id.  Increment sourceID hit in "reverse" - sourceID hit 0 is earliest in physical time.
			evt->feb_info[8] = (unsigned int)(hits - 1 - i);
#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS
			acqData.debugStream() << " Loop counter  = " << i;
			acqData.debugStream() << "  sourceID hit = " << evt->feb_info[8];
#endif
			// Reset the DPM pointer & clear the status.
			if (!(memory_reset = ResetDPM(crocTrial, channelTrial))) {
				std::cout << "Unable to reset DPM in acquire_data::TakeAllData for ADC readout." << std::endl;
				std::cout << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber() << std::endl;
				acqData.critStream() << "Unable to reset DPM in acquire_data::TakeAllData for ADC readout";
				acqData.critStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
				return 1; // Failure!
			} 
			// Read an ADC block...
			try {
				success = AcquireDeviceData(febTrial->GetADC(i), crocTrial, channelTrial, FEB_HITS_SIZE);
				if (success) throw success;
			} catch (bool e) {
				std::cout << "Error adding ADC Information to the DPM in acquire_data::TakeAllData!" << std::endl;
				acqData.critStream() << "Error adding ADC Information to the DPM in acquire_data::TakeAllData!";
				acqData.critStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " <<
					channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
				return 1; // Faiure!
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
#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS
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
		acqData.critStream() << "The DPM wasn't reset at the start of acquire_data::TakeAllData!";
		acqData.critStream() << " CROC, CHAIN, FEB = " << (crocTrial->GetCrocAddress()>>16) << ", " << 
			channelTrial->GetChainNumber() << ", " << febTrial->GetBoardNumber();
		return 1;
	}

	// Wait for threads to join if nedessary.
#if THREAD_ME
	// Where is eb_threads[1]?
	eb_threads[0]->join();
	eb_threads[2]->join();
#endif 

#if DEBUG_VERBOSE||DEBUG_LIMITEDBANKS
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
	if (dpmPointer==2) reset = true; // Not really enough, should check status register here too...
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
		// This makes no sense if we are coming from acquire_data::FillDPM... hence the singleton flag!
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
		// Investigate using FIFO BLT for FPGA programming frames though...
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
		// Set up a more general status checker?  This is probably okay...
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
 *  Returns a status integer (0 for success?).
 */
#if THREAD_ME
	lock lock_send(send_lock);
#endif
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debugStream() << " Entering acquire_data::AcquireDeviceData...";
	acqData.debugStream() << "  CROC Address:   " << (crocTrial->GetCrocAddress()>>16);
	acqData.debugStream() << "  Chain Number:   " << channelTrial->GetChainNumber();
	acqData.debug("  Device:         0x%X",frame->GetDeviceType());
#endif
	CVAddressModifier AM      = daqController->GetAddressModifier();
	CVDataWidth       DWS     = crocTrial->GetDataWidthSwapped();
	int               success = 0;
	// Try to add this frame's data to the DPM.
	// Reorganize & clean-up the try-catches here...
	try { 
		success = FillDPM(crocTrial, channelTrial, frame, frame->GetIncomingMessageLength(), length);
		if (success) throw success; 
	} catch (int e) {
		std::cout << "Error in acquire_data::AcquireDeviceData for FillDPM!  Error code = " << e << std::endl;
		acqData.critStream() << "Error in acquire_data::AcquireDeviceData for FillDPM!  Error code = " << e;
		acqData.critStream() << "  CROC Address:   " << (crocTrial->GetCrocAddress()>>16);
		acqData.critStream() << "  Chain Number:   " << channelTrial->GetChainNumber();
		acqData.crit("  Device:         0x%X",frame->GetDeviceType());
		return e;
	}
	try {
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
		std::cout << "Error in acquire_data::AcquireDeviceData for GetBlockRAM!  Error code = " << e << std::endl;
		acqData.critStream() << "Error in acquire_data::AcquireDeviceData for GetBlockRAM!  Error code = " << e;
		acqData.critStream() << "  CROC Address:   " << (crocTrial->GetCrocAddress()>>16);
		acqData.critStream() << "  Chain Number:   " << channelTrial->GetChainNumber();
		acqData.crit("  Device:         0x%X",frame->GetDeviceType());
		return 1;
	}
#if (DEBUG_VERBOSE)||(DEBUG_SENDMESSAGE)
	acqData.debugStream() << "   AcquireDeviceData success: " << success;
#endif
	return success;
}


int acquire_data::ResetSequencerControlLatch(int crimID)
{
/*! \fn int acquire_data::ResetSequencerControlLatch(int crimID)
 * Resets the sequencer control latch when the latching mechanism is enabled (V9+ CRIM only).
 *
 * \param int crimID The CRIM we are resetting.
 *
 * Returns a status integer (0 for success).
 */
#if DEBUG_TRIGGER
	acqData.debug("   Entering acquire_data::ResetSequencerControlLatch...");
	acqData.debug("   ->Preparing to address CRIM %d",(daqController->GetCrim(crimID)->GetCrimAddress()>>16));
#endif
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth       DW = daqController->GetDataWidth();
	int error     = -1;
	int errorCode =  1;
	// Reset sequencer control latch.
#if V9CRIM 
	try {
		unsigned char reset_pulse[] = { 0x4, 0x4 };
#if DEBUG_TRIGGER
		acqData.debug("    reset_plse msg = 0x%02X%02X",reset_pulse[1],reset_pulse[0]);
		acqData.debug("    pulse address  = 0x%X",daqController->GetCrim(crimID)->GetSoftCNRSTRegister());
#endif
		error = daqAcquire->WriteCycle(daqController->handle, 2, reset_pulse,
			daqController->GetCrim(crimID)->GetSoftCNRSTRegister(), AM, DW); 
		if (error) throw error;
	} catch (int e) {
		std::cout << 
			"Unable to send the sequencer control latch reset in acquire_data::ResetSequencerControlLatch!" << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << 
			"Unable to send the sequencer control latch reset in acquire_data::ResetSequencerControlLatch!";
		return errorCode;
	}
#endif
	return 0;
}

int acquire_data::TriggerDAQ(unsigned short int triggerBit, int crimID) 
{
/*! \fn int acquire_data::TriggerDAQ(unsigned short int triggerBit, int crimID)
 *
 * Sets up the acquisition trigger indexed by parameter triggerBit on CRIm with index crimID.
 *
 * Currently, we have the following triggers defined as enumerated types in the DAQ Header (v8):
 *  Note the trigger does not depend on CRIM timing mode explicity, but there is occasionally an 
 *  implicit dependence (e.g., NuMI can only run in CRIM MTM mode).
 * UnknownTrigger  = 0x0000,
 * Pedestal        = 0x0001,
 * LightInjection  = 0x0002,
 * ChargeInjection = 0x0004,
 * Cosmic          = 0x0008,
 * NuMI            = 0x0010,
 * MTBFMuon        = 0x0020,
 * MTBFBeam        = 0x0040,
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
				acqData.critStream() << "Unable to set the pulse delay register in acquire_data::TriggerDAQ!";
				return errorCode;
			}
#if DEBUG_TRIGGER
			acqData.debugStream() << "    ->Sent Sequencer Init. Signal!";
#endif
			break;
		// The "Cosmic" triggers are initiated via an external signal.
		case Cosmic:
		case MTBFMuon:
		case MTBFBeam:
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
	int success = 0;
#if DEBUG_IRQ
	acqData.debugStream() << "  Entering acquire_data::WaitOnIRQ: IRQLevel = " << daqController->GetCrim()->GetIRQLevel();
#endif
// Note, we have not exercised asserting interrrupts very thoroughly.  Expect trouble if you use this!
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
		acqData.critStream() << "The IRQ Wait probably timed-out..." << e;  
		return e;
	}
#endif
// endif - ASSERT_INTERRUPT

#if POLL_INTERRUPT
#if DEBUG_IRQ
	acqData.debugStream() << "  Polling Interrupt!";
	int intcounter = 0;
#endif
	// Wait length vars... (don't want to spend forever waiting around).
	unsigned long long startTime, nowTime;
	struct timeval waitstart, waitnow;
	gettimeofday(&waitstart, NULL);
	startTime = (unsigned long long)(waitstart.tv_sec);
	// VME manip.
	unsigned short interrupt_status = 0;
	unsigned short iline = (unsigned short)daqController->GetCrim()->GetIRQLine();
	unsigned char crim_send[2];
#if DEBUG_IRQ
	acqData.debugStream() << "  Interrupt line = " << iline;
#endif

	while ( !( interrupt_status & iline ) ) {
		try {
			crim_send[0] = crim_send[1] = 0;
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
			gettimeofday(&waitnow, NULL);
			nowTime = (unsigned long long)(waitnow.tv_sec);
			interrupt_status =  (crim_send[0]|(crim_send[1]<<0x08));
			if ( (nowTime-startTime) > timeOutSec) { 
				//std::cout << "Waiting... " << (nowTime-startTime) << std::endl;
				//std::cout << " Interrupt status = " << interrupt_status << std::endl; 
				success = 1;
				break; 
			}
		} catch (int e) {
			std::cout << "Error getting crim interrupt status in acquire_data::WaitOnIRQ!" << std::endl;
			daqController->ReportError(e);
			acqData.critStream() << "Error getting crim interrupt status in acquire_data::WaitOnIRQ!";
			return e;
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
		acqData.critStream() << "Error clearing crim interrupts in acquire_data::WaitOnIRQ!";
		return e;
	}
#endif
// endif - POLL_INTERRUPT
	return success;
}


int acquire_data::AcknowledgeIRQ() 
{
/*! \fn void acquire_data::AcknowledgeIRQ() 
 *
 * A function which acknowledges and resets the interrupt handler.
 *
 * Returns a status integer (0 for success).
 */
// AcknowledgeIRQ() needs a lot of try-catch polishing if we start using it...
#if DEBUG_IRQ
	acqData.debugStream() << "  Entering acquire_data::AcknowledgeIRQ...";
#endif
	CVDataWidth DW = daqController->GetDataWidth();
	int error;
	//unused//int errorCode = 3;
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
#if DEBUG_IRQ
			CVIRQLevels irqLevel = daqController->GetCrim()->GetIRQLevel();
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


bool acquire_data::ContactEventBuilder(event_handler *evt, int thread, 
	et_att_id attach, et_sys_id sys_id) 
{
/*! \fn void acquire_data::ContactEventBuilder(event_handler *evt, int thread, et_att_id attach,
 *                                        et_sys_id sys_id)
 *
 *  A function which sends raw data to the event builder via Event Transfer for processing into the 
 *  event model and final output file.  
 *
 *  \param event_handler *evt a pointer to the event structure holding raw data
 *  \param int thread an integer thread number, not used?
 *  \param et_att_id  attach the ET attachment to which this data will be sent
 *  \param et_sys_id  sys_id the ET system id for data handling
 */
	{ // Debug statements
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
		int status = et_event_new(sys_id, attach, &pe, ET_SLEEP, NULL, 
			sizeof(struct event_handler)); // Get an event.
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
			return false;
		} 
		// Put data into the event.
		if (status == ET_OK) {
#if DEBUG_ET_REPORT_EVENT
			acqData.debugStream() << "    Putting Event on ET System:";
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
		} // end if status == ET_OK

		// Put the event back into the ET system.
		status = et_event_put(sys_id, attach, pe); // Put the event away.
		if (status != ET_OK) {
			printf("et_producer: put error in acquire_data::ContactEventBuilder!\n");
			acqData.fatal("et_producer: put error in acquire_data::ContactEventBuilder!");
			return false;
		} 
		if (!et_alive(sys_id)) {
			et_wait_for_alive(sys_id);
		}
		break; // Done processing the event. 
	} // while alive 

#if DEBUG_ET_REPORT_EVENT
	acqData.debugStream() << "  Exiting acquire_data::ContactEventBuilder...";
#endif

	// report to calling method that data transfer went ok.
	return true;

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


void acquire_data::InitializeReadoutObjects(std::list<readoutObject*> *objectList)
{
/*! \fn InitializeReadoutObjects(std::list<readoutObject*> *objectList) 
 *
 * Initialize list of readoutObjects (find all FE channels that carry 
 * each FEBID in the list.
 *
 * \param std::list<readoutObject*> *objectList the list of readoutObjects built elsewhere.
 */
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "Initializing readoutObject List.";
	acqData.debugStream() << "********************************";
#endif
	std::list<readoutObject*>::iterator rop = objectList->begin();
	for (rop = objectList->begin(); rop != objectList->end(); rop++) {
		int febid = (*rop)->getFebID();
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
		acqData.debugStream() << "readoutObj feb id = " << febid << ", starting loop over CROCs...";
#endif
		std::vector<croc*> *crocVector     = daqController->GetCrocVector();
		std::vector<croc*>::iterator crocp = crocVector->begin();
		for (crocp = crocVector->begin(); crocp != crocVector->end(); crocp++) {
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
			acqData.debugStream() << " CROC Addr = " << ((*crocp)->GetCrocAddress()>>16)
				<< ", starting loop over Chains...";
#endif
			std::list<channels*> *chanList = (*crocp)->GetChannelsList();
			std::list<channels*>::iterator chp;
			for (chp = chanList->begin(); chp != chanList->end(); chp++) {
				bool addChain = false;
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
				acqData.debugStream() << "  Chain id = " << (*chp)->GetChainNumber() <<
					", starting loop over FEB's on the chain...";
#endif
				std::list<feb*> *febList = (*chp)->GetFebList();
				std::list<feb*>::iterator fp;
				for (fp = febList->begin(); fp != febList->end(); fp++) {
					int innerfebid = (int)(*fp)->GetBoardNumber();
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
					acqData.debugStream() << "   Inner febid = " << innerfebid;
#endif
					if (innerfebid == febid) { addChain = true; }
				}
				if (addChain) {
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
					acqData.debugStream() << "     Found a match on this chain!";
#endif
					(*rop)->addData(*chp,0); // init with zero hits
				} // end if addChain
			} // end for loop over channels
		} // end for loop over crocs
	} // end for loop over readoutObjects
} // end InitializeReadoutObjects


void acquire_data::DisplayReadoutObjects(std::list<readoutObject*> *objectList)
{
/*! \fn DisplayReadoutObjects(std::list<readoutObject*> *objectList)
 *
 * Display the contents of a list of readoutObjects.
 *
 * \param std::list<readoutObject*> *objectList the list to be explicated.
 */
	acqData.infoStream() << "readoutObject List Contents:";
	acqData.infoStream() << ".....................................";
	std::list<readoutObject*>::iterator rop = objectList->begin();
	for (rop = objectList->begin(); rop != objectList->end(); rop++) {
		int febid = (*rop)->getFebID();
		acqData.infoStream() << "readoutObject febid = " << febid;
		acqData.infoStream() << " dataLength = " << (*rop)->getDataLength();
		for (int i=0; i<(*rop)->getDataLength(); i++) {
			unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
			unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
			acqData.infoStream() << "  CROC = " << crocAddr << ", ChainNum = " 
				<< (*rop)->getChannel(i)->GetChainNumber()
				<< ", Hits on the channel (Original) = " << (*rop)->getHitsPerChannel(i)
				<< " (" << (*rop)->getOrigHitsPerChannel(i) << ")";
		}
	}
	acqData.infoStream() << ".....................................";
} // end DisplayReadoutObjects


void acquire_data::SendClearAndReset(channels *theChain)
{
/*! \fn SendClearAndReset(channels *theChain)
 * Send a Clear and Reset to a CROC FE Channel.
 *
 * \param channels *theChain the FE channel (referenced by Chain because of likely indexing choices).
 */
	int crocAddress = ( theChain->GetClearStatusAddress() & 0xFFFF0000 )>>16;
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "--> Entering SendClearAndReset for CROC " << crocAddress <<
		" Chain " << theChain->GetChainNumber();
	acqData.debug("  Clear Status Address = 0x%X",theChain->GetClearStatusAddress());
#endif
	CVAddressModifier    AM  = daqController->GetAddressModifier();
	CVDataWidth          DW  = daqController->GetDataWidth();
	unsigned char message[2] = {0x0A, 0x0A}; // 0202 + 0808 for clear status AND reset.

	// Clear the status & reset the pointer.
	try {
		int success = daqAcquire->WriteCycle(daqController->handle, 2, message,
			theChain->GetClearStatusAddress(), AM, DW);
		if (success) throw success;
	} catch (int e) {
		daqController->ReportError(e);
		std::cout << "VME Error in SendClearAndReset!  Cannot write to the status register!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "VME Error in SendClearAndReset!  Cannot write to the status register!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		exit(e);
	}
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)      
	acqData.debugStream() << "Executed SendClearAndReset for CROC " << crocAddress <<
		" Chain " << theChain->GetChainNumber();
#endif
} // end SendClearAndReset


int acquire_data::ReadStatus(channels *theChain, bool receiveCheck)
{
/*! \fn ReadStatus(channels *theChain, bool receiveCheck)
 *
 * Read the status register on a CROC FE Channel.
 *
 * \param channels *theChain the FE channel (referenced by Chain because of likely indexing choices).
 * \param bool receiveCheck flag to determine whether we should demand message received as part of the 
 *   criteria for success.
 */
	int crocAddress = ( theChain->GetClearStatusAddress() & 0xFFFF0000 )>>16;
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)    
	acqData.debugStream() << "--> Entering ReadStatus for CROC " << crocAddress <<
		" Chain " << (theChain->GetChainNumber());
	acqData.debug("  Status Address = 0x%X",theChain->GetStatusAddress());
#endif
	CVAddressModifier AM = daqController->GetAddressModifier();
	CVDataWidth DW       = daqController->GetDataWidth();

	unsigned short MessageReceivedCheck = 0xFFFF;
	if (receiveCheck) MessageReceivedCheck = MessageReceived;
	unsigned char statusBytes[] = {0x0,0x0};
	unsigned short status;

	do {
		try {
			int error = daqAcquire->ReadCycle(daqController->handle, statusBytes,
				theChain->GetStatusAddress(), AM, DW);
			if (error) throw error;
		} catch (int e) {
			daqController->ReportError(e);
			std::cout << "VME Error in ReadStatus while reading the status register!" << std::endl;
			std::cout << "  Error on CROC " << crocAddress <<
				" Chain " << theChain->GetChainNumber() << std::endl;
			acqData.critStream() << "VME Error in ReadStatus while reading the status register!";
			acqData.critStream() << "  Error on CROC " << crocAddress <<
				" Chain " << theChain->GetChainNumber();
			return e;
		}
		status = (unsigned short)( statusBytes[0] | statusBytes[1]<<0x08 );
		theChain->SetChannelStatus(status);
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)     
		acqData.debug("     Read Status - Chain %d status = 0x%04X",
			theChain->GetChainNumber(),status);
#endif
	} while ( !(status & MessageReceivedCheck) && !(status & CRCError) && !(status & TimeoutError)
		&& (status & RFPresent) && (status & SerializerSynch) && (status & DeserializerLock)
		&& (status & PLLLocked) );

	// Check for errors & handle them.
	if ( (status & CRCError) ) {
		std::cout << "CRC Error in ReadStatus!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "CRC Error in ReadStatus!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-10);
	}
	if ( (status & TimeoutError) ) {
		std::cout << "Timeout Error in acquire_data::SendMessage!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "Timeout Error in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-11);
	}
	if ( (status & FIFONotEmpty) ) {
		std::cout << "FIFO Not Empty Error in acquire_data::SendMessage!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "FIFO Not Empty Error in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
	}
	if ( (status & FIFOFull) ) {
		std::cout << "FIFO Full Error in acquire_data::SendMessage!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "FIFO Full Error in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
	}
	if ( (status & DPMFull) ) {
		std::cout << "DPM Full Error in acquire_data::SendMessage!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "DPM Full Error in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
	}
	if ( !(status & RFPresent) ) {
		std::cout << "No RF Error in acquire_data::SendMessage!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "No RF Error in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-12);
	}
	if ( !(status & SerializerSynch) ) {
		std::cout << "No SerializerSynch Error in acquire_data::SendMessage!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "No SerializerSynch Error in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-13);
	}
	if ( !(status & DeserializerLock) ) {
		std::cout << "DeserializerLock Error in acquire_data::SendMessage!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "DeserializerLock Error in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-14);
	}
	if ( !(status & PLLLocked) ) {
		std::cout << "PLLLock Error in acquire_data::SendMessage!" << std::endl;
		std::cout << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber() << std::endl;
		acqData.critStream() << "PLLLock Error in acquire_data::SendMessage!";
		acqData.critStream() << "  Error on CROC " << crocAddress <<
			" Chain " << theChain->GetChainNumber();
		return (-15);
	}
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "Executed ReadStatus for CROC " << crocAddress <<
		" Chain " << theChain->GetChainNumber();
#endif
	return 0; // Success!
}


template <class X> void acquire_data::SendFrameData(X *device, channels *theChannel)
{
/*! \fn
 *
 * Send messages to a generic device using normal write cycle -> write the outgoing message from 
 * the device to the FE Channel FIFO & send the message.
 * \param X *device the frame (template)
 * \param channels *theChannel the CROC FE Channel for the board housing the device.
 */
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "   -->Entering SendFrameData.";
#endif
	CVAddressModifier AM = cvA24_U_DATA;  // *Default* Controller Address Modifier
	CVDataWidth DW       = cvD16;         // *Default* Controller Data Width
	CVDataWidth DWS      = cvD16_swapped; // *Always* CROC DataWidthSwapped
	unsigned char send_message[2] = {0x01, 0x01};

	// Write the message to the channel FIFO.
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, device->GetOutgoingMessageLength(),
			device->GetOutgoingMessage(), theChannel->GetFIFOAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error in SendFrameData while writing to the FIFO!" << std::endl;
		std::cout << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber() << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Error in SendFrameData while writing to the FIFO!";
		acqData.fatalStream() << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		// Hard exit used for thread "friendliness" later...
		exit(e);
	}
	// Send the message.
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, 2, send_message,
			theChannel->GetSendMessageAddress(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error in SendFrameData while writing to the SendMessage address!" << std::endl;
		std::cout << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber() << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Error in SendFrameData while writing to the SendMessage address!";
		acqData.fatalStream() << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		// Hard exit used for thread "friendliness" later...
		exit(e);
	}
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "   Finished SendFrameData!";
#endif
}


template <class X> void acquire_data::SendFrameDataFIFOBLT(X *device, channels *theChannel)
{
/*! \fn template <class X> void SendFrameDataFIFOBLT(X *device, channels *theChannel)
 *
 * Send messages to a generic device using FIFO BLT write cycle -> write the outgoing message to the 
 * CROC FIFO & send the message (sensible for the long FPGA programming frames only).
 *
 * Actually, this doesn't really work at all with our electronics for some subtle reasons.  It will 
 * write, but the readback is messed up.  Best to avoid using this function until someday it is removed...
 *
 * \param X *device the frame (template)
 * \param channels *theChannel the CROC FE Channel for the board housing the device.
 */     
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "   -->Entering SendFrameDataFIFOBLT.";
#endif
	CVAddressModifier AM = cvA24_U_DATA;  // *Default* Controller Address Modifier
	CVDataWidth DW       = cvD16;         // *Default* Controller Data Width
	CVDataWidth DWS      = cvD16_swapped; // *Always* CROC DataWidthSwapped
	unsigned char send_message[2] = {0x01, 0x01};

	// Write the message to the channel FIFO using BLT.
	try {
		int error = daqAcquire->WriteFIFOBLT(daqController->handle, device->GetOutgoingMessageLength(),
			device->GetOutgoingMessage(), theChannel->GetFIFOAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error in SendFrameDataFIFOBLT while writing to the FIFO!" << std::endl;
		std::cout << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber() << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Error in SendFrameDataFIFOBLT while writing to the FIFO!";
		acqData.fatalStream() << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		// Hard exit used for thread "friendliness" later...
		exit(e);
	}
	// Send the message.
	try {
		int error = daqAcquire->WriteCycle(daqController->handle, 2, send_message,
			theChannel->GetSendMessageAddress(), AM, DW);
		if (error) throw error;
	} catch (int e) {
		std::cout << " Error in SendFrameDataFIFOBLT while writing to the SendMessage address!" << std::endl;
		std::cout << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber() << std::endl;
		daqController->ReportError(e);
		acqData.fatalStream() << "Error in SendFrameDataFIFOBLT while writing to the SendMessage address!";
		acqData.fatalStream() << "  Error on CROC " << ((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		// Hard exit used for thread "friendliness" later...
		exit(e);
	}
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "   Finished SendFrameDataFIFOBLT!";
#endif
}


template <class X> int acquire_data::RecvFrameData(X *device, channels *theChannel)
{
/*! \fn template <class X> int acquire_data::RecvFrameData(X *device, channels *theChannel)
 *
 * Receive messages for a generic device -> read DPM pointer, read BLT, and store data in the *device* buffer.
 * Because we use the device buffer here, this function should be used primarily for debugging and for 
 * building the FEB list.  For standard acquisition, use acquire_data::RecvFrameData(channels *theChannel).
 *
 * \param X *device the frame (template)
 * \param channels *theChannel the CROC FE Channel for the board housing the device.
 */
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "   -->Entering RecvFrameData for devices.";
#endif
	CVAddressModifier AM     = cvA24_U_DATA;  // *Default* Controller Address Modifier
	CVAddressModifier AM_BLT = cvA24_U_BLT;   // *Always* Channel Address Modifier
	CVDataWidth DWS          = cvD16_swapped; // *Always* CROC DataWidthSwapped
	unsigned short dpmPointer;
	unsigned char status[] = {0x0,0x0};

	try {
		int error = daqAcquire->ReadCycle(daqController->handle, status,
			theChannel->GetDPMPointerAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in RecvFrameData for devices!  Cannot read the status register!" << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in RecvFrameData for devices!  Cannot read the status register!";
		return e;
	}
	dpmPointer = (unsigned short) (status[0] | status[1]<<0x08);
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "    RecvFrameData DPM Pointer: " << dpmPointer;
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
			theChannel->GetDPMAddress(), AM_BLT, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in RecvFrameData for devices!  Cannot ReadBLT!" << std::endl;
		std::cout << "  Error on CROC " <<
			((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber() << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in RecvFrameData for devices!  Cannot ReadBLT!";
		acqData.critStream() << "  Error on CROC " <<
			((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		return e;
	}

	// Check Device Header for error flags (S2M, etc.)
	bool success = device->CheckForErrors();
	if (success) {
		return success; // There were errors.
	}
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "   Finished RecvFrameData for devices!  Returning " << success;
#endif
	return ((int)success);
}


int acquire_data::RecvFrameData(channels *theChannel)
{
/*! \fn int acquire_data::RecvFrameData(channels *theChannel)
 *
 * Receive messages from a CROC FE Channel DPM -> read DPM pointer, read the data via BLT, and store it in the
 * *channel* buffer.
 *
 * \param channels *theChannel the CROC FE Channel for the board housing the device.
 */
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "   -->Entering RecvFrameData for a channel.";
#endif
	CVAddressModifier AM     = cvA24_U_DATA;  // *Default* Controller Address Modifier
	CVAddressModifier AM_BLT = cvA24_U_BLT;   // *Always* Channel Address Modifier
	CVDataWidth DWS          = cvD16_swapped; // *Always* CROC DataWidthSwapped
	unsigned short dpmPointer;
	unsigned char status[] = {0x0,0x0};

	try {
		int error = daqAcquire->ReadCycle(daqController->handle, status,
			theChannel->GetDPMPointerAddress(), AM, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in RecvFrameData for a channel!  Cannot read the status register!" << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in RecvFrameData for a channel!  Cannot read the status register!";
		return e;
	}
	dpmPointer = (unsigned short) (status[0] | status[1]<<0x08);
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "    RecvFrameData DPM Pointer: " << dpmPointer;
#endif
	theChannel->SetDPMPointer(dpmPointer);
	// We must read an even number of bytes.
	int dataLength = 1;
	if (dpmPointer%2) {
		dataLength = dpmPointer + 1;
	} else {
		dataLength = dpmPointer;
	}
	if (dataLength%2) {
		acqData.critStream() << "Error in RecvFrameData for a channel!  Invalid DPM pointer length!";
		return 1;
	}
	DPMData = new unsigned char [dataLength];
	try {
		int error = daqAcquire->ReadBLT(daqController->handle, DPMData, dpmPointer,
			theChannel->GetDPMAddress(), AM_BLT, DWS);
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in RecvFrameData for a channel!  Cannot ReadBLT!" << std::endl;
		std::cout << "  Error on CROC " <<
			((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber() << std::endl;
		daqController->ReportError(e);
		acqData.critStream() << "Error in RecvFrameData for a channel!  Cannot ReadBLT!";
		acqData.critStream() << "  Error on CROC " <<
			((theChannel->GetClearStatusAddress()&0xFFFF0000)>>16) <<
			" Chain " << theChannel->GetChainNumber();
		return e;
	}
	theChannel->SetBuffer(DPMData);

	// Clean-up and return.
	delete [] DPMData;
#if (DEBUG_VERBOSE)&&(DEBUG_NEWREADOUT)
	acqData.debugStream() << "   Finished RecvFrameData for a channel!  Returning.";
#endif
	// Check for errors embedded in the data.
	// Note that this is really assuming only one frame of data is in the DPM at a time!
	return theChannel->CheckHeaderErrors(dataLength);
}


void acquire_data::FillEventStructure(event_handler *evt, int bank, channels *theChannel)
{
/*! \fn void acquire_data::FillEventStructure(event_handler *evt, int bank, channels *theChannel)
 *
 * Take data from the channel buffer and put it into the raw event structure for data processing by 
 * the event builder.
 *
 * \param event_handler *evt a pointer to the event handler structure
 * \param int bank an index for this data bank type
 * \param channels *theChannel a pointer to the croc channel object being processed.
 */
#if DEBUG_NEWREADOUT
	acqData.debugStream() << "  Entering acquire_data::FillEventStructure with bank type " << bank
		<< " and message length " << theChannel->GetDPMPointer();
#endif
	// Build sourceID
	evt->feb_info[4] = bank;  // 0==ADC, 1==TDC, 2==FPGA, 3==DAQ Header, 4==TriP-T
	const unsigned int buffLength = theChannel->GetDPMPointer(); // Data + Frame CRC;
	const unsigned int dataLength = buffLength - 2; 
	evt->feb_info[5] = dataLength;
#if DEBUG_NEWREADOUT
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
		evt->event_data[i] = theChannel->GetBuffer()[i];
	}
#if DEBUG_NEWREADOUT
	acqData.debugStream() << "   Got Data";
	acqData.debugStream() << "    Embedded (Data) Length      = " << (int)evt->event_data[0] +
		(int)(evt->event_data[1]<<8);
	acqData.debugStream() << "    theChannel->GetDPMPointer() = " << theChannel->GetDPMPointer();
	acqData.debugStream() << "    Total buffer length         = " << buffLength;
#if SHOW_DATABYTES
	for (unsigned int index = 0; index < buffLength; index++) {
		acqData.debug("     FillStructure data byte %02d = 0x%02X", index,
			(unsigned int)evt->event_data[index]);
	}
#endif
#endif 
}


int acquire_data::WriteAllData(event_handler *evt, et_att_id attach, et_sys_id sys_id, 
        std::list<readoutObject*> *readoutObjects, const int allowedTime, 
	const bool readFPGA, const int nReadoutADC, const bool zeroSuppress)
{
/*! \fn int acquire_data::WriteAllData(event_handler *evt, et_att_id attach, et_sys_id sys_id, 
 *		std::list<readoutObject*> *readoutObjects, const int allowedTime, 
 *		const bool readFPGA, const int nReadoutADC)
 *
 * Run the full acquisition sequence for a gate, write the data to file. 
 *
 *  \param *evt, a pointer to the event_handler structure containing information
 *		about the data being handled.
 *  \param attach, the ET attachemnt to which data will be stored
 *  \param sys_id, the ET system handle
 *  \param std::list<readoutObject*> *readoutObjects, a pointer to the list of hardware to be read out. 
 *  \param const int allowedTime, allowed readout time in microseconds 
 *  \param const bool readFPGA, sets whether we read the FPGA's
 *  \param const int nReadoutADC, sets how many max frames we will read
 *  \param const bool zeroSuppress, zero suppression flag (false == read end of gate, true == suppress).
 */
#if DEBUG_NEWREADOUT
	acqData.debugStream() << "Entering acquire_data::WriteAllData.";
	acqData.debugStream() << "++++++++++++++++++++++++++++++++++++";
	DisplayReadoutObjects(readoutObjects);
#endif
	struct timeval readstart, readend;
	unsigned long long startReadout, stopReadout;
	int readoutTimeDiff;  // For timing monitoring.  

	// Update startReadout for the next gate...
	gettimeofday(&readstart, NULL);
	startReadout = (unsigned long long)(readstart.tv_sec*1000000) + (unsigned long long)(readstart.tv_usec);

	bool continueReadout = true;
	bool readDisc        = true; // Always leave this on...
	bool readADC         = true;
	if (!nReadoutADC) { readADC = false; }

	// Fill entries in the event_handler structure for this event -> The sourceID.
	evt->new_event   = false; // We are always processing an existing event with this function!!!
	evt->feb_info[0] = 0;     // Link Number. -> *Probably* ALWAYS 0.
	evt->feb_info[1] = daqController->GetID(); // Crate ID

	int baseRead = 0;
	if (zeroSuppress) baseRead = 1;

#if PREVIEWHIT
	// Loop over readout objects, if febid==1, read the status for the channel and get the vector of data for 
	// boards with hits:
	//	PREVIEW_DATA(24 bits) = HVActual(16 bits) + TRIP2_HITCNT(4 bits) + TRIP0_HITCNT(4 bits)
	// Note that the board address is not part of the message, so we assume for many boards they are stacked 
	// in order:
	//	(24 bits - FEB1)(24 bits - FEB2)(24 bits - FEB3)(etc.)
	// Best understood as a buffer of bytes - 2 bytes for HV, 1 byte for hits.
#endif	
	// Do an "FPGA read".
	// First, send a read frame to each channel that has an FEB with the right index.
	// Then, after sending a frame to every channel, read each of them in turn for data.
	if (readFPGA && continueReadout) {
#if DEBUG_NEWREADOUT
		acqData.debugStream() << "==================";
		acqData.debugStream() << "Read the FPGA's...";
		acqData.debugStream() << "==================";
#endif
		std::list<readoutObject*>::iterator rop = readoutObjects->begin();
		while (rop != readoutObjects->end() && continueReadout) {
			int febid    = (*rop)->getFebID();
			int febindex = febid - 1;
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "-> Top of readoutObject loop.";
			acqData.debugStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
			acqData.debugStream() << "feb id    = " << febid;
#endif
			// Pointer for the FEB's on each channel.  Be careful about deleting!   
			feb *tmpFEB;

			// Clear and reset all channels that have an FEB with id febid first.
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Do the clear and resets for all channels with FEB's of the right id.";
#endif
			for (int i=0; i<(*rop)->getDataLength(); i++) {
				SendClearAndReset((*rop)->getChannel(i));
				try {
					int error = ReadStatus((*rop)->getChannel(i), doNotCheckForMessRecvd); 
					if (error) throw error; 
				} catch (int e) { 
					unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
					unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
					acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
					acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber();
					return e; // Error, stop!
				}
			} // end loop over data in readout object for send clear and reset and check status

			// Send an FPGA read frame request to each channel with an FEB with id febid.
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Send the read FPGA frame requests to all channels with FEB's of the right id.";
#endif
			for (int i=0; i<(*rop)->getDataLength(); i++) {
				// Make a pointer to the FEB on the channel with board number febid
				tmpFEB = (*rop)->getChannel(i)->GetFebVector(febindex);
				int brdnum = tmpFEB->GetBoardNumber();
				if (brdnum!=febid) { acqData.fatalStream() << "Major error!"; exit(1); }
#if DEBUG_NEWREADOUT
				unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
				unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
				acqData.debugStream() << "  CROC = " << crocAddr << ", Chain Number = " << 
					(*rop)->getChannel(i)->GetChainNumber() << ", FEB = " << brdnum;
#endif
				// Compose an FPGA read frame.
#if V90FIRMWARE
				tmpFEB->MakeShortMessage();
#else
				Devices dev     = FPGA;
				Broadcasts b    = None;
				Directions d    = MasterToSlave;
				FPGAFunctions f = Read;
				tmpFEB->MakeDeviceFrameTransmit(dev,b,d,f,(unsigned int)tmpFEB->GetBoardNumber());
				tmpFEB->MakeMessage();
#endif
				// Send the message & delete the outgoingMessage.
				SendFrameData(tmpFEB, (*rop)->getChannel(i));
				tmpFEB->DeleteOutgoingMessage();
				tmpFEB = 0;
			} // end loop over data in readout object for send read frame

			// Check the status for each channel to be sure the message was sent and recv'd.
			// There should only be one frame of data (from the FEB's in the loop above).
			// Read the data & decalre it to ET.
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Check the status to be sure the message was sent and recv'd.  If so, read the data & decalre it.";
#endif
			for (int i=0; i<(*rop)->getDataLength(); i++) {
				unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
				unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
				try {
					int error = ReadStatus((*rop)->getChannel(i), checkForMessRecvd); 
					if (error) throw error; 
				} catch (int e) { 
					acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
					acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber();
					return e; // Error, stop!
				}
				// Make a pointer to the FEB on the channel with board number febid
				tmpFEB = (*rop)->getChannel(i)->GetFebVector(febindex);
				int brdnum = tmpFEB->GetBoardNumber();
				if (brdnum!=febid) { acqData.fatalStream() << "Major error!"; exit(1); }
#if DEBUG_NEWREADOUT
				acqData.debugStream() << "  CROC = " << crocAddr << ", Chain Number = " << 
					(*rop)->getChannel(i)->GetChainNumber() << ", FEB = " << brdnum;
#endif
				// Read the DPM.  
				try {
					int error = RecvFrameData((*rop)->getChannel(i));
					if (error) throw error; 
				} catch (int e) { 
					acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
					acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber();
					return e; // Error, stop!
				}
				// Fiddle with evt data.
				evt->feb_info[2] = crocAddr;
				evt->feb_info[3] = (*rop)->getChannel(i)->GetChainNumber();
				evt->feb_info[6] = brdnum;
				evt->feb_info[7] = firmwareVersion; // We don't parse the FPGA's anymore in the DAQ... (int)tmpFEB->GetFirmwareVersion();
				// FillEventStructure here.  FES reads from the *channel's* buffer, not the frame's!
				FillEventStructure(evt, 2, (*rop)->getChannel(i));
				// ContactEventBuilder here.
				ContactEventBuilder(evt, (int)0, attach, sys_id); 
				// Cleanup...
				(*rop)->getChannel(i)->DeleteBuffer();
				tmpFEB = 0;
			} // end loop over data for reading the DPM

			// Increment the readoutObject pointer.
			rop++;
			// Check readout time - are we okay?
			gettimeofday(&readend, NULL);
			stopReadout = (unsigned long long)(readend.tv_sec*1000000) + (unsigned long long)(readend.tv_usec);
			readoutTimeDiff = (int)stopReadout - (int)startReadout;
			if (readoutTimeDiff > allowedTime) { continueReadout = false; }
		} // end while loop over readout objects
	} // end if readFPGA

	// Do a "Discr read".  Loop over FEB ID's (readoutObjects) a while loop.
	// First, send a read frame to each channel that has an FEB with the right index.
	// Then, after sending a frame to every channel, read each of them in turn for data.
	if (readDisc && continueReadout) {
#if DEBUG_NEWREADOUT
		acqData.debugStream() << "===================";
		acqData.debugStream() << "Read the Discr's...";
		acqData.debugStream() << "===================";
#endif
		std::list<readoutObject*>::iterator rop = readoutObjects->begin();
		while (rop != readoutObjects->end() && continueReadout) {
			int febid    = (*rop)->getFebID();
			int febindex = febid - 1;
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "-> Top of readoutObject loop.";
			acqData.debugStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
			acqData.debugStream() << "feb id    = " << febid;
#endif
			// Pointer for the FEB's on each channel.  Be careful about deleting!   
			feb *tmpFEB;

			// Clear and reset all channels that have an FEB with id febid first.
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Do the clear and resets for all channels with FEB's of the right id.";
#endif
			for (int i=0; i<(*rop)->getDataLength(); i++) {
				SendClearAndReset((*rop)->getChannel(i));
				try {
					int error = ReadStatus((*rop)->getChannel(i), doNotCheckForMessRecvd); 
					if (error) throw error; 
				} catch (int e) { 
					unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
					unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
					acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
					acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber();
					return e; // Error, stop!
				}
			} // end loop over data in readout object for send clear and reset, check status

			// Send a Discr read frame request to each channel with an FEB with id febid.
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Send the read Discr frame requests to all channels with FEB's of the right id.";
#endif
			for (int i=0; i<(*rop)->getDataLength(); i++) {
				// Make a pointer to the FEB on the channel with board number febid
				tmpFEB  = (*rop)->getChannel(i)->GetFebVector(febindex);
				int brdnum = tmpFEB->GetBoardNumber();
				if (brdnum!=febid) { acqData.fatalStream() << "Major error!"; exit(1); }
#if DEBUG_NEWREADOUT
				unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
				unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
				acqData.debugStream() << "  CROC = " << crocAddr << ", Chain Number = " << 
					(*rop)->getChannel(i)->GetChainNumber() << ", FEB = " << brdnum;
#endif
				// Discr. frame built correctly in class constructor (message deleted in destructor)
				// Send the message.
				SendFrameData(tmpFEB->GetDisc(), (*rop)->getChannel(i));
				tmpFEB  = 0;
			} // end loop over data in readout object for send read frame

			// Check the status for each channel to be sure the message was sent and recv'd.
			// There should only be one frame of data (from the FEB's in the loop above).
			// Read the data & parse it for the number of hits.  Set the appropriate hitsPerChannel value. 
			// Decalre it to ET.
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Check the status to be sure the message was sent and recv'd.  If so, read the data & decalre it.";
#endif
			for (int i=0; i<(*rop)->getDataLength(); i++) {
				unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
				unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
				try {
					int error = ReadStatus((*rop)->getChannel(i), checkForMessRecvd); 
					if (error) throw error; 
				} catch (int e) { 
					acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
					acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber();
					return e; // Error, stop!
				}
				// Make a pointer to the FEB on the channel with board number febid
				tmpFEB = (*rop)->getChannel(i)->GetFebVector(febindex);
				int brdnum = tmpFEB->GetBoardNumber();
				if (brdnum!=febid) { acqData.fatalStream() << "Major error!"; exit(1); }
#if DEBUG_NEWREADOUT
				acqData.debugStream() << "  CROC = " << crocAddr << ", Chain Number = " << 
					(*rop)->getChannel(i)->GetChainNumber() << ", FEB = " << brdnum;
#endif
				// Read the DPM.  
				try {
					int error = RecvFrameData((*rop)->getChannel(i));
					if (error) throw error; 
				} catch (int e) { 
					acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
					acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber();
					return e; // Error, stop!
				}
				// Hit Info in event_data for discriminator frames in indices 12 && 13.
				//  event_data[12] = 0xWX, event_data[13] = 0xYZ
				//  W = # of hits TriP 0, X = # of hits TriP 1, Y = # of hits TriP 2, Z = # of hits TriP 3
				//  (Possibly the byte assignment is wrong/flipped somehow...)
				//  Whether we are pushing in pairs or not, we always want to read a number of adc blocks
				//  corresponding to the largest number of hits between the four plus one (end of gate).
				// Calculate the nhits variable so we can read the correct number of ADC Frames. 
				unsigned char maxHits = ((*rop)->getChannel(i)->GetBuffer()[12] >= (*rop)->getChannel(i)->GetBuffer()[13]) ? 
					(*rop)->getChannel(i)->GetBuffer()[12] : (*rop)->getChannel(i)->GetBuffer()[13];
				int nhits = ( (maxHits & 0x0F) >= ((maxHits & 0xF0)>>4) ) ?
					((int)maxHits & 0x0F) : ((int)(maxHits & 0xF0)>>4);
				nhits++; // add end of gate hit
				(*rop)->setHitsPerChannel(i, nhits);
				(*rop)->setOrigHitsPerChannel(i, nhits);
#if DEBUG_NEWREADOUT
				acqData.debugStream() << "   TOTAL Number of hits (" << i << ") = " << (*rop)->getHitsPerChannel(i);
#endif
				// Fiddle with evt data.
				evt->feb_info[2] = crocAddr;
				evt->feb_info[3] = (*rop)->getChannel(i)->GetChainNumber();
				evt->feb_info[6] = brdnum;
				evt->feb_info[7] = firmwareVersion; // We don't parse the FPGA's anymore in the DAQ... (int)tmpFEB->GetFirmwareVersion();
				// FillEventStructure here.  FES reads from the *channel's* buffer, not the frame's!
				FillEventStructure(evt, 1, (*rop)->getChannel(i));
				// ContactEventBuilder here.
				ContactEventBuilder(evt, (int)0, attach, sys_id);
				// Cleanup...
				(*rop)->getChannel(i)->DeleteBuffer();
				tmpFEB  = 0;
			} // end loop over data for reading the dpm

			// Increment the readoutObject pointer.
			rop++;
			// Check readout time - are we okay?
			gettimeofday(&readend, NULL);
			stopReadout = (unsigned long long)(readend.tv_sec*1000000) + (unsigned long long)(readend.tv_usec);
			readoutTimeDiff = (int)stopReadout - (int)startReadout;
			if (readoutTimeDiff > allowedTime) { continueReadout = false; }
		} // end while loop over readout objects
#if DEBUG_NEWREADOUT
		acqData.debugStream() << "&&&&&&&&&&&&&&&&&&&& - End of ReadDisc";
		acqData.debugStream() << "redoutObject Status:";
		DisplayReadoutObjects(readoutObjects);
#endif
	} // end readDisc

	// Do an "ADC read".  Loop over FEB ID's (readoutObjects) a while loop.  First, send a read frame to each 
	// channel that has an FEB with the right index if there is still a hit to read.  Then, after sending a 
	// frame to each of those channels, read each of them in turn for data.  After the read, decrement the 
	// hit counter.
	if (readADC && continueReadout) {
#if DEBUG_NEWREADOUT
		acqData.debugStream() << "===================";
		acqData.debugStream() << "Read the ADC's...";
		acqData.debugStream() << "===================";
#endif
		std::list<readoutObject*>::iterator rop = readoutObjects->begin();
		while (rop != readoutObjects->end() && continueReadout) {
			int febid    = (*rop)->getFebID();
			int febindex = febid - 1;
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "-> Top of readoutObject loop.";
			acqData.debugStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
			acqData.debugStream() << "feb id    = " << febid;
#endif
			// Pointer for the FEB's on each channel.  Be careful about deleting!   
			feb *tmpFEB;

			// Clear and reset all channels that have an FEB with id febid that still have a hit.
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Do the clear and resets for all channels with FEB's of the right id with a hit.";
#endif
			for (int i=0; i<(*rop)->getDataLength(); i++) {
				SendClearAndReset((*rop)->getChannel(i));
				try {
					int error = ReadStatus((*rop)->getChannel(i), doNotCheckForMessRecvd); 
					if (error) throw error; 
				} catch (int e) { 
					unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
					unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
					acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
					acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber();
					return e; // Error, stop!
				}
			} // end loop for clear and reset

			// Send an ADC read frame request to each channel with an FEB with id febid that still has a hit.
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Send the read ADC frame requests to all channels with FEB's of the right id with a hit.";
#endif
			for (int i=0; i<(*rop)->getDataLength(); i++) {
				int hitNum = (*rop)->getHitsPerChannel(i);
				int hitIdx = hitNum - 1; // Explicit offset.
				if (hitNum > baseRead) {
					// Make a pointer to the FEB on the channel with board number febid
					tmpFEB  = (*rop)->getChannel(i)->GetFebVector(febindex);
					int brdnum = tmpFEB->GetBoardNumber();
					if (brdnum!=febid) { acqData.fatalStream() << "Major error!"; exit(1); }
#if DEBUG_NEWREADOUT
					unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
					unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
					acqData.debugStream() << "  CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber() <<", FEB = " << brdnum << 
						", hits = " << (*rop)->getHitsPerChannel(i);
#endif
					// ADC frame built correctly in class constructor (message deleted in destructor)
					// Send the message for the deepest hit (we will decrement the counter later)
					SendFrameData(tmpFEB->GetADC(hitIdx), (*rop)->getChannel(i));
					tmpFEB  = 0;
				} // end if hitNum > 0
			} // end loop for send read request

			// Check the status for each channel to be sure the message was sent and recv'd.
			// There should only be one frame of data (from the FEB's in the loop above).
			// Read the data & decrement the appropriate hitsPerChannel value. 
			// Decalre it to ET. 
#if DEBUG_NEWREADOUT
			acqData.debugStream() << "->Check the status to be sure the message was sent and recv'd.  If so, read the data & decalre it.";
#endif
			bool stillHaveHits = false;
			for (int i=0; i<(*rop)->getDataLength(); i++) { // Read the earliest in *time* first -> deepest in the pipeline.
				int hitNum = (*rop)->getHitsPerChannel(i);
				int orgNum = (*rop)->getOrigHitsPerChannel(i) - 1;
				int hitIdx = hitNum - 1; // Explicit offset.
				if (hitNum > baseRead) {
					unsigned int clrstsAddr = (*rop)->getChannel(i)->GetClearStatusAddress();
					unsigned int crocAddr   = (clrstsAddr & 0xFF0000)>>16;
					try {
						int error = ReadStatus((*rop)->getChannel(i), checkForMessRecvd); 
						if (error) throw error; 
					} catch (int e) { 
						acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
						acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
							(*rop)->getChannel(i)->GetChainNumber();
						return e; // Error, stop!
					}
					// Make a pointer to the FEB on the channel with board number febid
					tmpFEB = (*rop)->getChannel(i)->GetFebVector(febindex);
					int brdnum = tmpFEB->GetBoardNumber();
					if (brdnum!=febid) { acqData.fatalStream() << "Major error!"; exit(1); }
#if DEBUG_NEWREADOUT
					acqData.debugStream() << "  CROC = " << crocAddr << ", Chain Number = " << 
						(*rop)->getChannel(i)->GetChainNumber() << ", FEB = " << brdnum << 
						", hits = " << (*rop)->getHitsPerChannel(i);
#endif
					// Read the DPM. 
					try {
						int error = RecvFrameData((*rop)->getChannel(i));
						if (error) throw error; 
					} catch (int e) { 
						acqData.critStream() << "Error in WriteAllData!  Cannot read the status register!";
						acqData.critStream() << "->Failed on CROC = " << crocAddr << ", Chain Number = " << 
							(*rop)->getChannel(i)->GetChainNumber();
						return e; // Error, stop!
					}
					// Fiddle with evt data.
					evt->feb_info[2] = crocAddr;
					evt->feb_info[3] = (*rop)->getChannel(i)->GetChainNumber();
					evt->feb_info[6] = brdnum;
					evt->feb_info[7] = firmwareVersion; // We don't parse the FPGA's anymore in the DAQ... (int)tmpFEB->GetFirmwareVersion();
					// Set the hit id.  Increment sourceID hit in "reverse" - sourceID hit 0 is earliest in physical time.
					evt->feb_info[8] = (unsigned int)(orgNum - hitIdx);
#if DEBUG_NEWREADOUT
					acqData.debugStream() << "   Original Max Hit Index on this board         = " << orgNum;
					acqData.debugStream() << "   Current Hit Index (ADC block) on this board  = " << hitIdx;
					acqData.debugStream() << "   Reported Hit ID                              = " << evt->feb_info[8];
					acqData.debugStream() << "     orgNum-hitIdx+1 = " << (orgNum-hitIdx+1);
					acqData.debugStream() << "     nReadoutADC     = " << nReadoutADC;
					if ( (orgNum-hitIdx+1) >= nReadoutADC ) { acqData.debugStream() << "     Time to cycle out."; }
#endif
					// FillEventStructure here.  FES reads from the *channel's* buffer, not the frame's!
					FillEventStructure(evt, 0, (*rop)->getChannel(i));
					// ContactEventBuilder here.
					ContactEventBuilder(evt, (int)0, attach, sys_id);
					// Cleanup...
					(*rop)->getChannel(i)->DeleteBuffer();
					tmpFEB  = 0;
					// Update hit architecture
					if ( (orgNum-hitIdx+1) >= nReadoutADC ) { 
#if DEBUG_NEWREADOUT
						acqData.debugStream() << "   Cycling out!  We've read the deepest N hits."; 
#endif
						stillHaveHits = false; 
						(*rop)->setHitsPerChannel(i, 0); // Don't read any more hits!
					} else {
						if (hitIdx>0) stillHaveHits = true; // only needs to be true for one channel
						(*rop)->setHitsPerChannel(i, hitIdx); // hitNum--
					}
#if DEBUG_NEWREADOUT
					acqData.debugStream() << "   New Number of hits (" << i << ") = " << (*rop)->getHitsPerChannel(i);
#endif
				} // end if hit check
			} // end for loop over readoutObject data

			if (!stillHaveHits) {
				(*rop)->zeroOrigHitsPerChannel();
				rop++; 
			} // else repeat the loop for the same channels & boards. 
			// Check readout time - are we okay?
			gettimeofday(&readend, NULL);
			stopReadout = (unsigned long long)(readend.tv_sec*1000000) + (unsigned long long)(readend.tv_usec);
			readoutTimeDiff = (int)stopReadout - (int)startReadout;
			if (readoutTimeDiff > allowedTime) { continueReadout = false; }
		} // end while

#if DEBUG_NEWREADOUT
		acqData.debugStream() << "&&&&&&&&&&&&&&&&&&&& - End of ReadADC";
		acqData.debugStream() << "redoutObject Status:";
		DisplayReadoutObjects(readoutObjects);
#endif
	} // end if readADC


#if DEBUG_NEWREADOUT
	acqData.debugStream() << "Exiting acquire_data::WriteAllData.";
	acqData.debugStream() << "-----------------------------------";
#endif
	return 0;
}


void acquire_data::RecvPreviewData(channels *theChannel, unsigned char *previewData)
{
/*! \fn acquire_data::RecvPreviewData(unsigned char *previewData)
 *
 * Read the channel status register and then read the preview hit data into a buffer.
 *
 * \param channels *theChannel, the CROC FE channel that we will read the status of.
 * \param unsigned char *previewData, the buffer we will fill with data.
 */
	// See acquire_data::RecvFrameData for a model.
}
#endif
