#ifndef TestSuite_h
#define TestSuite_h
/*! 
  \file TestSuite.h
  \brief Header file for the unit tests sequence.
  \author Gabriel Perdue

  The tests cannot be run in any order - there is a specific order.
  */

#include <tr1/memory> 

#include "log4cppHeaders.h"

#include "Controller.h"
#include "EChannelsConfigRegParser.h"
#include "ECROC.h"
#include "CRIM.h"
#include "FrontEndBoard.h"
#include "SequencerReadoutBlock.h"

#include "ReadoutWorker.h"
#include "ReadoutStateRecorder.h"
#include "DAQWorker.h"
#include "DAQArgs.h"

#include <sqlite3.h>

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
    unsigned int nFEBs, unsigned int pointer );
unsigned short int ReadDPMTestPointer( ECROC * ecroc, unsigned int channel, 
    unsigned int nFEBs );

// This test should be called eigth.
void SequencerReadoutBlockTest( unsigned char * data, unsigned short dataLength );

// This test should be called ninth.
void ReadADCTest( EChannels* channel, unsigned int nFEBs );

// This test should be called tenth.
void ReadDiscrTest( EChannels* channel, unsigned int nFEBs );

// This test should be called eleventh.
CRIM * GetAndTestCRIM( unsigned int address, Controller * controller );

// This test should be called 12th.
void TestSQLiteTemp();

// This test should be called 13th.
void TestSQLite( EChannels *channel );

// This test should be called 14th
void TestVMECrate( int crateNumber );  

// This test should be called 15th.
ReadoutWorker * GetAndTestReadoutWorker( int controllerID, unsigned int ecrocCardAddress, 
    unsigned int crimCardAddress, int nch0, int nch1, int nch2, int nch3);

// This test should be called 16th.
void TestDAQWorker( DAQWorker * worker );

// This test should be called 17th.
void TestReadoutStateRecorder();


//--------------------------------------------------------------------------------------
// Helper Functions - not tests per se.
void FPGAWriteConfiguredFrame( EChannels* channel, std::tr1::shared_ptr<FPGAFrame> frame );
void FPGASetupForChargeInjection( EChannels* channel, int boardID );
void TRIPSetupForChargeInjection( EChannels* channel, int boardID );
void FPGASetupForGeneric( EChannels* channel, int boardID );
void TRIPSetupForGeneric( EChannels* channel, int boardID );

#endif
