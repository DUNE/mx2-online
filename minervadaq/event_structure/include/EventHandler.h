#ifndef EventHandler_h
#define EventHandler_h
/*! 
  \file EventHandler.h
  \brief Define the EventHandler struct.
*/

#include "MinervaDAQSizes.h"

/*! 
  \struct EventHandler
  \brief Hold all the data for a chain (SequencerReadoutBlock).
  \author Gabriel Perdue
  */
struct EventHandler {
  unsigned short dataLength;
  unsigned char data[ MinervaDAQSizes::MaxTotalDataPerChain ];
};

#endif
