#ifndef TestSuite_cxx
#define TestSuite_cxx

#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>

#include <assert.h>
#include <sys/time.h>

#include "TestSuite.h"

const std::string thisScript = "TestSuite";
log4cpp::Appender* appender;
log4cpp::Category& root   = log4cpp::Category::getRoot();
log4cpp::Category& logger = log4cpp::Category::getInstance( thisScript );

static int testCount = 0;

// We expect 1298 per Board == 68 (FPGA) + 2 x 446 (ADC Frames w/ Discr. Hits) + 338
// 338 == 18 + 40 per hit per TRiP
// At some point, we expect 3 x 446 bytes for ADC Frames when the Channel reads
// the "un-timed" hit buffer as well (N+1 readout mode).
static const int chgInjReadoutBytesPerBoard = FPGAFrameMaxSize + 2*ADCFrameMaxSize + 338;

static const unsigned short genericGateStart = 40938;
static const unsigned short genericHVTarget = 25000;
static const unsigned short genericGateLength = 1600;
static const unsigned short genericHVPeriodManual = 35000;
static const unsigned short genericDiscEnableMask = 0xFFFF;
static const unsigned int   genericTimer = 12;

int main( int argc, char * argv[] ) 
{
  std::cout << "Starting test suite..." << std::endl;

  if (argc < 2) {
    std::cout << "Usage : " << thisScript
      << " -c <CROC-E Address> -h <CHANNEL Number 0-3> -f <Number of FEBs>" 
      << std::endl;
    exit(0);
  }

  unsigned int ecrocCardAddress = 1;
  unsigned int channel          = 0;
  unsigned int nFEBs            = 5; // USE SEQUENTIAL ADDRESSING!!!
  int controllerID              = 0;

  // Process the command line argument set. opt index == 0 is the executable.
  int optind = 1;
  printf("Arguments: ");
  while ((optind < argc) && (argv[optind][0]=='-')) {
    std::string sw = argv[optind];
    if (sw=="-c") {
      optind++;
      ecrocCardAddress = (unsigned int)atoi(argv[optind]);
      printf(" CROC-E Address = %03d ", ecrocCardAddress);
    }
    else if (sw=="-h") {
      optind++;
      channel = (unsigned int)( atoi(argv[optind]) );
      printf(" CROC-E Channel = %1d ", channel);
    }
    else if (sw=="-f") {
      optind++;
      nFEBs = (unsigned int)atoi(argv[optind]);
      printf(" Number of FEBs = %02d ", nFEBs);
    }
    else
      std::cout << "\nUnknown switch: " << argv[optind] << std::endl;
    optind++;
  }
  std::cout << std::endl;
  if (optind < argc) {
    std::cout << "There were remaining arguments!  Are you sure you set the run up correctly?" << std::endl;
    std::cout << "  Remaining arguments = ";
    for (;optind<argc;optind++) std::cout << argv[optind];
    std::cout << std::endl;
  }

  std::string logName = "/work/data/logs/" + thisScript + ".txt";
  appender = new log4cpp::FileAppender( "default", logName, false ); //  cryptic false = do not append
  appender->setLayout(new log4cpp::BasicLayout());
  root.addAppender(appender);
  root.setPriority(log4cpp::Priority::ERROR);
  logger.setPriority(log4cpp::Priority::DEBUG);
  logger.infoStream() << "--Starting " << thisScript << " Script.--";

  // Get & initialize a Controller object.
  Controller * controller = GetAndTestController( 0x00, controllerID );

  // Get & initialize a CROC-E.
  ECROC * ecroc = GetAndTestECROC( ecrocCardAddress, controller );

  // Test that the specified number of FEBs are available & set up the channel.
  TestChannel( ecroc, channel, nFEBs );

  // Grab a pointer to our configured channel for later use.
  EChannels * echannel = ecroc->GetChannel( channel ); 

  // Write some generic values to the FEB that are different than what we use 
  // for charge injection and different from the power on defaults. Then read them 
  // back over the course of the next two tests.
  SetupGenericFEBSettings( echannel, nFEBs );
  FEBFPGAWriteReadTest( echannel, nFEBs );
  FEBTRiPWriteReadTest( echannel, nFEBs );

  // Set up charge injection and read the data. We test for data sizes equal 
  // to what we expect. Get a copy of the buffer and its size for parsing.
  SetupChargeInjection( echannel, nFEBs );
  unsigned short int pointer = ReadDPMTestPointer( ecroc, channel, nFEBs ); 
  unsigned char * dataBuffer = ReadDPMTestData( ecroc, channel, nFEBs, pointer ); 

  // Read the ADC and parse them.
  ReadADCTest( echannel, nFEBs );

  // Read the Discriminators and parse them.
  ReadDiscrTest( echannel, nFEBs );

  /* std::cout << "\n" << sizeof( dataBuffer )/sizeof( unsigned char ) << std::endl; */
  delete [] dataBuffer;
  delete ecroc;
  delete controller;

  std::cout << "Passed all tests! Executed " << testCount << " tests." << std::endl;
  return 0;
}


//---------------------------------------------------
void ReadDiscrTest( EChannels* channel, unsigned int nFEBs )
{
  std::cout << "Testing Read Discrs...";  

  for (unsigned int nboard = 1; nboard <= 1/*nFEBs*/; nboard++) {

    channel->ClearAndResetStatusRegister();

    // Recall the FEB vect attached to the channel is indexed from 0.
    int vectorIndex = nboard - 1;
    FEB *feb = channel->GetFEBVector( vectorIndex );

    channel->WriteMessageToMemory( feb->GetDisc()->GetOutgoingMessage(), 
        feb->GetDisc()->GetMessageSize() );
    channel->SendMessage();
    unsigned short status = channel->WaitForMessageReceived();
    assert( 0x1010 == status );
    unsigned short pointer = channel->ReadDPMPointer();
    assert( 18/*header*/ + 2/*nhits*/*4/*ntrips*/*40/*bytes/trip*/ == pointer ); 
    unsigned char* data = channel->ReadMemory( pointer );

    feb->GetDisc()->message = data;
    assert( !feb->GetDisc()->CheckForErrors() );
    assert( !feb->GetDisc()->DecodeRegisterValues((int)0)); 
    for (unsigned int i = 0; i < 4; ++i) 
      assert( 2 == feb->GetDisc()->GetNHitsOnTRiP(i) );

    feb->GetDisc()->printMessageBufferToLog(pointer);
    feb->GetDisc()->message = 0;
    delete [] data;
  }

  std::cout << "Passed!" << std::endl;
  testCount++;
}


//---------------------------------------------------
void ReadADCTest( EChannels* channel, unsigned int nFEBs )
{
  std::cout << "Testing Read ADCs...";  

  int iHit = 1; // 0 - 1 should be charge injected

  for (unsigned int nboard = 1; nboard <= nFEBs; nboard++) {

    channel->ClearAndResetStatusRegister();

    // Recall the FEB vect attached to the channel is indexed from 0.
    int vectorIndex = nboard - 1;
    FEB *feb = channel->GetFEBVector( vectorIndex );

    channel->WriteMessageToMemory( feb->GetADC(iHit)->GetOutgoingMessage(), 
        feb->GetADC(iHit)->GetMessageSize() );
    channel->SendMessage();
    unsigned short status = channel->WaitForMessageReceived();
    assert( 0x1010 == status );
    unsigned short pointer = channel->ReadDPMPointer();
    assert( ADCFrameMaxSize == pointer ); 
    unsigned char* data = channel->ReadMemory( pointer );

    feb->GetADC(iHit)->message = data;
    assert( !feb->GetADC(iHit)->CheckForErrors() );
    assert( !feb->GetADC(iHit)->DecodeRegisterValues((int)90)); // 90 == FEB firmware ver, for now...
    feb->GetADC(iHit)->message = 0;
    delete [] data;

  }

  std::cout << "Passed!" << std::endl;
  testCount++;
}


//---------------------------------------------------
unsigned char * ReadDPMTestData( ECROC * ecroc, unsigned int channel, unsigned int nFEBs, unsigned short pointer ) 
{
  std::cout << "Testing ReadDPM Data...";  

  EChannels * echannel = ecroc->GetChannel( channel );
  assert( nFEBs == echannel->GetFEBVector()->size() );

  unsigned short counter = echannel->ReadEventCounter();
  logger.infoStream() << " After open gate, event counter = " << counter;
  assert( 0 != counter );
  unsigned char* dataBuffer = echannel->ReadMemory( pointer );
  logger.debugStream() << "Data: -----------------------------";
  for (unsigned int i=0; i<pointer; i+=2 ) {
    unsigned int j = i + 1;
    logger.debugStream()
      << std::setfill('0') << std::setw( 2 ) << std::hex << (int)dataBuffer[i] << " "
      << std::setfill('0') << std::setw( 2 ) << std::hex << (int)dataBuffer[j] << " "
      << "\t"
      << std::setfill('0') << std::setw( 5 ) << std::dec << i << " "
      << std::setfill('0') << std::setw( 5 ) << std::dec << j;
  }
  ecroc->DisableSequencerReadout();

  std::cout << "Passed!" << std::endl;
  testCount++;
  return dataBuffer;
}

//---------------------------------------------------
unsigned short int ReadDPMTestPointer( ECROC * ecroc, unsigned int channel, unsigned int nFEBs )
{
  std::cout << "Testing ReadDPM Pointer...";  

  ecroc->ClearAndResetStatusRegisters();
  EChannels * echannel = ecroc->GetChannel( channel );
  assert( nFEBs == echannel->GetFEBVector()->size() );

  unsigned short pointer = echannel->ReadDPMPointer();
  /* std::cout << "\n After reset, pointer = " << pointer << std::endl; */
  assert( (0 == pointer) || (1 == pointer) );  // ??? 1 ???
  ecroc->FastCommandOpenGate();
  ecroc->EnableSequencerReadout();
  ecroc->SendSoftwareRDFE();

  echannel->WaitForSequencerReadoutCompletion();
  pointer = echannel->ReadDPMPointer();
  /* std::cout << "\n After open gate, pointer = " << pointer << std::endl; */
  logger.infoStream() << " After open gate, pointer = " << pointer;
  assert( chgInjReadoutBytesPerBoard * nFEBs == pointer );

  std::cout << "Passed!" << std::endl;
  testCount++;
  return pointer;


}

//---------------------------------------------------
void SetupGenericFEBSettings( EChannels* channel, unsigned int nFEBs )
{
  // This is not exactly a test, per se. If the setup is 
  // done incorrectly, it will show in *later* tests.
  for (unsigned int nboard = 1; nboard <= nFEBs; nboard++) {
    FPGASetupForGeneric( channel, nboard );
    TRIPSetupForGeneric( channel, nboard );
  }
}

//---------------------------------------------------
void SetupChargeInjection( EChannels* channel, unsigned int nFEBs )
{
  // This is not exactly a test, per se. If the setup is 
  // done incorrectly, it will show in *later* tests.
  for (unsigned int nboard = 1; nboard <= nFEBs; nboard++) {
    FPGASetupForChargeInjection( channel, nboard );
    TRIPSetupForChargeInjection( channel, nboard );
  }
}

//---------------------------------------------------
void FEBFPGAWriteReadTest( EChannels* channel, unsigned int nFEBs )
{
  std::cout << "Testing FEB FPGA Read back...";  
  logger.debugStream() << "FEBFPGAWriteReadTest";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress();

  for (unsigned int nboard = 1; nboard <= nFEBs; nboard++) {
    // Recall the FEB vect attached to the channel is indexed from 0.
    int vectorIndex = nboard - 1;

    FEB *feb = channel->GetFEBVector( vectorIndex );

    // Re-set to defaults (to make sure we read new values in).
    feb->SetFEBDefaultValues();

    // ReadFPGAProgrammingRegisters sets up the message and reads the data into the channel memory...
    unsigned short dataLength = channel->ReadFPGAProgrammingRegistersToMemory( feb );
    assert( dataLength == FPGAFrameMaxSize );
    // ...then ReadMemory retrieves the data.
    unsigned char * dataBuffer = channel->ReadMemory( dataLength );
    feb->message = dataBuffer;
    feb->DecodeRegisterValues(dataLength);
    feb->printMessageBufferToLog(dataLength);
    logger.debugStream() << "We read fpga's for feb " << (int)feb->GetBoardID();
    feb->ShowValues();

    assert( FPGA == feb->GetDeviceType() ); 
    assert( nboard == (unsigned int)feb->GetFEBNumber() );
    assert( genericTimer == feb->GetTimer() );
    assert( genericGateStart == feb->GetGateStart() );
    assert( genericHVTarget == feb->GetHVTarget() );
    assert( genericGateLength == feb->GetGateLength() );
    assert( genericHVPeriodManual == feb->GetHVPeriodManual() );
    assert( genericDiscEnableMask == feb->GetDiscEnMask0() );
    assert( genericDiscEnableMask == feb->GetDiscEnMask1() );
    assert( genericDiscEnableMask == feb->GetDiscEnMask2() );
    assert( genericDiscEnableMask == feb->GetDiscEnMask3() );

    feb->message = 0;
    delete [] dataBuffer;
  }
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void FEBTRiPWriteReadTest( EChannels* channel, unsigned int nFEBs )
{
  std::cout << "Testing TRiP Read back...";  

  for (unsigned int boardID = 1; boardID <= nFEBs; boardID++ ) {
    int vectorIndex = boardID - 1;
    FEB *feb = channel->GetFEBVector( vectorIndex );

    for ( int i=0; i<6 /* 6 trips per FEB */; i++ ) {
      // Clear Status & Reset
      channel->ClearAndResetStatusRegister();

      // Set up the message... (just to look at)
      feb->GetTrip(i)->SetRead(true);
      feb->GetTrip(i)->MakeMessage();
      unsigned int tmpML = feb->GetTrip(i)->GetMessageSize();
      assert( TRiPProgrammingFrameReadSize == tmpML );

      std::stringstream ss;
      ss << "Trip " << i << std::endl;
      unsigned char *message = feb->GetTrip(i)->GetOutgoingMessage();
      for (unsigned int j = 0; j < tmpML; j +=4 ) {
        ss << j << "\t" << (int)message[j];
        if (j+1 < tmpML) ss << "\t" << (int)message[j+1];
        if (j+2 < tmpML) ss << "\t" << (int)message[j+2];
        if (j+3 < tmpML) ss << "\t" << (int)message[j+3];
        ss << std::endl;
      }
      assert( message[0] == (unsigned char)boardID );
      assert( message[2] == 0 );
      assert( message[3] == 0 );
      message = 0;
      feb->GetTrip(i)->DeleteOutgoingMessage();

      // remake the message internally
      channel->WriteTRIPRegistersReadFrameToMemory( feb, i );
      channel->SendMessage();
      unsigned short status = channel->WaitForMessageReceived();
      unsigned short dataLength = channel->ReadDPMPointer();
      logger.debugStream() << "FEB " << boardID << "; Status = 0x" << std::hex << status 
        << "; TRIPSetupForChargeInjection dataLength = " << std::dec << dataLength;
      assert( dataLength == TRiPProgrammingFrameReadResponseSize ); 

      for (unsigned int k=0;k<14;k++) {
        ss << "Trip Register " << k << "; Value = " << 
          (int)feb->GetTrip(i)->GetTripValue(k) << std::endl;
      }
      logger.debugStream() << ss.str();
      assert( 0 == feb->GetTrip(i)->GetTripValue(9) );  // we set this
    }
  }
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void FPGAWriteConfiguredFrame( EChannels* channel, FEB* feb )
{
  channel->ClearAndResetStatusRegister();
  channel->WriteFPGAProgrammingRegistersToMemory( feb );
  channel->SendMessage();
  channel->WaitForMessageReceived();
}

//---------------------------------------------------
void TRIPSetupForChargeInjection( EChannels* channel, int boardID )
{
  // No real point in reading and decoding the response frame - the TRiP's send 
  // a response frame composed entirely of zeroes when being *written* to.        
  logger.debugStream() << "TRIPSetup for Charge Injection";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress()
    << std::dec << "; FEB Addr = " << boardID;

  int vectorIndex = boardID - 1;
  FEB *feb = channel->GetFEBVector( vectorIndex );

  for ( int i=0; i<6 /* 6 trips per FEB */; i++ ) {
    // Clear Status & Reset
    channel->ClearAndResetStatusRegister();

    // Set up the message...
    feb->GetTrip(i)->SetRead(false);
    {
      feb->GetTrip(i)->SetRegisterValue( 0, DefaultTripRegisterValues.tripRegIBP );
      feb->GetTrip(i)->SetRegisterValue( 1, DefaultTripRegisterValues.tripRegIBBNFOLL );
      feb->GetTrip(i)->SetRegisterValue( 2, DefaultTripRegisterValues.tripRegIFF );
      feb->GetTrip(i)->SetRegisterValue( 3, DefaultTripRegisterValues.tripRegIBPIFF1REF );
      feb->GetTrip(i)->SetRegisterValue( 4, DefaultTripRegisterValues.tripRegIBOPAMP );
      feb->GetTrip(i)->SetRegisterValue( 5, DefaultTripRegisterValues.tripRegIB_T );
      feb->GetTrip(i)->SetRegisterValue( 6, DefaultTripRegisterValues.tripRegIFFP2 );
      feb->GetTrip(i)->SetRegisterValue( 7, DefaultTripRegisterValues.tripRegIBCOMP );
      feb->GetTrip(i)->SetRegisterValue( 8, DefaultTripRegisterValues.tripRegVREF );
      feb->GetTrip(i)->SetRegisterValue( 9, DefaultTripRegisterValues.tripRegVTH );
      feb->GetTrip(i)->SetRegisterValue(10, DefaultTripRegisterValues.tripRegPIPEDEL);
      feb->GetTrip(i)->SetRegisterValue(11, DefaultTripRegisterValues.tripRegGAIN );
      feb->GetTrip(i)->SetRegisterValue(12, DefaultTripRegisterValues.tripRegIRSEL );
      feb->GetTrip(i)->SetRegisterValue(13, DefaultTripRegisterValues.tripRegIWSEL );
      feb->GetTrip(i)->SetRegisterValue(14, 0x1FE ); //inject, enable first words, 0x1FFFE for two...
      // Injection patterns:
      // ~~~~~~~~~~~~~~~~~~~
      // Funny structure... 34 bits... using "FermiDAQ" nomenclature...
      // InjEx0: 1 bit (extra channel - ignore)
      // InjB0: Byte 0 - 8 bits - visible to HIGH and LOW gain ->(mask) 0x1FE (0xFF<<1)
      // InjB1: Byte 1 - 8 bits - visible to HIGH and LOW gain ->(mask) 0x1FE00 (0xFF<<1)<<8
      // InjB2: Byte 2 - 8 bits - visible to MEDIUM and LOW gain ->(mask) 0x1FE0000, etc.
      // InjB3: Byte 3 - 8 bits - visible to MEDIUM and LOW gain ->(mask) 0x1FE000000, etc.
      // InjEx33: 1 bit (extra channel - ignore)
      // 
      // The high and medium gain channel mappings are
      // straightforward:
      // B0+B1 -> 16 bits -> 16 (qhi) chs in sequence for each of the trips 0-3
      // B2+B3 -> 16 bits -> 16 (qmed) chs in sequence for each of the trips 0-3
      // 
      // The low gain channel mappings are more complicated. See comments in DecodeRawEvent
      // in the MINERvA Framework.  To write to all 32 channels, we need to write to B0+B1+B2+B3.
      //
      // Note that we are writing to individual TriP's here! To get a different pattern in 
      // "pixels" 0-15 && 16-31, you need to write something to TriP 0 and something 
      // different to TriP 1, etc.
    }

    channel->WriteTRIPRegistersToMemory( feb, i );
    channel->SendMessage();
    unsigned short status = channel->WaitForMessageReceived();
    unsigned short dataLength = channel->ReadDPMPointer();
    logger.debugStream() << "FEB " << boardID << "; Status = 0x" << std::hex << status 
      << "; TRIPSetupForChargeInjection dataLength = " << std::dec << dataLength;
    assert( dataLength == TRiPProgrammingFrameWriteResponseSize ); 
  }
}

//---------------------------------------------------
void FPGASetupForChargeInjection( EChannels* channel, int boardID )
{
  logger.debugStream() << "FPGASetup for Charge Injection";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress()
    << std::dec << "; FEB Addr = " << boardID;

  int vectorIndex = boardID - 1;
  FEB *feb = channel->GetFEBVector( vectorIndex );
  {
    struct timeval sTimeVal;
    gettimeofday(&sTimeVal,NULL);
    unsigned int gateTimeMod = sTimeVal.tv_sec % 1000;
    unsigned char val[]={0x0};
    feb->SetTripPowerOff(val);
    feb->SetGateStart(41938);
    // we should see something different call to call
    feb->SetGateLength( 1000 + gateTimeMod );
    feb->SetHVPeriodManual(41337);
    feb->SetHVTarget(25000);
    unsigned char previewEnable[] = {0x0};
    feb->SetPreviewEnable(previewEnable);
    // inject registers, DON'T ENABLE THE LOW GAIN TRIPS!
    for (int i=0; i<4; i++) {
      // try to get hits in different windows (need ~35+ ticks) 
      unsigned char inj[] = { 1 + (unsigned char)i*(40) + 2*((int)boardID) };
      unsigned char enable[] = {0x1};
      feb->SetInjectCount(inj,i);
      feb->SetInjectEnable(enable,i);
      feb->SetDiscrimEnableMask(0xFFFF,i);
    }
    unsigned short int dacval = 4000;
    feb->SetInjectDACValue(dacval);
    unsigned char injPhase[] = {0x1};
    feb->SetInjectPhase(injPhase);
    // Change FEB fpga function to write
    Devices dev     = FPGA;
    Broadcasts b    = None;
    Directions d    = MasterToSlave;
    FPGAFunctions f = Write;
    feb->MakeDeviceFrameTransmit(dev,b,d,f, (unsigned int)feb->GetBoardNumber());
  }
  FPGAWriteConfiguredFrame( channel, feb );

  // Set up DAC
  unsigned char injStart[] = {0x1};
  feb->SetInjectDACStart(injStart);
  FPGAWriteConfiguredFrame( channel, feb );

  // Reset DAC Start
  unsigned char injReset[] = {0x0};
  feb->SetInjectDACStart(injReset);
  FPGAWriteConfiguredFrame( channel, feb );
}

//---------------------------------------------------
void TRIPSetupForGeneric( EChannels* channel, int boardID )
{
  // No real point in reading and decoding the response frame - the TRiP's send 
  // a response frame composed entirely of zeroes when being *written* to.        
  logger.debugStream() << "TRIPSetup for Generic Settings";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress()
    << std::dec << "; FEB Addr = " << boardID;

  int vectorIndex = boardID - 1;
  FEB *feb = channel->GetFEBVector( vectorIndex );

  for ( int i=0; i<6 /* 6 trips per FEB */; i++ ) {
    // Clear Status & Reset
    channel->ClearAndResetStatusRegister();

    // Set up the message...
    feb->GetTrip(i)->SetRead(false);
    {
      feb->GetTrip(i)->SetRegisterValue( 0, DefaultTripRegisterValues.tripRegIBP );
      feb->GetTrip(i)->SetRegisterValue( 1, DefaultTripRegisterValues.tripRegIBBNFOLL );
      feb->GetTrip(i)->SetRegisterValue( 2, DefaultTripRegisterValues.tripRegIFF );
      feb->GetTrip(i)->SetRegisterValue( 3, DefaultTripRegisterValues.tripRegIBPIFF1REF );
      feb->GetTrip(i)->SetRegisterValue( 4, DefaultTripRegisterValues.tripRegIBOPAMP );
      feb->GetTrip(i)->SetRegisterValue( 5, DefaultTripRegisterValues.tripRegIB_T );
      feb->GetTrip(i)->SetRegisterValue( 6, DefaultTripRegisterValues.tripRegIFFP2 );
      feb->GetTrip(i)->SetRegisterValue( 7, DefaultTripRegisterValues.tripRegIBCOMP );
      feb->GetTrip(i)->SetRegisterValue( 8, DefaultTripRegisterValues.tripRegVREF );
      feb->GetTrip(i)->SetRegisterValue( 9, 0 ); // we'll turn the TRiPs on before we do chg inj
      feb->GetTrip(i)->SetRegisterValue(10, DefaultTripRegisterValues.tripRegPIPEDEL);
      feb->GetTrip(i)->SetRegisterValue(11, DefaultTripRegisterValues.tripRegGAIN );
      feb->GetTrip(i)->SetRegisterValue(12, DefaultTripRegisterValues.tripRegIRSEL );
      feb->GetTrip(i)->SetRegisterValue(13, DefaultTripRegisterValues.tripRegIWSEL );
      feb->GetTrip(i)->SetRegisterValue(14, 0x0 ); 
    }

    channel->WriteTRIPRegistersToMemory( feb, i );
    channel->SendMessage();
    unsigned short status = channel->WaitForMessageReceived();
    unsigned short dataLength = channel->ReadDPMPointer();
    logger.debugStream() << "FEB " << boardID << "; Status = 0x" << std::hex << status 
      << "; TRIPSetupForGeneric dataLength = " << std::dec << dataLength;
    assert( dataLength == TRiPProgrammingFrameWriteResponseSize ); 
  }
}

//---------------------------------------------------
void FPGASetupForGeneric( EChannels* channel, int boardID )
{
  logger.debugStream() << "FPGASetup for Generic Settings";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress()
    << std::dec << "; FEB Addr = " << boardID;

  int vectorIndex = boardID - 1;
  FEB *feb = channel->GetFEBVector( vectorIndex );
  {
    unsigned char val[]={0x0};
    feb->SetTripPowerOff(val);
    feb->SetTimer( genericTimer );
    feb->SetGateStart( genericGateStart );
    feb->SetGateLength( genericGateLength );
    feb->SetHVPeriodManual( genericHVPeriodManual );
    feb->SetHVTarget( genericHVTarget );
    unsigned char previewEnable[] = {0x0};
    feb->SetPreviewEnable(previewEnable);
    for (int i=0; i<4; i++) {
      unsigned char inj[] = { 1 + (unsigned char)i*(2) + 2*((int)boardID) };
      unsigned char enable[] = {0x0};
      feb->SetInjectCount(inj,i);
      feb->SetInjectEnable(enable,i);
      feb->SetDiscrimEnableMask(0xFFFF,i);
    }
    unsigned short int dacval = 0;
    feb->SetInjectDACValue(dacval);
    unsigned char injPhase[] = {0x0};
    feb->SetInjectPhase(injPhase);
    // Change FEB fpga function to write
    Devices dev     = FPGA;
    Broadcasts b    = None;
    Directions d    = MasterToSlave;
    FPGAFunctions f = Write;
    feb->MakeDeviceFrameTransmit(dev,b,d,f, (unsigned int)feb->GetBoardNumber());
    assert( FPGA == feb->GetDeviceType() ); 
    assert( boardID == feb->GetFEBNumber() );
    assert( FrameHeaderLengthOutgoing + FPGANumRegisters == feb->GetOutgoingMessageLength() );
    assert( genericTimer == feb->GetTimer() );
    assert( genericGateStart == feb->GetGateStart() );
    assert( genericHVTarget == feb->GetHVTarget() );
    assert( genericGateLength == feb->GetGateLength() );
    assert( genericHVPeriodManual == feb->GetHVPeriodManual() );
    assert( genericDiscEnableMask == feb->GetDiscEnMask0() );
    assert( genericDiscEnableMask == feb->GetDiscEnMask1() );
    assert( genericDiscEnableMask == feb->GetDiscEnMask2() );
    assert( genericDiscEnableMask == feb->GetDiscEnMask3() );
  }
  FPGAWriteConfiguredFrame( channel, feb );
}

//---------------------------------------------------
void TestChannel( ECROC* ecroc, unsigned int channelNumber, unsigned int nFEBs )
{
  std::cout << "Testing ECROC Channel...";  

  EChannels * channel = ecroc->GetChannel( channelNumber );
  assert( channel != NULL );
  assert( channel->GetChannelNumber() == channelNumber );
  assert( channel->GetParentECROCAddress() == ecroc->GetAddress() );
  assert( channel->GetParentCROCNumber() == (ecroc->GetAddress() >> ECROCAddressShift) );
  assert( channel->GetDirectAddress() == 
      ecroc->GetAddress() + EChannelOffset * (unsigned int)(channelNumber) );
  channel->SetupNFEBs( nFEBs );
  assert( channel->GetFEBVector()->size() == nFEBs ); 
  channel->ClearAndResetStatusRegister();
  unsigned short status = channel->ReadFrameStatusRegister();
  assert( /* (status == 0x1010) || */ (status == 0x4040) );
  assert( channel->ReadTxRxStatusRegister() == 0x2410 );

  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
ECROC * GetAndTestECROC( unsigned int address, Controller * controller )
{
  std::cout << "Testing Get and Test ECROC...";  
  if (address < (1<<ECROCAddressShift)) {
    address = address << ECROCAddressShift;
  }
  ECROC * ecroc = new ECROC( address, controller );

  assert( ecroc->GetAddress() == address );
  // These methods are void. Not clear it makes sense to call all 
  // public CROCE methods since they're talking to the hardware.
  ecroc->Initialize();
  ecroc->ClearAndResetStatusRegisters();
  ecroc->EnableSequencerReadout();
  ecroc->DisableSequencerReadout();

  std::cout << "Passed!" << std::endl;
  testCount++;
  return ecroc;
}

//---------------------------------------------------
Controller * GetAndTestController( int address, int crateNumber )
{
  std::cout << "Testing Get and Test Controller...";  
  Controller * controller = new Controller( address, crateNumber );

  assert( controller->Initialize() == 0 );
  assert( controller->GetAddress() == (unsigned int)address );
  assert( controller->GetCrateNumber() == crateNumber );

  std::cout << "Passed!" << std::endl;
  testCount++;
  return controller;
}

#endif
