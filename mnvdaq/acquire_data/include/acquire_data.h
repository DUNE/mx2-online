#ifndef acquire_data_h
#define acquire_data_h
#include "MinervaDAQtypes.h"
#include "controller.h" 
#include "adctdc.h" // This class isn't included in the contoller, but we need it for reads & writes.
#include "acquire.h" 
#include "log4cppHeaders.h"

#include <boost/thread/thread.hpp>
#include <boost/bind.hpp>
#include "MinervaEvent.h"
#include "event_builder.h"

#include <fstream>
#include <string>
#include <sstream>


// The RunningMode defines the sort of data being collected during a run and is not synonymous with 
// trigger type.  For example, the MixedBeamLightInjection RunningMode will alternate between beam 
// gates and LI gates.  The RunningMode defines the CRIM timing mode and sets the behavior of the LI 
// box and governs the switch between trigger types.  These are equivalent to OperatingMode in the 
// old Windows DAQ system.  This value is not stored in the data stream but *is* stored in the 
// SAM metadata.
typedef enum RunningModes {
	OneShot                 = 0, // "OneShot" - Internal CRIM Timing, No Frequency.
	NuMIBeam                = 1, // "MTM" - MTM CRIM Timing, (No Frequency).
	Cosmics                 = 2, // "Cosmic" - Intneral CRIM Timing, w/ Frequency Set!
	PureLightInjection      = 3, // MTM CRIM Timing, (No Frequency), software gates, LI Box alive
	MixedBeamPedestal       = 4, // MTM CRIM Timing, (No Frequency), MTM && software gates
	MixedBeamLightInjection = 5  // MTM CRIM Timing, (No Frequency), MTM && software gates, LI Box alive
};

// The TriggerType dictates whether or not the DAQ issues a software gate command to the CRIM and 
// additionally is written into the DAQ Header to identify the data type for the GATE.  The value 
// assignments here must match those defined in the DAQHeader class in the MINERvA Software framework.
typedef enum TriggerType {
	UnknownTrigger  = 0x0000,
	Pedestal        = 0x0001,
	LightInjection  = 0x0002,
	ChargeInjection = 0x0004,
	Cosmic          = 0x0008,
	NuMI            = 0x0010,
	TGReserved6     = 0x0020,
	TGReserved7     = 0x0040,
	MonteCarlo      = 0x0080  // Obviously, the DAQ should not write this type, ever!
};

log4cpp::Category& acqData = log4cpp::Category::getInstance(std::string("acqData"));

/*! \class acquire_data
 *  \brief The class containing all methods necessary for 
 *  requesting and manipulating data from teh MINERvA detector.
 *
 *  This class contains all of the necessary functions 
 *  for acquiring and manipulating data from the MINERvA detector.
 *  The class is set up for either threaded or multi-threaded operation
 *  as needed by the experiment.  
 *
 *  There are also functions for setting and monitoring the HV on 
 *  the FEB's if necessary.  
 *
 *  This class sets up the electronics, builds a list of FEB's on 
 *  each CROC channel, and executes the data acquisition sequence for each FEB
 *  on a channel.  These functions are called via an acquire_data class object
 *  from the main routine.
 *
 */
class acquire_data {
	private: 
		controller *daqController; /*!< A CAEN V2718 VME Controller Object */
		acquire *daqAcquire; /*!< An object of VME write functions */

		unsigned char *DPMData; /*!<A buffer for handling BLT data */

		boost::mutex crim_lock, croc_lock, feb_lock, data_lock,
			send_lock, receive_lock, connect_lock; /*!< Boost multiple exclusions for threaded operation */

		static const int dpmMax; /*!<Maximum number of bytes the DPM can hold */
		std::ofstream frame_acquire_log; /*!< log file streamer for timing output */
		std::string et_filename; /*!< A string object for the Event Transfer output filename */
		static const int numberOfHits;
		static const unsigned int timeOutSec; /*!< How long we will wait for a beam spill before moving on... */
		log4cpp::Appender* acqAppender;
		int hwInitLevel;        /*!< Flag that controls whether or not we setup the timing registers of the VME cards (CROCs & CRIMs). */

	public:
		/*! Specialized constructor. */
		acquire_data(std::string fn, log4cpp::Appender* appender, log4cpp::Priority::Value priority, 
			int hwInit=0) {
#if TIME_ME
			frame_acquire_log.open("frame_data_time_log.csv"); 
#endif
			et_filename = fn;
			acqAppender = appender;
			acqData.setPriority(priority);
			hwInitLevel = hwInit;
		};
		/*! Specialized destructor. */
		~acquire_data() {
			std::cout << "Deleting acqire_data." << std::endl;
			frame_acquire_log.close(); 
			delete daqAcquire; 
			delete daqController; 
		};

		typedef boost::mutex::scoped_lock  lock; /*!< A BOOST scoped_lock for threaded operation */
		boost::mutex eb_mutex; /*!< A BOOST multiple exclusion for sending data to the event builder */

		/*! An access function:  returns the value of the requested controller object */
		controller inline *GetController() {return daqController;};

		/*! Function to initialize the data acquisition electronics and make up necessary functional objects */
		void InitializeDaq(int id, RunningModes runningMode); // Pass it a controller ID & a running mode.

		/*! Function to initialize a CRIM at the given VME address w/ index & running mode */
		void InitializeCrim(int address, int index, RunningModes runningMode); 

		/*! Function to initialize a CROC at the given VME address; requires an index. 
		    Additionally, we pass the number of FEB's to search for on each channel.  
		    (These are passed this way for formatting convenience.)  11 is the default 
		    (instead of 15) because 11 is the maximum number we will install on a chain.  */
		void InitializeCroc(int address, int crocNo, int nFEBchain0=11, int nFEBchain1=11, int nFEBchain2=11, int nFEBchain3=11); 

		/*! Function to set up the interrupt handler on CRIM index */
		int SetupIRQ(int index);

		/*! Function to re-enable the interrupt handler for CRIM index */
		int ResetGlobalIRQEnable(int index);

		/*! Function to build a list of FEB objects for use in data acquisition. */
		int BuildFEBList(int chainID, int crocNo, int nFEBs=11);

		/*! Write to the CROC Fast Command register. */
		// Passing an array like this is a bit old fashioned, but there it is...
		int WriteCROCFastCommand(int id, unsigned char command[]);

		/*! Reset the CRIM sequencer latch (only needed in Cosmic mode) */
		int ResetCRIMSequencerLatch(int id);

		/*! A templated function for sending messages from a generic "device" */
		template <class X> int SendMessage(X *device, croc *crocTrial, channels *channelTrial, bool singleton);

		/*! A templated function for receiving messages from a generic "device" */
		template <class X> int ReceiveMessage(X *device, croc *crocTrial, channels *channelTrial);

		/*! A templated class for filling the DPM on each CROC channel, should that be desired */
		template <class X> int FillDPM(croc *crocTrial, channels *channelTrial, X *frame, 
			int outgoing_length, int incoming_length);

		/*! Function which executes the acquisition sequence for a given FEB.
		    We pass a boolean flag and hit depth integer to control the "readout level" for 
		    each FEB. */
		bool TakeAllData(feb *febTrial, channels *channelTrial, croc *crocTrial, event_handler *evt, int thread, 
			et_att_id  attach, et_sys_id  sys_id, bool readFPGA=true, int nReadoutADC=8);

		/*! Function which fills an event structure for further data handling by the event builder; templated */
		template <class X> void FillEventStructure(event_handler *evt, int bank, X *frame, 
			channels *channelTrial);

		/*! A templated function for acquiring data from a chosen device */
		template <class X> int AcquireDeviceData(X *frame, croc *crocTrial, channels *channelTrial, int length);

		/*! A function for reading off a CROC channel's DPM */
		int GetBlockRAM(croc *crocTrial, channels *channelTrial);

		/*! An access function for returning the buffer into which DPM data has been stored */
		unsigned char inline *GetDPMBuffer() {return DPMData;};

		/*! An access function for returning the VME read/write function object */
		inline acquire* GetDaqAcquire() {return daqAcquire;};

		/*! Function to reset a CROC channel's DPM */
		bool ResetDPM(croc*, channels*);

		/*!  Function which runs the "trigger" (only executes a VME command for "OneShot"). */
		int TriggerDAQ(unsigned short int triggerBit, int crimID); // Note, be careful about the master CRIM.

		/*! Function which waits for the interrupt handler to raise an interrupt */
		int WaitOnIRQ();

		/*! Function which acknowledges the interrupt and resets the interrupt handler */
		int AcknowledgeIRQ();

		/*! Function which sends data to the event builder via ET */
		void ContactEventBuilder(event_handler *evt,int thread, et_att_id  attach, et_sys_id  sys_id);

		/*! Function that gets the MINOS SGATE value from the CRIM registers.  Check the "master" CRIM. */
		unsigned int GetMINOSSGATE();
};

#endif