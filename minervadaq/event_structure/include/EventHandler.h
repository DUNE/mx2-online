#ifndef EventHandler_h
#define EventHandler_h
/*! \file EventHandler.h
*/

#include "MinervaDAQSizes.h"

struct EventHandler {
  unsigned short dataLength;
  unsigned char data[ MinervaDAQSizes::MaxTotalDataPerChain ];
};

#endif
