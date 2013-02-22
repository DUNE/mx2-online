#ifndef FrontEndBoard_cpp
#define FrontEndBoard_cpp

#include "log4cppHeaders.h"
#include "FrontEndBoard.h"
#include "exit_codes.h"

log4cpp::Category& FrontEndBoardLog = log4cpp::Category::getInstance(std::string("FrontEndBoard"));

//-----------------------------------------------------
FrontEndBoard::FrontEndBoard( febAddresses a )
{
  /*! \fn********************************************************************************
   * The log-free constructor takes the following arguments:
   * \param a: The address (number) of the FrontEndBoard
   * \param reg:  The number of one byte registers in the FrontEndBoard message body
   *       The message body is set up for FrontEndBoard Firmware Versions 78+ (54 registers).  
   *       It will need to be adjusted for other firmware versions. ECS & GNP
   */
  boardNumber  = a;      
  FrontEndBoardLog.setPriority(log4cpp::Priority::DEBUG);  

}

//-----------------------------------------------------
std::auto_ptr<FPGAFrame> FrontEndBoard::GetFPGAFrame()
{
  std::auto_ptr<FPGAFrame> f( new FPGAFrame( boardNumber ) );
  return f;
}




#endif
