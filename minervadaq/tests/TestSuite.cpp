#ifndef TestSuite_cxx
#define TestSuite_cxx
/*! 
  \file TestSuite.cpp
  \brief Implementation file for the unit tests.
  \author Gabriel Perdue
*/

#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>

#include <assert.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <unistd.h>

#include "ReadoutTypes.h"
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
static const int chgInjReadoutBytesPerBoard = MinervaDAQSizes::FPGAFrameMaxSize + 
  3*MinervaDAQSizes::ADCFrameMaxSize + 344 + 1;//344;

static const unsigned short genericGateStart = 40938;
static const unsigned short genericHVTarget = 25000;
static const unsigned short genericGateLength = 1600;
static const unsigned short genericHVPeriodManual = 35000;
static const unsigned short genericDiscEnableMask = 0xFFFF;
static const unsigned int   genericTimer = 12;

static const Modes::RunningModes runningMode = Modes::OneShot;

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
  unsigned int crimCardAddress  = 224;
  unsigned int channel          = 1;
  unsigned int nFEBs            = 5; // USE SEQUENTIAL ADDRESSING!!!
  int nch0 = 0, nch1 = 0, nch2 = 0, nch3 = 0;

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
    else if (sw=="-r") {
      optind++;
      crimCardAddress = (unsigned int)atoi(argv[optind]);
      printf(" CRIM Address = %03d ", crimCardAddress);
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
  if (channel == 0) nch0 = nFEBs;
  if (channel == 1) nch1 = nFEBs;
  if (channel == 2) nch2 = nFEBs;
  if (channel == 3) nch3 = nFEBs;

  std::string logName = "/work/data/logs/" + thisScript + ".txt";
  struct DAQWorkerArgs * args = DAQArgs::DefaultArgs();
  args->numberOfGates = 2;
  args->logFileName = logName;

  appender = new log4cpp::FileAppender( "default", args->logFileName, false ); //  cryptic false = do not append
  appender->setLayout(new log4cpp::BasicLayout());
  root.addAppender(appender);
  root.setPriority(log4cpp::Priority::ERROR);
  logger.setPriority(log4cpp::Priority::DEBUG);
  logger.infoStream() << "--Starting " << thisScript << " Script.--";

  struct timeval run;
  gettimeofday(&run, NULL);
  unsigned long long start = (unsigned long long)(run.tv_sec*1000000)
    + (unsigned long long)(run.tv_usec);

  int controllerID = 0;

  // Get & initialize a Controller object.
  Controller * controller = GetAndTestController( 0x00, controllerID );

  // Get & initialize a CROC-E.
  ECROC * ecroc = GetAndTestECROC( ecrocCardAddress, controller );

  std::cout << "== After GetAndTestECROC. " << std::endl;  

  // Test that the specified number of FEBs are available & set up the channel.
  TestChannel( ecroc, channel, nFEBs );
  std::cout << "== After TestChannel " << std::endl; 
   
  // Grab a pointer to our configured channel for later use.
  EChannels * echannel = ecroc->GetChannel( channel ); 
  std::cout << "== After GetChannel" << std::endl;  

  // Write some generic values to the FEB that are different than what we use 
  // for charge injection and different from the power on defaults. Then read them 
  // back over the course of the next two tests.
  SetupGenericFEBSettings( echannel, nFEBs );
  std::cout << "== After SetupGenericFEBSettings " << std::endl;  

  FEBFPGAWriteReadTest( echannel, nFEBs );
  std::cout << "== After FEBFPGAWriteReadTest " << std::endl;  

  FEBTRiPWriteReadTest( echannel, nFEBs );
  std::cout << "== After FEBTRiPWriteReadTest " << std::endl;  


  // Set up charge injection and read the data. We test for data sizes equal 
  // to what we expect. Get a copy of the buffer and its size for parsing.
  SetupChargeInjection( echannel, nFEBs );
  unsigned int pointer = ReadDPMTestPointer( ecroc, channel, nFEBs ); 
  unsigned char * dataBuffer = ReadDPMTestData( ecroc, channel, nFEBs, pointer ); 

  // Process the data from the sequencer.
  SequencerReadoutBlockTest( dataBuffer, pointer );

  // Read the ADC and parse them.
  ReadADCTest( echannel, nFEBs );

  // Test the VME Crate
  TestVMECrate( controllerID );

  // Read the Discriminators and parse them.
  ReadDiscrTest( echannel, nFEBs );

  // Get & initialize a CRIM.
  CRIM * crim = GetAndTestCRIM( crimCardAddress, controller );

  TestSQLiteTemp();
  TestSQLite( echannel );

  delete crim;
  delete ecroc;
  delete controller;

  ReadoutWorker * rworker = GetAndTestReadoutWorker( controllerID, ecrocCardAddress,
      crimCardAddress, nch0, nch1, nch2, nch3 );
  delete rworker;
  
  std::cout << "== After GetAndTestReadutWorker. Before calling DAQWorker " << std::endl;  


  sig_atomic_t continueRunning = true;
  DAQWorker * dworker = new DAQWorker( args, log4cpp::Priority::DEBUG, &continueRunning );
  std::cout << "== After DAQWorker and before calling TestDAQWorker..." << std::endl;  
  
  TestDAQWorker( dworker );
  std::cout << "== After TestDAQWorker " << std::endl;  

  delete dworker;
  delete args;

  std::cout << "== After TestDAQWorker. Before calling TestReadoutStateRecorder..." << std::endl;  
  TestReadoutStateRecorder();

  log4cpp::Category::shutdown();
  std::cout << "Passed all tests! Executed " << testCount << " tests." << std::endl;

  gettimeofday(&run, NULL);
  unsigned long long stop = (unsigned long long)(run.tv_sec*1000000)
    + (unsigned long long)(run.tv_usec);
  std::cout << "Run Time = " << (stop - start) << " microsec." << std::endl;
  return 0;
}

//---------------------------------------------------
void TestSQLite( EChannels* channel )
{
  std::cout << "Testing TestSQLite...";  
  logger.debugStream() << "Testing:--------------TestSQLite--------------";

  int rc(0);
  DAQWorkerArgs * defArgs = DAQArgs::DefaultArgs();

  struct timeval t;
  unsigned long long start = 0L;
  gettimeofday(&t, NULL);
  start = (unsigned long long)(t.tv_sec);

  std::stringstream ss;
  ss << start;
  std::string dbname = "/work/conditions/test" + ss.str() + ".db";
  defArgs->errDBFileName = dbname;
  DBWorker * dbWorker = new DBWorker( defArgs, log4cpp::Priority::DEBUG );

  struct stat sb;
  assert( 0 == stat( dbname.c_str(), &sb ) );
  logger.debug("DB File exists? File size: %lld bytes", (long long) sb.st_size);
  if (0 == sb.st_size) {
    rc = dbWorker->CreateStandardHWErrorsTable();
    assert( SQLITE_OK == rc );
  }

  int crate = 0;
  VMEModuleTypes::VMECommunicatorType type = VMEModuleTypes::EChannels;
  unsigned int address = 0xFFFFFFFF;
  std::string message = "test message";
  FHWException * ex = new FHWException(crate,type,address,message);


  rc = dbWorker->AddErrorToDB( *ex, start, start/10000L, (start%10000L) );
  assert( SQLITE_OK == rc );

  // sleep to keep timestamps unique in the db - lame, but simple
  sleep(1);
  try {
    channel->throwIfError( 1, "test error" );
  }
  catch (FHWException &ex) {
    gettimeofday(&t, NULL);
    start = (unsigned long long)(t.tv_sec);
    rc = dbWorker->AddErrorToDB( ex, start, start/10000L, (start%10000L) );
    assert( SQLITE_OK == rc );
  }

  delete defArgs;
  delete ex;
  delete dbWorker;

  logger.debugStream() << "Passed:--------------TestSQLite--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void TestSQLiteTemp()
{
  std::cout << "Testing TestSQLiteTemp...";  
  logger.debugStream() << "Testing:--------------TestSQLiteTemp--------------";

  const char *tmpfile = ""; // default to temp db
  sqlite3 *db = NULL;
  char *vfsName = NULL;  
  int rc = 0;
  int flags = SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE; 

  sqlite3_initialize();
  rc = sqlite3_open_v2( tmpfile, &db, flags, vfsName ); 

  if (SQLITE_OK != rc) {
    sqlite3_close( db );
    assert( SQLITE_OK == rc );
  }

  /* perform db operations */ 

  sqlite3_close( db ); 
  sqlite3_shutdown();

  logger.debugStream() << "Passed:--------------TestSQLiteTemp--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void TestReadoutStateRecorder()
{
  std::cout << "Testing ReadoutStateRecorder...";  
  logger.debugStream() << "Testing:--------------ReadoutStateRecorder--------------";

  struct DAQWorkerArgs * args = DAQArgs::DefaultArgs();

  ReadoutStateRecorder *stateRecorder = new ReadoutStateRecorder( args, log4cpp::Priority::DEBUG );

  stateRecorder->BeginNextGate();
  stateRecorder->FinishGate();

  Triggers::TriggerType trigType = stateRecorder->GetNextTriggerType();
  logger.debugStream() << "Trigger Type = " << trigType;
  assert( 1 == trigType ); // Default mode is OneShot, so Trigger Type is Pedestal
  std::tr1::shared_ptr<DAQHeader> daqHdr = stateRecorder->GetDAQHeader( HeaderData::SentinelBank );
  assert( 56 == daqHdr->GetDataLength() );
  logger.debugStream() << "Sentinel Bank Length = " << daqHdr->GetDataLength();

  delete stateRecorder;
  delete args;

  logger.debugStream() << "Passed:--------------ReadoutStateRecorder--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void TestVMECrate( int crateNumber )
{
  std::cout << "Testing VMECrate...";  
  logger.debugStream() << "Testing:--------------VMECrate--------------";

  // Test "by-hand" gate generation with the RDFE sequencer.
  /* for (std::vector<VMECrate*>::iterator p=crates.begin(); p!=crates.end(); ++p) { */
  /*   (*p)->EnableSequencerReadout(); */
  /*   (*p)->SendSoftwareRDFE(); */
  /*   (*p)->WaitForSequencerReadoutCompletion(); */
  /*   (*p)->DisableSequencerReadout(); */
  /* } */


  logger.debugStream() << "Passed:--------------VMECrate--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void TestDAQWorker( DAQWorker * worker )
{
  std::cout << "Testing DAQWorker...";  
  logger.debugStream() << "Testing:--------------DAQWorker--------------";

  std::cout << "Initialize Hardware ";
  worker->InitializeHardware(); 
  std::cout << "  Initialized Hardware. Calling TakeData "; 
  worker->TakeData();
  std::cout << " After TakeData ";

  logger.debugStream() << "Passed:--------------DAQWorker--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void SequencerReadoutBlockTest( unsigned char * data, unsigned short dataLength )
{
  std::cout << "Testing SequencerReadoutBlockTest...";  
  logger.debugStream() << "Testing:--------------SequencerReadoutBlockTest--------------";
  SequencerReadoutBlock * block = new SequencerReadoutBlock();
  block->SetData( data, dataLength );
  logger.debugStream() << "SequencerReadoutBlockTest : Parsing Data into Frames";
  block->ProcessDataIntoFrames();
  logger.debugStream() << "SequencerReadoutBlockTest : Inspecting Frames";
  while (block->FrameCount()) {
    LVDSFrame * frame = block->PopOffFrame();
    logger.debugStream() << (*frame);  
    frame->printReceivedMessageToLog();
    delete frame;
  }
  delete block;

  logger.debugStream() << "Passed:--------------SequencerReadoutBlockTest--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
ReadoutWorker * GetAndTestReadoutWorker( int controllerID, unsigned int ecrocCardAddress, 
    unsigned int crimCardAddress, int nch0, int nch1, int nch2, int nch3)
{
  std::cout << "Testing Get and Test ReadoutWorker...";  
  ReadoutWorker *worker = NULL;
  sig_atomic_t status = true;
  worker = new ReadoutWorker( log4cpp::Priority::DEBUG, &status, true );
  assert( NULL != worker );
  logger.infoStream() << "Got the ReadoutWorker.";

  worker->AddCrate(0);
  worker->GetVMECrateVector(0)->AddECROC( ecrocCardAddress, nch0, nch1, nch2, nch3 );
  worker->GetVMECrateVector(0)->AddCRIM( crimCardAddress );
  worker->InitializeCrates( runningMode );

  std::cout << "Passed!" << std::endl;
  testCount++;
  return worker;
} 


//---------------------------------------------------
CRIM * GetAndTestCRIM( unsigned int address, Controller * controller )
{
  std::cout << "Testing Get and Test CRIM...";  
  if (address < (1<<VMEModuleTypes::CRIMAddressShift)) {
    address = address << VMEModuleTypes::CRIMAddressShift;
  }
  CRIM * crim = new CRIM( address, controller );

  assert( crim->GetAddress() == address );
  crim->Initialize( runningMode );
  unsigned short status = crim->GetStatus();
  assert( 0xf200 == status );
  unsigned short interruptStatus = crim->GetInterruptStatus();
  crim->ClearPendingInterrupts( interruptStatus );
  interruptStatus = crim->GetInterruptStatus();
  assert( 0 == interruptStatus );

  logger.infoStream() << "CRIM " << (*crim) << " passed all tests!";
  std::cout << "Passed!" << std::endl;
  testCount++;
  return crim;
}

//---------------------------------------------------
void ReadDiscrTest( EChannels* channel, unsigned int nFEBs )
{
  std::cout << "Testing Read Discrs...";  
  logger.debugStream() << "Testing:--------------ReadDiscrTest--------------";

  for (unsigned int nboard = 1; nboard <= nFEBs; nboard++) {

    channel->ClearAndResetStatusRegister();

    // Recall the FEB vect attached to the channel is indexed from 0.
    int vectorIndex = nboard - 1;
    FrontEndBoard *feb = channel->GetFrontEndBoardVector( vectorIndex );
    std::tr1::shared_ptr<DiscrFrame> frame = feb->GetDiscrFrame();

    channel->WriteFrameRegistersToMemory( frame );
    channel->SendMessage();
    unsigned short status = channel->WaitForMessageReceived();
    assert( 0x1010 == status );
    unsigned int pointer = channel->ReadDPMPointer();
    assert( 25 + 2/*hits/trip*/ * 4/*trips*/ * 40 /*bytes/hit*/ == pointer ); // 338 assumes 2 hits per trip
    unsigned char* data = channel->ReadMemory( pointer );

    frame->SetReceivedMessage(data);
    frame->printReceivedMessageToLog();
    assert( !frame->CheckForErrors() );
    frame->DecodeRegisterValues(); 
    for (unsigned int i = 0; i < 4; ++i) 
      assert( 2 == frame->GetNHitsOnTRiP(i) );
  }

  logger.debugStream() << "Passed:--------------ReadDiscrTest--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}


//---------------------------------------------------
void ReadADCTest( EChannels* channel, unsigned int nFEBs )
{
  std::cout << "Testing Read ADCs...";  
  logger.debugStream() << "Testing:--------------ReadADCTest--------------";

  int iHit = 1; // 0 - 1 should be charge injected

  for (unsigned int nboard = 1; nboard <= nFEBs; nboard++) {

    channel->ClearAndResetStatusRegister();

    // Recall the FEB vect attached to the channel is indexed from 0.
    int vectorIndex = nboard - 1;
    FrontEndBoard *feb = channel->GetFrontEndBoardVector( vectorIndex );
    std::tr1::shared_ptr<ADCFrame> frame = feb->GetADCFrame(iHit);

    channel->WriteFrameRegistersToMemory( frame );
    channel->SendMessage();
    unsigned short status = channel->WaitForMessageReceived();
    assert( 0x1010 == status );
    unsigned int pointer = channel->ReadDPMPointer();
    //std::cout << "adc pointer " << pointer << std::endl;
    assert( MinervaDAQSizes::ADCFrameMaxSize == pointer ); 
    unsigned char* data = channel->ReadMemory( pointer );

    frame->SetReceivedMessage(data);
    assert( !frame->CheckForErrors() );
    frame->printReceivedMessageToLog();
    frame->DecodeRegisterValues(); 
  }

  logger.debugStream() << "Passed:--------------ReadADCTest--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}


//---------------------------------------------------
unsigned char * ReadDPMTestData( ECROC * ecroc, unsigned int channel, 
    unsigned int nFEBs, unsigned int pointer ) 
{
  std::cout << "Testing ReadDPM Data...";  

  EChannels * echannel = ecroc->GetChannel( channel );
  assert( nFEBs == echannel->GetFrontEndBoardVector()->size() );

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
  assert( nFEBs == echannel->GetFrontEndBoardVector()->size() );

  unsigned int pointer = echannel->ReadDPMPointer();
  logger.infoStream() << " After reset, pointer = " << pointer;
  assert( (0 == pointer) || (1 == pointer) );  // ??? 1 ???
  ecroc->FastCommandOpenGate();
  usleep(300);
  ecroc->EnableSequencerReadout();
  ecroc->SendSoftwareRDFE();

  echannel->WaitForSequencerReadoutCompletion();
  pointer = echannel->ReadDPMPointer();
  logger.infoStream() << " After open gate, pointer = " << pointer;
  logger.infoStream() << "  Expect to find = " << chgInjReadoutBytesPerBoard << " * " <<
    nFEBs << " = " << chgInjReadoutBytesPerBoard * nFEBs;
  assert( chgInjReadoutBytesPerBoard * nFEBs == pointer );
  
  std::cout << "Passed!" << std::endl;
  testCount++;
  return pointer;


}

//---------------------------------------------------
void SetupGenericFEBSettings( EChannels* channel, unsigned int nFEBs )
{
  logger.debugStream() << "SetupGenericFEBSettings";
  // This is not exactly a test, per se. If the setup is 
  // done incorrectly, it will show in *later* tests.
  for (unsigned int nboard = 1; nboard <= nFEBs; nboard++) {
    FPGASetupForGeneric( channel, nboard );
    TRIPSetupForGeneric( channel, nboard );
  }
  logger.debugStream() << "Finished SetupGenericFEBSettings";
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
  logger.debugStream() << "Testing:--------------FEBFPGAWriteReadTest--------------";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress();

  for (unsigned int nboard = 1; nboard <= nFEBs; nboard++) {

    // Recall the FEB vect attached to the channel is indexed from 0.
    int vectorIndex = nboard - 1;
    FrontEndBoard *feb = channel->GetFrontEndBoardVector( vectorIndex );

    // Re-set to defaults (to make sure we read new values in).
    std::tr1::shared_ptr<FPGAFrame> frame = feb->GetFPGAFrame();
    frame->SetFPGAFrameDefaultValues();

    // ReadFPGAProgrammingRegisters sets up the message and reads the data into the channel memory...
    unsigned int dataLength = channel->ReadFPGAProgrammingRegistersToMemory( frame );
    assert( MinervaDAQSizes::FPGAFrameMaxSize == dataLength );
    // ...then ReadMemory retrieves the data.
    unsigned char * dataBuffer = channel->ReadMemory( dataLength );
    frame->SetReceivedMessage(dataBuffer);
    frame->DecodeRegisterValues();
    frame->printReceivedMessageToLog();
    logger.debugStream() << "We read fpga's for feb " << (int)frame->GetBoardID();
    frame->ShowValues();

    assert( FrameTypes::FPGA == frame->GetDeviceType() ); 
    assert( nboard == (unsigned int)frame->GetFEBNumber() );
    assert( genericTimer == frame->GetTimer() );
    assert( genericGateStart == frame->GetGateStart() );
    assert( genericHVTarget == frame->GetHVTarget() );
    assert( genericGateLength == frame->GetGateLength() );
    assert( genericHVPeriodManual == frame->GetHVPeriodManual() );
    assert( genericDiscEnableMask == frame->GetDiscEnMask0() );
    assert( genericDiscEnableMask == frame->GetDiscEnMask1() );
    assert( genericDiscEnableMask == frame->GetDiscEnMask2() );
    assert( genericDiscEnableMask == frame->GetDiscEnMask3() );
  }
  logger.debugStream() << "Passed:--------------FEBFPGAWriteReadTest--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void FEBTRiPWriteReadTest( EChannels* channel, unsigned int nFEBs )
{
  std::cout << "Testing TRiP Read back...";  
  logger.debugStream() << "Testing:--------------FEBTRiPWriteReadTest--------------";

  for (unsigned int boardID = 1; boardID <= nFEBs; boardID++ ) {
    int vectorIndex = boardID - 1;
    FrontEndBoard *feb = channel->GetFrontEndBoardVector( vectorIndex );

    for ( int i=0; i<6 /* 6 trips per FEB */; i++ ) {
      // Clear Status & Reset
      channel->ClearAndResetStatusRegister();

      { // the frame will be local to this block and clean up when we exit the block
        std::tr1::shared_ptr<TRIPFrame> frame = feb->GetTRIPFrame(i);
        // Set up the message... (just to look at)
        frame->SetRead(true);
        frame->MakeMessage();
        unsigned int tmpML = frame->GetOutgoingMessageLength();
        assert( MinervaDAQSizes::TRiPProgrammingFrameReadSize == tmpML );
        std::stringstream ss;
        ss << "Trip " << i << std::endl;
        unsigned char *message = frame->GetOutgoingMessage();
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
        logger.debugStream() << ss.str();
      }

      std::tr1::shared_ptr<TRIPFrame> frame = feb->GetTRIPFrame(i);
      channel->WriteTRIPRegistersReadFrameToMemory( frame );
      channel->SendMessage();
      unsigned short status = channel->WaitForMessageReceived();
      unsigned int dataLength = channel->ReadDPMPointer();
      logger.debugStream() << "FEB " << boardID << "; Status = 0x" << std::hex << status 
        << "; FEBTRiPWriteReadTest dataLength = " << std::dec << dataLength;
      assert( MinervaDAQSizes::TRiPProgrammingFrameReadResponseSize == dataLength ); 
      unsigned char * dataBuffer = channel->ReadMemory( dataLength );
      frame->SetReceivedMessage(dataBuffer);
      frame->printReceivedMessageToLog();
      frame->DecodeRegisterValues();
      logger.debugStream() << "We read trip's for feb " << (int)frame->GetFEBNumber() << " trip " << frame->GetTripNumber();
      // frame->ShowValues(); // TODO add this as a virtual function to LVDSFrame  

      std::stringstream ss;
      for (unsigned int k=0;k<14;k++) {
        ss << "Trip Register " << k << "; Value = " << 
          (int)frame->GetTripValue(k) << std::endl;
      }
      logger.debugStream() << ss.str();
      assert( 0 == frame->GetTripValue(9) );  // we set this
    }
  }
  logger.debugStream() << "Passed:--------------FEBTRiPWriteReadTest--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
void FPGAWriteConfiguredFrame( EChannels* channel, std::tr1::shared_ptr<FPGAFrame> frame )
{
  logger.debugStream() << "FPGAWriteConfiguredFrame";
  channel->ClearAndResetStatusRegister();
  channel->WriteFrameRegistersToMemory( frame );
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
  FrontEndBoard *feb = channel->GetFrontEndBoardVector( vectorIndex );

  for ( int i=0; i<6 /* 6 trips per FEB */; i++ ) {

    std::tr1::shared_ptr<TRIPFrame> frame = feb->GetTRIPFrame(i);
    channel->ClearAndResetStatusRegister();

    // Set up the message...
    frame->SetRead(false);
    {
      frame->SetRegisterValue( 0, TripTTypes::DefaultTripRegisterValues.tripRegIBP );
      frame->SetRegisterValue( 1, TripTTypes::DefaultTripRegisterValues.tripRegIBBNFOLL );
      frame->SetRegisterValue( 2, TripTTypes::DefaultTripRegisterValues.tripRegIFF );
      frame->SetRegisterValue( 3, TripTTypes::DefaultTripRegisterValues.tripRegIBPIFF1REF );
      frame->SetRegisterValue( 4, TripTTypes::DefaultTripRegisterValues.tripRegIBOPAMP );
      frame->SetRegisterValue( 5, TripTTypes::DefaultTripRegisterValues.tripRegIB_T );
      frame->SetRegisterValue( 6, TripTTypes::DefaultTripRegisterValues.tripRegIFFP2 );
      frame->SetRegisterValue( 7, TripTTypes::DefaultTripRegisterValues.tripRegIBCOMP );
      frame->SetRegisterValue( 8, TripTTypes::DefaultTripRegisterValues.tripRegVREF );
      frame->SetRegisterValue( 9, TripTTypes::DefaultTripRegisterValues.tripRegVTH );
      frame->SetRegisterValue(10, TripTTypes::DefaultTripRegisterValues.tripRegPIPEDEL);
      frame->SetRegisterValue(11, TripTTypes::DefaultTripRegisterValues.tripRegGAIN );
      frame->SetRegisterValue(12, TripTTypes::DefaultTripRegisterValues.tripRegIRSEL );
      frame->SetRegisterValue(13, TripTTypes::DefaultTripRegisterValues.tripRegIWSEL );
      frame->SetRegisterValue(14, 0x1FE ); //inject, enable first words, 0x1FFFE for two...
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

    channel->WriteFrameRegistersToMemory( frame );
    channel->SendMessage();
    unsigned short status = channel->WaitForMessageReceived();
    unsigned int dataLength = channel->ReadDPMPointer();
    logger.debugStream() << "FEB " << boardID << "; Status = 0x" << std::hex << status 
      << "; TRIPSetupForChargeInjection dataLength = " << std::dec << dataLength;
    assert( MinervaDAQSizes::TRiPProgrammingFrameWriteResponseSize == dataLength ); 
  }
}

//---------------------------------------------------
void FPGASetupForChargeInjection( EChannels* channel, int boardID )
{
  logger.debugStream() << "FPGASetup for Charge Injection";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress()
    << std::dec << "; FEB Addr = " << boardID;

  int vectorIndex = boardID - 1;
  FrontEndBoard *feb = channel->GetFrontEndBoardVector( vectorIndex );
  std::tr1::shared_ptr<FPGAFrame> frame = feb->GetFPGAFrame();
  {
    unsigned char val[]={0x0};
    frame->SetTripPowerOff(val);
    frame->SetGateStart(41938);
    frame->SetGateLength( 1337 );
    frame->SetHVPeriodManual(41337);
    frame->SetHVTarget(25000);
    unsigned char previewEnable[] = {0x0};
    frame->SetPreviewEnable(previewEnable);
    for (int i=0; i<4; i++) {
      // try to get hits in different windows (need ~35+ ticks) 
      int tickOffset = 40;//40;
      //std::cout << "boardID = " << boardID << std::endl;
      unsigned char inj[] = { 1 + (unsigned char)i*(tickOffset) + 2*((int)boardID) };
      unsigned char enable[] = {0x1};
      frame->SetInjectCount(inj,i);
      frame->SetInjectEnable(enable,i);
      frame->SetDiscrimEnableMask(0xFFFF,i);
    }
    unsigned short int dacval = 3000;//4000;
    frame->SetInjectDACValue(dacval);
    unsigned char injPhase[] = {0x1};
    frame->SetInjectPhase(injPhase);
    FrameTypes::Devices dev     = FrameTypes::FPGA;
    FrameTypes::Broadcasts b    = FrameTypes::None;
    FrameTypes::Directions d    = FrameTypes::MasterToSlave;
    FrameTypes::FPGAFunctions f = FrameTypes::Write;
    frame->MakeDeviceFrameTransmit(dev,b,d,f, (unsigned int)frame->GetFEBNumber());
  }
  FPGAWriteConfiguredFrame( channel, frame );

  // Set up DAC
  unsigned char injStart[] = {0x1};
  frame->SetInjectDACStart(injStart);
  FPGAWriteConfiguredFrame( channel, frame );

  // Reset DAC Start
  unsigned char injReset[] = {0x0};
  frame->SetInjectDACStart(injReset);
  FPGAWriteConfiguredFrame( channel, frame );
}

//---------------------------------------------------
void TRIPSetupForGeneric( EChannels* channel, int boardID )
{
  // No real point in reading and decoding the response frame - the TRiP's send 
  // a response frame composed entirely of zeroes when being *written* to.        
  logger.debugStream() << "Testing:--------------TRIPSetupForGeneric--------------";
  logger.debugStream() << "TRIPSetup for Generic Settings";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress()
    << std::dec << "; FEB Addr = " << boardID;

  int vectorIndex = boardID - 1;
  FrontEndBoard *feb = channel->GetFrontEndBoardVector( vectorIndex );

  for ( int i=0; i<6 /* 6 trips per FEB */; i++ ) {

    std::tr1::shared_ptr<TRIPFrame> frame = feb->GetTRIPFrame(i);
    channel->ClearAndResetStatusRegister();

    // Set up the message...
    frame->SetRead(false);
    {
      frame->SetRegisterValue( 0, TripTTypes::DefaultTripRegisterValues.tripRegIBP );
      frame->SetRegisterValue( 1, TripTTypes::DefaultTripRegisterValues.tripRegIBBNFOLL );
      frame->SetRegisterValue( 2, TripTTypes::DefaultTripRegisterValues.tripRegIFF );
      frame->SetRegisterValue( 3, TripTTypes::DefaultTripRegisterValues.tripRegIBPIFF1REF );
      frame->SetRegisterValue( 4, TripTTypes::DefaultTripRegisterValues.tripRegIBOPAMP );
      frame->SetRegisterValue( 5, TripTTypes::DefaultTripRegisterValues.tripRegIB_T );
      frame->SetRegisterValue( 6, TripTTypes::DefaultTripRegisterValues.tripRegIFFP2 );
      frame->SetRegisterValue( 7, TripTTypes::DefaultTripRegisterValues.tripRegIBCOMP );
      frame->SetRegisterValue( 8, TripTTypes::DefaultTripRegisterValues.tripRegVREF );
      frame->SetRegisterValue( 9, 0 ); // we'll turn the TRiPs on before we do chg inj
      frame->SetRegisterValue(10, TripTTypes::DefaultTripRegisterValues.tripRegPIPEDEL);
      frame->SetRegisterValue(11, TripTTypes::DefaultTripRegisterValues.tripRegGAIN );
      frame->SetRegisterValue(12, TripTTypes::DefaultTripRegisterValues.tripRegIRSEL );
      frame->SetRegisterValue(13, TripTTypes::DefaultTripRegisterValues.tripRegIWSEL );
      frame->SetRegisterValue(14, 0x0 ); 
    }

    channel->WriteFrameRegistersToMemory( frame );
    channel->SendMessage();
    unsigned short status = channel->WaitForMessageReceived();
    unsigned int dataLength = channel->ReadDPMPointer();
    logger.debugStream() << "FEB " << boardID << "; Status = 0x" << std::hex << status 
      << "; TRIPSetupForGeneric dataLength = " << std::dec << dataLength;
    assert( MinervaDAQSizes::TRiPProgrammingFrameWriteResponseSize == dataLength ); 
  }
  logger.debugStream() << "Passed:--------------TRIPSetupForGeneric--------------";
}

//---------------------------------------------------
void FPGASetupForGeneric( EChannels* channel, int boardID )
{
  logger.debugStream() << "FPGASetup for Generic Settings";
  logger.debugStream() << " EChannels Direct Address = " << std::hex << channel->GetDirectAddress()
    << std::dec << "; FEB Addr = " << boardID;

  int vectorIndex = boardID - 1;
  FrontEndBoard *feb = channel->GetFrontEndBoardVector( vectorIndex );
  std::tr1::shared_ptr<FPGAFrame> frame = feb->GetFPGAFrame();
  {
    unsigned char val[]={0x0};
    frame->SetTripPowerOff(val);
    frame->SetTimer( genericTimer );
    frame->SetGateStart( genericGateStart );
    frame->SetGateLength( genericGateLength );
    frame->SetHVPeriodManual( genericHVPeriodManual );
    frame->SetHVTarget( genericHVTarget );
    unsigned char previewEnable[] = {0x0};
    frame->SetPreviewEnable(previewEnable);
    for (int i=0; i<4; i++) {
      unsigned char inj[] = { 1 + (unsigned char)i*(2) + 2*((int)boardID) };
      unsigned char enable[] = {0x0};
      frame->SetInjectCount(inj,i);
      frame->SetInjectEnable(enable,i);
      frame->SetDiscrimEnableMask(0xFFFF,i);
    }
    unsigned short int dacval = 0;
    frame->SetInjectDACValue(dacval);
    unsigned char injPhase[] = {0x0};
    frame->SetInjectPhase(injPhase);
    FrameTypes::Devices dev     = FrameTypes::FPGA;
    FrameTypes::Broadcasts b    = FrameTypes::None;
    FrameTypes::Directions d    = FrameTypes::MasterToSlave;
    FrameTypes::FPGAFunctions f = FrameTypes::Write;
    frame->MakeDeviceFrameTransmit(dev,b,d,f, (unsigned int)frame->GetFEBNumber());
    assert( FrameTypes::FPGA == frame->GetDeviceType() ); 
    assert( boardID == frame->GetFEBNumber() );
    assert( genericTimer == frame->GetTimer() );
    assert( genericGateStart == frame->GetGateStart() );
    assert( genericHVTarget == frame->GetHVTarget() );
    assert( genericGateLength == frame->GetGateLength() );
    assert( genericHVPeriodManual == frame->GetHVPeriodManual() );
    assert( genericDiscEnableMask == frame->GetDiscEnMask0() );
    assert( genericDiscEnableMask == frame->GetDiscEnMask1() );
    assert( genericDiscEnableMask == frame->GetDiscEnMask2() );
    assert( genericDiscEnableMask == frame->GetDiscEnMask3() );
  }
  FPGAWriteConfiguredFrame( channel, frame );
}

//---------------------------------------------------
void TestChannel( ECROC* ecroc, unsigned int channelNumber, unsigned int nFEBs )
{
  std::cout << "Testing ECROC Channel...";  
  logger.debugStream() << "Testing:--------------TestChannel--------------";

  EChannels * channel = ecroc->GetChannel( channelNumber );
  assert( channel != NULL );
  assert( channel->GetChannelNumber() == channelNumber );
  assert( channel->GetParentECROCAddress() == ecroc->GetAddress() );
  assert( channel->GetParentCROCNumber() == 
      (ecroc->GetAddress() >> VMEModuleTypes::ECROCAddressShift) );
  assert( channel->GetDirectAddress() == 
      ecroc->GetAddress() + VMEModuleTypes::EChannelOffset * (unsigned int)(channelNumber) );
  channel->SetupNFrontEndBoards( nFEBs );
  assert( channel->GetFrontEndBoardVector()->size() == nFEBs ); 
  channel->ClearAndResetStatusRegister();
  unsigned short status = channel->ReadFrameStatusRegister();
  assert( /* (status == 0x1010) || */ (status == 0x4040) );
  //assert( channel->ReadTxRxStatusRegister() == 0x2410 );

  std::tr1::shared_ptr<EChannelsConfigRegParser> config = channel->GetChannelConfiguration();
  logger.infoStream() << "Channel Configuration = " << config->Description();

  bool clockMonIsFalling = config->ClockMonPhaseBitIsFalling();

  config->SetClockMonPhaseSelFalling();
  channel->SetChannelConfiguration( config );
  std::tr1::shared_ptr<EChannelsConfigRegParser> fconfig = channel->GetChannelConfiguration();
  logger.infoStream() << "Channel Configuration After Set Falling = " << fconfig->Description();
  assert( fconfig->ClockMonPhaseBitIsFalling() == true );
  assert( fconfig->ClockMonPhaseBitIsLeading() == false );

  config->SetClockMonPhaseSelLeading();
  channel->SetChannelConfiguration( config );
  std::tr1::shared_ptr<EChannelsConfigRegParser> lconfig = channel->GetChannelConfiguration();
  logger.infoStream() << "Channel Configuration After Set Leading = " << lconfig->Description();
  assert( lconfig->ClockMonPhaseBitIsFalling() == false );
  assert( lconfig->ClockMonPhaseBitIsLeading() == true );

  if (clockMonIsFalling) {
    config->SetClockMonPhaseSelFalling();
  } else {
    config->SetClockMonPhaseSelLeading();
  }
  channel->SetChannelConfiguration( config );
  logger.infoStream() << "Channel Configuration = " << config->Description();


  logger.infoStream() << "EChannel " << (*channel) << " passed all tests!";
  logger.debugStream() << "Passed:--------------TestChannel--------------";
  std::cout << "Passed!" << std::endl;
  testCount++;
}

//---------------------------------------------------
ECROC * GetAndTestECROC( unsigned int address, Controller * controller )
{
  std::cout << "Testing Get and Test ECROC...";  
  logger.debugStream() << "Testing:--------------GetAndTestECROC--------------";
  if (address < (1<<VMEModuleTypes::ECROCAddressShift)) {
    address = address << VMEModuleTypes::ECROCAddressShift;
  }
  ECROC * ecroc = new ECROC( address, controller );

  assert( ecroc->GetAddress() == address );
  // These methods are void. Not clear it makes sense to call all 
  // public CROCE methods since they're talking to the hardware.
  ecroc->Initialize( runningMode );
  ecroc->ClearAndResetStatusRegisters();
  ecroc->EnableSequencerReadout();
  ecroc->DisableSequencerReadout();

  unsigned short seqdelay = 0;
  ecroc->SetSequencerDelayValue( 0x1FF );
  ecroc->SequencerDelayEnable();
  seqdelay = ecroc->ReadSequencerPulseDelayRegister();
  assert( seqdelay == 0x81FF );
  ecroc->SetSequencerDelayValue( 0x1A3 );
  ecroc->SequencerDelayDisable();
  seqdelay = ecroc->ReadSequencerPulseDelayRegister();
  assert( seqdelay == 0x01A3 );
  ecroc->SetSequencerDelayValue( 0x0 );
  seqdelay = ecroc->ReadSequencerPulseDelayRegister();
  assert( seqdelay == 0x0 );

  logger.infoStream() << "ECROC " << (*ecroc) << " passed all tests!";
  logger.debugStream() << "Passed:--------------GetAndTestECROC--------------";
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
