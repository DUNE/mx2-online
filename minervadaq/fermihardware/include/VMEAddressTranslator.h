#ifndef VMEAddressTranslator_h
#define VMEAddressTranslator_h
/*! \file VMEAddressTranslator.h 
*/

#include <string>

#include "VMEModuleTypes.h"

/*! 
  \class VMEAddressTranslator
  \brief Simple VME address decoding.
  \author Gabriel Perdue

  By convention, CROC and ECROC *numbers* are 0x1 through 0xF, 
  and CRIM *numbers* are 0x10 through 0xF0. In principle they 
  could be set differently and then this class will not give 
  sensible answers.

  In general, this class offers no protections - if you pass an 
  invalid address, the class will just calculate a number and 
  return it.
  */

class VMEAddressTranslator 
{
  static const unsigned int CROCMask;
  static const unsigned int CRIMMask;
  static const unsigned int ECROCMask;
  static const unsigned int EChannelsMask;

  public:
    static unsigned int GetCROCNumber( unsigned int address );
    static unsigned int GetCRIMNumber( unsigned int address );
    static unsigned int GetECROCNumber( unsigned int address );
    static unsigned int GetEChannelsNumber( unsigned int address );
};

#endif
