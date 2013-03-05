#ifndef EventHandler_h
#define EventHandler_h

#include "MinervaDAQSizes.h"

struct EventHandler {
  unsigned short dataLength;
  unsigned char data[ MinervaDAQSizes::MaxTotalDataPerChain ];
};

#endif
