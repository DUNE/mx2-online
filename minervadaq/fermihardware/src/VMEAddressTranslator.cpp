#ifndef VMEAddressTranslator_cpp
#define VMEAddressTranslator_cpp
/*! \file VMEAddressTranslator.cpp
*/

#include "VMEAddressTranslator.h"


const unsigned int VMEAddressTranslator::CROCMask      =   0x0F0000; /*!< 24 bit address */
const unsigned int VMEAddressTranslator::CRIMMask      =   0xF00000; /*!< 24 bit address */
const unsigned int VMEAddressTranslator::ECROCMask     = 0xFF000000; /*!< 32 bit address */
const unsigned int VMEAddressTranslator::EChannelsMask = 0x000F0000; /*!< 32 bit address */

//-----------------------------
unsigned int VMEAddressTranslator::GetCROCNumber( unsigned int address )
{
  return ( (address & CROCMask) >> VMEModuleTypes::CROCAddressShift );
}

//-----------------------------
unsigned int VMEAddressTranslator::GetCRIMNumber( unsigned int address )
{
  return ( (address & CRIMMask) >> VMEModuleTypes::CRIMAddressShift );
}

//-----------------------------
unsigned int VMEAddressTranslator::GetECROCNumber( unsigned int address )
{
  return ( (address & ECROCMask) >> VMEModuleTypes::ECROCAddressShift);
}

//-----------------------------
unsigned int VMEAddressTranslator::GetEChannelsNumber( unsigned int address )
{
  return ( (address & EChannelsMask) / VMEModuleTypes::EChannelOffset );
}

#endif
