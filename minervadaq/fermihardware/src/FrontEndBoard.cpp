#ifndef FrontEndBoard_cpp
#define FrontEndBoard_cpp
/*! \file FrontEndBoard.cpp
*/

#include "log4cppHeaders.h"
#include "FrontEndBoard.h"
#include "exit_codes.h"

log4cpp::Category& FrontEndBoardLog = log4cpp::Category::getInstance(std::string("FrontEndBoard"));

//-----------------------------------------------------
FrontEndBoard::FrontEndBoard( FrameTypes::FEBAddresses theAddress ) : 
  boardNumber(theAddress)
{
  FrontEndBoardLog.setPriority(log4cpp::Priority::DEBUG);  
}

//-----------------------------------------------------
std::tr1::shared_ptr<FPGAFrame> FrontEndBoard::GetFPGAFrame()
{
  std::tr1::shared_ptr<FPGAFrame> frame( new FPGAFrame( this->boardNumber ) );
  return frame;
}

//-----------------------------------------------------
std::tr1::shared_ptr<TRIPFrame> FrontEndBoard::GetTRIPFrame(int tripNumber)
{
  using namespace TripTTypes;

  TRiPFunctions chipFunction = tNone;
  switch (tripNumber) {   
    case 0:
      chipFunction = tTR0;
      break;
    case 1:
      chipFunction = tTR1;
      break;
    case 2:
      chipFunction = tTR2;
      break; 
    case 3:
      chipFunction = tTR3;
      break;
    case 4:
      chipFunction = tTR4;
      break;
    case 5:
      chipFunction = tTR5;
      break;
    default:
      FrontEndBoardLog.fatalStream() << "Invalid TriP ChipID at instantiation!";
      exit(EXIT_FEB_UNSPECIFIED_ERROR);
  }
  std::tr1::shared_ptr<TRIPFrame> frame( new TRIPFrame( this->boardNumber, chipFunction ) );
  return frame;
}

//-----------------------------------------------------
std::tr1::shared_ptr<ADCFrame> FrontEndBoard::GetADCFrame(int hitBlock)
{
  using namespace FrameTypes;

  RAMFunctionsHit ramFunction = NoRAM;
  switch (hitBlock) {
    case 0:
      ramFunction = ReadHit7;
      break;
    case 1:
      ramFunction = ReadHit6;
      break;
    case 2:
      ramFunction = ReadHit5;
      break;
    case 3:
      ramFunction = ReadHit4;
      break;
    case 4:
      ramFunction = ReadHit3;
      break;
    case 5:
      ramFunction = ReadHit2;
      break;
    case 6:
      ramFunction = ReadHit1;
      break;
    case 7:
      ramFunction = ReadHit0;
      break;
    default:
      FrontEndBoardLog.fatalStream() << "Invalid ADC RAMFunction at instantiation!";
      exit(EXIT_FEB_UNSPECIFIED_ERROR);
  }

  std::tr1::shared_ptr<ADCFrame> frame( new ADCFrame( this->boardNumber, ramFunction ) );
  return frame;
}

//-----------------------------------------------------
std::tr1::shared_ptr<DiscrFrame> FrontEndBoard::GetDiscrFrame() 
{
  std::tr1::shared_ptr<DiscrFrame> frame( new DiscrFrame( this->boardNumber ) );
  return frame;
}



#endif
