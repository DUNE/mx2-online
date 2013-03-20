#ifndef RegisterWords_h
#define RegisterWords_h
/*! \file RegisterWords.h
*/

/*!
  \brief Constants used for specific messages to the VME modules.
  \author Gabriel Perdue
  */
namespace RegisterWords {

  unsigned char channelReset[] = {0x00,0x80};  /*!< Send to a ECROC EChannels */
  unsigned char sendMessage[]  = {0x00,0x40};  /*!< Send to a ECROC EChannels */

};

#endif
