#ifndef acquire_data_h
#define acquire_data_h
#include "controller.h" 
#include "adctdc.h" // This class isn't included in the contoller, but we need it for reads & writes.
#include "acquire.h" 

#include <boost/thread/thread.hpp>
#include <boost/bind.hpp>
#include "MinervaEvent.h"
#include "event_builder.h"

#include <fstream>
#include <string>
#include <sstream>

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

	public:
		/*! Specialized constructor which takes the filename string for the timing output */
		acquire_data(std::string fn) {frame_acquire_log.open("frame_data_time_log.csv"); 
		et_filename = fn;};
		/*! Specialized destructor */
		~acquire_data() {std::cout<<"deleting acqire data"<<std::endl;delete daqAcquire; delete daqController; };

		typedef boost::mutex::scoped_lock  lock; /*!< A BOOST scoped_lock for threaded operation */
		boost::mutex eb_mutex; /*!< A BOOST multiple exclusion for sending data to the event builder */

		/*! An access function:  returns the value of the requested controller object */
		controller inline *GetController() {return daqController;};
		/*! Function to initialize the data acquisition electronics and make up necessary functional objects */
		void InitializeDaq(int id); //pass it a controller ID
		/*! Function to initialize a CRIM at the given VME address */
		void InitializeCrim(int address); //threaded function
		/*! Function to initialize a CROC at the given VME address; requires an identifier */
		void InitializeCroc(int address, int a); //threaded function
		/*! Function to set up the interrupt handler */
		int SetupIRQ();
		/*! Function to re-enable the interrupt handler */
		int ResetGlobalIRQEnable();
		/*! Function to build a list of FEB objects for use in data acquisition */
		int BuildFEBList(int i, int j);
		/*! Function to initialize TRiP-t chips on FEB's */
		int InitializeTrips(feb *tmpFEB, croc *tmpCroc, channels *tmpChan);
		/*! Function to set the high voltage on a given FEB */
		int SetHV(feb *febTrial, croc *crocTrial, channels *channelTrial, int newHV, int newPulse, int hvEnable);
		/*! Function to monitor the high voltage on a given FEB */
		int MonitorHV(feb *febTrial, croc *tmpCroc, channels *tmpChan);

		/*! A templated function for sending messages from a generic "device" */
		template <class X> int SendMessage(X *device, croc *crocTrial, channels *channelTrial,bool singleton);
		/*! A templated function for receiving messages from a generic "device" */
		template <class X> int ReceiveMessage(X *device, croc *crocTrial, channels *channelTrial);
		/*! A templated class for filling the DPM on each CROC channel, should that be desired */
		template <class X> bool FillDPM(croc *crocTrial, channels *channelTrial, X *frame, 
		int outgoing_length, int incoming_length);
		/*! Function which executes the acquisition sequence for a given FEB */
		bool TakeAllData(feb *febTrial, channels *channelTrial, croc *crocTrial, event_handler *evt, int thread, 
			et_att_id  attach, et_sys_id  sys_id);
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
		/*!  Function which sets up a designated "trigger" */
		void TriggerDAQ(int a);
		/*! Function which waits for the interrupt handler to raise an interrupt */
		void WaitOnIRQ();
		/*! Function which acknowledges the interrupt and resets the interrupt handler */
		void AcknowledgeIRQ();
		/*! Function which sends data to the event builder via ET */
		void ContactEventBuilder(event_handler *evt,int thread, et_att_id  attach, et_sys_id  sys_id);
};

#endif
