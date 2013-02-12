#ifndef daqmain_cxx
#define daqmain_cxx

#include <fstream>
#include <iostream>
#include <sstream>
#include <assert.h>

#include "DAQWorker.h"
#include "ReadoutTypes.h"
#include "exit_codes.h"
#include "daqmain.h"

// log4cpp message levels:
//	emergStream(), fatalStream(), alert..., crit..., error..., warn..., notice..., info..., debug...
log4cpp::Appender* baseAppender;
log4cpp::Category& rootCat = log4cpp::Category::getRoot();
log4cpp::Category& daqmain = log4cpp::Category::getInstance(std::string("daqmain"));

int main( int argc, char * argv[] ) 
{
  struct DAQWorkerArgs * args = parseArgs( argc, argv, "0" );

  /* char lasttrigger_filename[100]; sprintf(lasttrigger_filename,"/work/conditions/last_trigger.dat"); */ 

  baseAppender = new log4cpp::FileAppender("default", args->logFileName);
  baseAppender->setLayout(new log4cpp::BasicLayout());
  rootCat.addAppender(baseAppender);
  rootCat.setPriority(log4cpp::Priority::DEBUG);
  daqmain.setPriority(log4cpp::Priority::DEBUG);

  DAQWorker * worker = new DAQWorker( args, baseAppender, log4cpp::Priority::DEBUG );

  // worker->setUpET();  // ?
  // worker->TakeData();

  log4cpp::Category::shutdown();
  delete worker;
  delete args;

  return 0;
}

struct DAQWorkerArgs * parseArgs( const int& argc, char * argv[], const std::string& controllerID )
{
  struct DAQWorkerArgs * args = new DAQWorkerArgs;
  assert( args != NULL );

  std::string fileRoot = "/work/data/";
  args->runNumber = 1;
  args->subRunNumber = 0;
  args->numberOfGates = 100;
  args->runMode = OneShot;  
  args->detector = UnknownDetector;
  args->detectorConfigCode = 0;  // number of FEBs
  args->ledLevel = 0;
  args->ledGroup = 0;
  args->hardwareInitLevel = 1; // default to VME init, do not touch FEBs 
  args->networkPort = 65535;
  args->etFileName = fileRoot + "etsys/testme_RawData";
  args->logFileName = fileRoot + "logs/testme_Log.txt";
  args->samFileName = fileRoot + "sam/testme_SAM.py";
  args->dataFileName = fileRoot + "rawdata/testme_RawData.dat";
  /* const char* name = dataFileName.c_str(); */ 
  args->hardwareConfigFileName = "unknown"; 

  int optind = 1;
  while ((optind < argc) && (argv[optind][0]=='-')) {
    std::string sw = argv[optind];
    if (sw=="-r") {
      optind++;
      args->runNumber = atoi(argv[optind]);
    }
    else if (sw=="-s") {
      optind++;
      args->subRunNumber = atoi(argv[optind]);
    }
    else if (sw=="-g") {
      optind++;
      args->numberOfGates = atoi(argv[optind]);
    }
    else if (sw=="-m") {
      optind++;
      args->runMode = (RunningModes)atoi(argv[optind]);
    }
    else if (sw=="-d") {
      optind++;
      args->detector = (DetectorTypes)atoi(argv[optind]);
    }
    else if (sw=="-et") {
      optind++;
      std::string fileBaseName = argv[optind];
      args->etFileName   = fileRoot + "etsys/" + fileBaseName + "_RawData";
      args->logFileName  = fileRoot + "logs/" + fileBaseName + "_Controller" + 
        controllerID + "Log.txt";
      args->samFileName  = fileRoot + "sam/" + fileBaseName + "_SAM.py";
      args->dataFileName = fileRoot + "rawdata/" + fileBaseName + "_RawData.dat";
    }
    else if (sw=="-cf") {
      optind++;
      args->hardwareConfigFileName = argv[optind]; 
    }
    else if (sw=="-dc") {
      optind++;
      args->detectorConfigCode = atoi(argv[optind]);
    }
    else if (sw=="-ll") {
      optind++;
      args->ledLevel = (unsigned char)atoi(argv[optind]);
    }
    else if (sw=="-lg") {
      optind++;
      args->ledGroup = (unsigned char)atoi(argv[optind]);
    }
    else if (sw=="-hw") {
      optind++;
      args->hardwareInitLevel = atoi(argv[optind]);
    }
    else if (sw=="-p") {
      optind++;
      args->networkPort = atoi(argv[optind]);
    }
    optind++;
  }

  // Exit if there are unknown (misconfigured) arguments.
  if (optind < argc) {
    std::cout << "There were remaining arguments!  Are you SURE you set the run up correctly?" << std::endl;
    std::cout << "  Remaining arguments = ";
    for (;optind<argc;optind++) std::cout << argv[optind];
    std::cout << std::endl;
    free(args);
    exit(EXIT_CONFIG_ERROR);
  }

  return args;
}



#endif
