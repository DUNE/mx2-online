#ifndef TestSuite_h
#define TestSuite_h

#include "log4cppHeaders.h"

#include "MinervaDAQtypes.h"
#include "Controller.h"
#include "ECROC.h"

// The tests cannot be run in any order - there is a specific order.

// This test should be called first.
Controller * GetAndTestController( int address, int crateNumber );

// This test should be called second.
ECROC * GetAndTestECROC( unsigned int address, Controller * controller );

// This test should be called third.
void TestChannel( ECROC* ecroc, unsigned int channelNumber, unsigned int nFEBs );

// These tests are coupled and should be called back-to-back-to-back. 
// They should be called as a set as the fourth & fifth tests.
void SetupGenericFEBSettings( EChannels* channel, unsigned int nFEBs );
void FEBTRiPWriteReadTest( EChannels* channel, unsigned int nFEBs );
void FEBFPGAWriteReadTest( EChannels* channel, unsigned int nFEBs );

// These tests are coupled and should be called back-to-back-to-back. 
// We use the pointer from one test in the other.
// They should be called as a set as the sixth & seventh tests.
void SetupChargeInjection( EChannels* channel, unsigned int nFEBs );
unsigned char * ReadDPMTestData( ECROC * ecroc, unsigned int channel, 
    unsigned int nFEBs, unsigned short pointer );
unsigned short int ReadDPMTestPointer( ECROC * ecroc, unsigned int channel, 
    unsigned int nFEBs );

// This test should be called eigth.
void ReadADCTest( EChannels* channel, unsigned int nFEBs );

// This test should be called ninth.
void ReadDiscrTest( EChannels* channel, unsigned int nFEBs );

// Helper Functions - not tests per se.
void FPGAWriteConfiguredFrame( EChannels* channel, FEB* feb );
void FPGASetupForChargeInjection( EChannels* channel, int boardID );
void TRIPSetupForChargeInjection( EChannels* channel, int boardID );
void FPGASetupForGeneric( EChannels* channel, int boardID );
void TRIPSetupForGeneric( EChannels* channel, int boardID );

#endif
