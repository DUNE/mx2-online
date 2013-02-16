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

  Controller * controller = GetAndTestController( 0x00, controllerID );
  ECROC * ecroc = GetAndTestECROC( ecrocCardAddress, controller );
  TestChannel( ecroc, channel, nFEBs );
  EChannels * echannel = ecroc->GetChannel( channel ); 
  SetupChargeInjection( echannel, nFEBs );
  unsigned short int pointer = ReadDPMTestPointer( ecroc, channel, nFEBs ); 
  unsigned char * dataBuffer = ReadDPMTestData( ecroc, channel, nFEBs, pointer ); 

  /* std::cout << "\n" << sizeof( dataBuffer )/sizeof( unsigned char ) << std::endl; */
  delete [] dataBuffer;
  delete ecroc;
  delete controller;

  std::cout << "Passed all tests! Executed " << testCount << " tests." << std::endl;
  return 0;
}


//---------------------------------------------------
unsigned char * ReadDPMTestData( ECROC * ecroc, unsigned int channel, unsigned int nFEBs, unsigned short pointer ) 
{
  std::cout << "Testing ReadDPM Data... ";  

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
  std::cout << "Testing ReadDPM Pointer... ";  

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
void FPGAWriteConfiguredFrame( EChannels* channel, FEB* feb )
{
  channel->ClearAndResetStatusRegister();
  channel->WriteFPGAProgrammingRegistersToMemory( feb );
  channel->SendMessage();
  channel->WaitForMessageReceived();
  /* unsigned short dataLength = channel->ReadDPMPointer(); */
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
    assert( dataLength == TRiPProgrammingFrameReadSize ); 
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
    feb->SetGateStart(42938);
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
      feb->GetTrip(i)->SetRegisterValue( 9, DefaultTripRegisterValues.tripRegVTH );
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
    std::cout << "TRIPSetupForGeneric dataLength = " << dataLength << std::endl;
    logger.debugStream() << "FEB " << boardID << "; Status = 0x" << std::hex << status 
      << "; TRIPSetupForGeneric dataLength = " << std::dec << dataLength;
    assert( dataLength == TRiPProgrammingFrameReadSize ); 
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
    feb->SetGateStart(40938);
    feb->SetGateLength( 1600 );
    feb->SetHVPeriodManual(44337);
    feb->SetHVTarget(25000);
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
