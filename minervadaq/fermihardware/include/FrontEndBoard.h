#ifndef FrontEndBoard_h
#define FrontEndBoard_h
/*! \file FrontEndBoard.h
*/

#include "TRIPFrame.h"
#include "ADCFrame.h"
#include "DiscrFrame.h"
#include "FPGAFrame.h"

/*! 
  \class FrontEndBoard
  \brief The class which holds all of the information associated with a Front End Board (FEB).
  \author Gabriel Perdue

  FrontEndBoard does not hold data (beyond its FEB address). It instead serves as a placeholder 
  in loops over boards in EChannels and as a convenience factor for returning instances of 
  advanced frames. It does not store these frames, but rather creates them on the fly and hands 
  over a shared_ptr.
  */

class FrontEndBoard {

  private:
    FrameTypes::FEBAddresses boardNumber; 

  public:
    FrontEndBoard( FrameTypes::FEBAddresses theAddress ); 
    ~FrontEndBoard() { };    

    FrameTypes::FEBAddresses inline GetBoardNumber() { return boardNumber; };

    std::tr1::shared_ptr<FPGAFrame> GetFPGAFrame();
    std::tr1::shared_ptr<TRIPFrame> GetTRIPFrame(int tripNumber); 
    std::tr1::shared_ptr<ADCFrame> GetADCFrame(int hitBlock); 
    std::tr1::shared_ptr<DiscrFrame> GetDiscrFrame(); 

};

#endif
