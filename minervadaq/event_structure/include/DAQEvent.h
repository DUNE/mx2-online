#ifndef DAQEvent_h
#define DAQEvent_h

static const int febInfoSize = 76;
static const int febDiscSize = 1146;
static const int febHitsSize = 885; // 446
static const int daqHeaderSize = 56;

#include "FrameHeader.h"

/*! \class DAQEvent 
 *  \brief This class will build the event and then pass eventData to be written to disk & displayed.
 */
class DAQEvent {
	private:
		unsigned char *data_block; 
		unsigned char event_block[daqHeaderSize]; 
		log4cpp::Appender* evtAppender; 

	public:
		DAQEvent(unsigned char det, unsigned short int config, int run, int sub_run, 
			unsigned short int trig, unsigned char ledGroup, unsigned char ledLevel, 
			unsigned long long g_gate, unsigned int gate, unsigned long long trig_time, 
			unsigned short int error, unsigned int minos, unsigned int read_time, 
			FrameHeader *header,  unsigned short int nADCFrames, unsigned short int nDiscFrames, 
			unsigned short int nFPGAFrames ,log4cpp::Appender* appender=0);
		~DAQEvent() { };
		template <class X> void MakeDataBlock(X *frame, FrameHeader *header);
		inline unsigned char* GetDataBlock() {return data_block;};
		void DeleteDataBlock() {delete [] data_block;};
		unsigned char inline GetEventBlock(int i) {return event_block[i];};
};

#endif
