#ifndef TestSuite_h
#define TestSuite_h

#include "log4cppHeaders.h"

#include "MinervaDAQtypes.h"
#include "Controller.h"
#include "ECROC.h"

// These two tests are coupled and should be called back-to-back. 
// We use the pointer from one test in the other.
unsigned char * ReadDPMTestData( ECROC * ecroc, unsigned int channel, 
    unsigned int nFEBs, unsigned short pointer );
unsigned short int ReadDPMTestPointer( ECROC * ecroc, unsigned int channel, 
    unsigned int nFEBs );

void SetupChargeInjection( EChannels* channel, unsigned int nFEBs );
void SetupGenericFEBSettings( EChannels* channel, unsigned int nFEBs );
void FPGAWriteConfiguredFrame( EChannels* channel, FEB* feb );
void FPGASetupForChargeInjection( EChannels* channel, int boardID );
void TRIPSetupForChargeInjection( EChannels* channel, int boardID );
void FPGASetupForGeneric( EChannels* channel, int boardID );
void TRIPSetupForGeneric( EChannels* channel, int boardID );
void TestChannel( ECROC* ecroc, unsigned int channelNumber, unsigned int nFEBs );
ECROC * GetAndTestECROC( unsigned int address, Controller * controller );
Controller * GetAndTestController( int address, int crateNumber );


#endif
