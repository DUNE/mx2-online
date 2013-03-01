#ifndef EventHandler_h
#define EventHandler_h

#include "MinervaDAQtypes.h"

struct EventHandler {
  unsigned short dataLength;
  unsigned char data[ MaxTotalDataPerChain ];
};

#endif
