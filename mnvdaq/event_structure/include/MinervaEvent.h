#ifndef MinervaEvent_h
#define MinervaEvent_h

#if v65
#define FEB_INFO_SIZE 62 //number of bytes in an FEB FPGA Frame with the event header
#elif v81
#define FEB_INFO_SIZE 76 //number of bytes in an FEB FPGA Frame with the event header
#endif
#define FEB_DISC_SIZE 982 //number of bytes in the discriminator buffer with event header
#define FEB_HITS_SIZE 885 //number of bytes in an ADC buffer with event header (per hit)
#define DAQ_HEADER 56 //number of bytes for the event header with the DAQ header attached.

//This offset value defines where in the output buffer we need to begin
//inserting data for a given FEB's worth of information
//So:
//FEB 1's data starts at byte 0 and goes to SINGLE_EVENT_OFFSET-1
//FEB 2's data starts at byte SINGLE_EVENT_OFFSET  and goes to 2*SINGLE_EVENT_OFFSET-1
//and so on until the end of the DAQ Event Info block in the last DAQ_HEADER bytes of the buffer.

#define MIN_CHAN_ID 0x0004 //crate 0, croc 1, channel 0
#define FEB_MIN_NUMBER 1 //decided more-or-less by fiat

#include "feb.h"

#include <boost/thread/mutex.hpp>

/*! \class MinervaHeader
 *
 * \brief Class which holds and manipulates data in event block headers
 *
 * This class holds and sets up MINERvA event headers for data blocks.  
 * It is used by the event builder to place headers at the top of event blocks 
 * before sending data to a file for storage.
 *
 */
class MinervaHeader {
	private:
		unsigned short data_bank_header[4]; /*!<The data bank header for all data other than EOE */
		unsigned short DAQ_event_header[4]; /*!<The End-of-Event (EOE) Record header */
		unsigned short chan_number; /*!<the channel number for data having a header attached */
		boost::mutex mutex; /*!<A BOOST mutual exclusion for threaded operation */

	public:
		/*! the constructor */
		MinervaHeader(int crateID, int crocID, int chanID, 
			int bank, int feb_number, int firmware, int hit, int length);
		/*! default constructor */
		MinervaHeader(unsigned char crate);
		/*! default destructor */
		~MinervaHeader() { };
		unsigned short inline *GetDataBankHeader() {return data_bank_header;};
		unsigned short inline *GetDAQEvtHeader() {return DAQ_event_header;};
		unsigned short inline GetChanNo() {return chan_number;};
};

/*! \class MinervaEvent 
 *  \brief this class will build the event and then pass off eventData to be written to disk & 
 *  displayed and stuff.
 */
class MinervaEvent {
	private:
		// unsigned char buffer[MAX_BUFFER_SIZE]; //all of the FEB's & DAQ headers + the EVENT DAQ INFO
		boost::mutex mutex; /*!<A BOOST mutual exclusion for threaded operation*/
		unsigned char *data_block; /*!<what to put the data into */
		unsigned char event_block[DAQ_HEADER]; /*!<a special buffer to hold onto the event info while we process
		everything else. */
	public:
		/*! the default constructor */
		MinervaEvent() { };
		/*! the constructor */
		MinervaEvent(int det, int config, int run, int sub_run, int trig,
			unsigned int g_gate, unsigned int gate, unsigned long int trig_time, 
			unsigned short int error, unsigned int minos, MinervaHeader *header);
		/*! the default destructor */
		~MinervaEvent() { };
		template <class X> void MakeDataBlock(X *frame, MinervaHeader *header);
		inline unsigned char* GetDataBlock() {return data_block;};
		unsigned char inline GetEventBlock(int i) {return event_block[i];};
};

#endif
