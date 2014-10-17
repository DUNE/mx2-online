#ifndef RunHeader_h
#define RunHeader_h
/*! 
  \file RunHeader.h
*/

#include <vector>
#include "FrameHeader.h"

/*! 
  \class RunHeader 
  \brief This class will build the Run Header used to hold run information
  \author William Badgett
  */
class RunHeader 
{
  private:
    unsigned char* data; 
    unsigned short dataLength;

  public:
    RunHeader(FrameHeader * header, std::vector<unsigned short> configurations);
    ~RunHeader();

    enum 
    {
      MAX_CROC = 15,
      CHANNELS_PER_CROC = 4
    };

    unsigned char* GetData() const;
    unsigned char GetData(int i) const;
    unsigned short GetDataLength() const;
    void ClearData();
};


static const int runHeaderSize = 4 * RunHeader::MAX_CROC * sizeof(unsigned short) * RunHeader::CHANNELS_PER_CROC + sizeof(int) + FrameHeader::FRAME_HEADER_SIZE * sizeof(short);

#endif
