#ifndef ADCFrame_h
#define ADCFrame_h
/*! \file ADCFrame.h
*/

#include "LVDSFrame.h"

/*! 
  \class ADCFrame
  \brief This class controls the frames that stores hit pulse heights.
  \author Cristian Gingu
  \author Gabriel Perdue
  \author Elaine Schulte
  */
class ADCFrame : public LVDSFrame {
  private:

  public: 
    ADCFrame(FrameTypes::FEBAddresses a, FrameTypes::RAMFunctionsHit f); 
    ~ADCFrame() {};

    // Not entirely sure why we need "+2", but we seem to...
    inline unsigned int GetOutgoingMessageLength() { 
      return (MinervaDAQSizes::FrameHeaderLengthOutgoing + 2); 
    };
    void MakeMessage();
    void DecodeRegisterValues(); 
};

#endif
