#ifndef TestSuite_h
#define TestSuite_h

#include "log4cppHeaders.h"

#include "MinervaDAQtypes.h"
#include "Controller.h"
#include "ECROC.h"

unsigned char * ReadDPMTest( ECROC * ecroc, unsigned int channel, unsigned int nFEBs );
void SetupChargeInjection( EChannels* channel, unsigned int nFEBs );
void FPGAWriteConfiguredFrame( EChannels* channel, FEB* feb );
void TRIPSetupForChargeInjection( EChannels* channel, int boardID );
void FPGASetupForChargeInjection( EChannels* channel, int boardID );
void TestChannel( ECROC* ecroc, unsigned int channelNumber, unsigned int nFEBs );
ECROC * GetAndTestECROC( unsigned int address, Controller * controller );
Controller * GetAndTestController( int address, int crateNumber );


#endif
