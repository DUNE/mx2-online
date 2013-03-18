#ifndef DAQHeader_h
#define DAQHeader_h
/*! \file DAQHeader.h
*/

static const int daqHeaderSize = 56;

#include "FrameHeader.h"

/*! \class DAQHeader 
 *  \brief This class will build the DAQ Header.
 */
class DAQHeader {
	private:
		unsigned char* data; 
    unsigned short dataLength;

	public:
    DAQHeader(FrameHeader *header); // by default we build a Sentinel frame.
		DAQHeader(unsigned char det, unsigned short int config, int run, int sub_run, 
			unsigned short int trig, unsigned char ledGroup, unsigned char ledLevel, 
			unsigned long long g_gate, unsigned int gate, unsigned long long trig_time, 
			unsigned short int error, unsigned int minos, unsigned int read_time, 
			FrameHeader *header,  unsigned short int nADCFrames, unsigned short int nDiscFrames, 
			unsigned short int nFPGAFrames);
		~DAQHeader();

		unsigned char* GetData() const;
		unsigned char GetData(int i) const;
		unsigned short GetDataLength() const;
		void ClearData();
};




#endif
