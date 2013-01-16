#ifndef ReadoutWorker_h
#define ReadoutWorker_h
#include "MinervaDAQtypes.h"
#include "Controller.h" 
#include "ECROC.h"
#include "crim.h"
#include "log4cppHeaders.h"

#include "MinervaEvent.h"
#include "event_builder.h"

#include <fstream>
#include <string>
#include <sstream>
#include <signal.h>   // for sig_atomic_t




// Logging base.
log4cpp::Category& acqData = log4cpp::Category::getInstance(std::string("acqData"));


// Mixed mode cutoff time for physics spills.  If a physics gate takes longer than this to
// read out, we will abort the following calibration gate and skip to another physics gate.
#if WH14T||WH14B
#if SINGLEPC
const int physReadoutMicrosec = 13500; //microseconds, useful test stand value
//const int physReadoutMicrosec = 135000; //microseconds, useful test stand value
#else
const int physReadoutMicrosec = 150000; //microseconds, useful test stand value?
#endif // WH14
#else
const int physReadoutMicrosec = 900000; //microseconds, good MINERvA value for 2.06 s spill cycle?
#endif

// Total allowed readout times (microseconds).
int allowedReadoutTime;
// Bail on any gate taking longer than these times and set an error flag.
// Label by triggerType.
const int allowedPedestal       =   900000;
//const int allowedPedestal       =  5000;  // Play-around test value.  
const int allowedNuMI           =  4000000; // Block for at most one spill?
const int allowedCosmic         = 10000000; // UNTESTED! (Really, an MTest value.)
const int allowedLightInjection =   900000; // Same as pedestal (we are mixing now).


/*! \class ReadoutWorker
 *  \brief The class containing all methods necessary for 
 *  requesting and manipulating data from the MINERvA detector.
 *
 *  This class contains all of the necessary functions 
 *  for acquiring and manipulating data from the MINERvA detector.
 *
 *  This class sets up the electronics, builds a list of FEB's on 
 *  each CROC channel, and executes the data acquisition sequence for each FEB
 *  on a channel.  These functions are called via an ReadoutWorker class object
 *  from the main routine.
 */
class ReadoutWorker {
	private: 
		controller *daqController; /*!< A CAEN V2718 VME Controller Object */
		acquire *daqAcquire;       /*!< An object of VME write functions */

		unsigned char *DPMData; /*!<A buffer for handling BLT data */

		boost::mutex data_lock, send_lock; /*!< Boost multiple exclusions for threaded operation */

		static const int dpmMax;              /*!<Maximum number of bytes the DPM can hold */
		std::ofstream frame_acquire_log;      /*!< log file streamer for timing output */
		std::string et_filename;              /*!< A string object for the Event Transfer output filename */
		static const unsigned int timeOutSec; /*!< How long we will wait for a beam spill before moving on... */
		log4cpp::Appender* acqAppender;
		int hwInitLevel;        /*!< Flag that controls whether or not we setup the timing registers of the VME cards (CROCs & CRIMs). */

		static const bool checkForMessRecvd, doNotCheckForMessRecvd; 
		static const bool checkForErrs, doNotCheckForErrs;       
	public:
		/*! Specialized constructor. */
		ReadoutWorker(std::string fn, log4cpp::Appender* appender, log4cpp::Priority::Value priority, 
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
		~ReadoutWorker() {
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
		void InitializeDaq(int id, RunningModes runningMode, std::list<readoutObject*> *readoutObjs=0);

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

		/*! Resets the sequencer control latch when the latching mechanism is enabled (V9+ CRIM only). */
		int ResetSequencerControlLatch(int crimID); 

		/*!  Function that runs the "trigger" (only executes a VME command for "OneShot"). */
		int TriggerDAQ(unsigned short int triggerBit, int crimID); // Note, be careful about the master CRIM.

		/*! Function that waits for the interrupt handler to raise an interrupt */
		int WaitOnIRQ(sig_atomic_t const & continueFlag);

		/*! Function that acknowledges the interrupt and resets the interrupt handler */
		int AcknowledgeIRQ();

		/*! Function that sends data to the event builder via ET */
		bool ContactEventBuilder(event_handler *evt, int thread, et_att_id attach, et_sys_id sys_id);

		/*! Function that gets the MINOS SGATE value from the CRIM registers.  Check the "master" CRIM. */
		unsigned int GetMINOSSGATE();

		// New readout model functions.
		// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		/*! Send a Clear and Reset to a CROC FE Channel. */
		void SendClearAndReset(channels *theChain);
		/*! Send a Status Register *Clear only* to a CROC FE Channel. */
		void SendClear(channels *theChain);
		/*! Send a *DPM Pointer reset only* to a CROC FE Channel. */
		void SendReset(channels *theChain);
		/*! Read the status register on a CROC FE Channel with a flag to see if we should check for the message recv'd. */
		int ReadStatus(channels *theChain, bool receiveCheck);

		/*! Initialize a list of readoutObjects. */
		void InitializeReadoutObjects(std::list<readoutObject*> *objectList);
		/*! Display the contents of a list of readoutObjects. */
		void DisplayReadoutObjects(std::list<readoutObject*> *objectList);

		/*! Send messages to a generic device using normal write cycle. 
		    -> Write the outgoing message from the device to the FE Channel FIFO, send the message. */
		template <class X> void SendFrameData(X *device, channels *theChannel);

		/*! Send messages to a generic device using FIFO BLT write cycle. 
		    -> Write the outgoing message from the device to the FE Channel FIFO using BLT, send the message. */ 
		template <class X> void SendFrameDataFIFOBLT(X *device, channels *theChannel);

		/*! Receive messages for a generic device.
		   -> Read DPM pointer, read BLT, store data in *device* buffer.
		   -> Should be used primarily for debugging and for building the FEB list. */
		template <class X> int RecvFrameData(X *device, channels *theChannel);

		/*! Receive messages. 
		   -> Read DPM pointer, read BLT, store data in *channel* buffer. */
		int RecvFrameData(channels *theChannel, bool checkForErrors=true);

		/*! Function that fills an event structure for further data handling by the event builder. */
		void FillEventStructure(event_handler *evt, int bank, channels *theChannel);

		/*! Run the full acquisition sequence for a gate, write the data to file. */
		int WriteAllData(event_handler *evt, et_att_id attach, et_sys_id sys_id, 
			std::list<readoutObject*> *readoutObjects, const int allowedTime, 
			const bool readFPGA, const int nReadoutADC, const bool zeroSuppress);

};

#endif
