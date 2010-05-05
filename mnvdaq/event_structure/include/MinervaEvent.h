#ifndef MinervaEvent_h
#define MinervaEvent_h

/* Note: When using these to check the status of space in the DPM, we are actually being 
too conservative because the 8 bytes we are using for the MINERvA header are not in use 
at that stage (and so we can ignore the 2 bytes of "real" CRC). */

#define FEB_INFO_SIZE 76  // number of bytes in an FEB FPGA Frame with the event header
/* Not completely clear how we should handle the frame CRC: 
	76 = 8 MINERvA Header + 2 length + 9 header + 1 dummy (even) + 54 registers + 2 CRC 
The framework set is 74? -> no CRC == 8 + Length value embedded in the frame?  Probably not. 
The length in the old DAQ was defined as the embedded length + 2.  So, for whatever reason, 
the CRC was explicitly kept.  -> So, keep an eye on this while decoding! */

#define FEB_DISC_SIZE 1146 // number of bytes in the discriminator buffer with event header
/* The Discriminator blocks are of variable size:
	15 header + 2 CRC + 1 dummy + 40 per hit per trip
The prescription then must be to prodive the maximum possible space, but trim the buffer before
passing it to the event builder in order to ensure the frame length matches the buffer length. */
/* 8 MINERvA Header + 2 Length + 13 header + 1 dummy + 40*4*7 + 2 CRC == 1146 */

#define FEB_HITS_SIZE 885 // number of bytes in an ADC buffer with event header (per hit)
/* 885 = 8 MINERvA Header + 2 Length + 9 Header + 864 data bytes + 2 CRC (no dummy?) */ 

#define DAQ_HEADER 56     // number of bytes for the event header with the DAQ header attached.
/* 8 MINERvA Header + 48 bytes in v5.  This is the framework set. */

// The offset value defines where in the output buffer we need to begin inserting data for a 
// given FEB's worth of information.  So:
//   FEB 1's data starts at byte 0 and goes to SINGLE_EVENT_OFFSET-1
//   FEB 2's data starts at byte SINGLE_EVENT_OFFSET  and goes to 2*SINGLE_EVENT_OFFSET-1
// and so on until the end of the DAQ Event Info block in the last DAQ_HEADER bytes of the buffer.

#define MIN_CHAN_ID 0x0004 //crate 0, croc 1, channel 0
#define FEB_MIN_NUMBER 1   //decided more-or-less by fiat

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
 *  \brief This class will build the event and then pass eventData to be written to disk & displayed.
 */
class MinervaEvent {
	private:
		boost::mutex mutex; /*!<A BOOST mutual exclusion for threaded operation*/
		unsigned char *data_block; /*!<what to put the data into */
		unsigned char event_block[DAQ_HEADER]; /*!<a special buffer to hold onto the event info while we process
		everything else. */
	public:
		/*! the default constructor */
		MinervaEvent() { };
		/*! the constructor */
		MinervaEvent(unsigned char det, unsigned short int config, int run, int sub_run, 
			unsigned short int trig, unsigned char ledGroup, unsigned char ledLevel, 
			unsigned long long g_gate, unsigned long long gate, unsigned long long trig_time, 
			unsigned short int error, unsigned int minos, MinervaHeader *header);
		/*! the default destructor */
		~MinervaEvent() { };
		template <class X> void MakeDataBlock(X *frame, MinervaHeader *header);
		inline unsigned char* GetDataBlock() {return data_block;};
		unsigned char inline GetEventBlock(int i) {return event_block[i];};
};

#endif
