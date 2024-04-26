#ifndef DAQArgs_h
#define DAQArgs_h
/*! 
  \file DAQArgs.h
*/

#include <assert.h>
#include <iostream>
#include "DAQWorkerArgs.h"
#include "exit_codes.h"
#include <stdlib.h>

/*! 
  \class DAQArgs
  \brief Return default and parsed DAQWorkerArgs.
  \author Gabriel Perdue
  */
class DAQArgs {

  static const std::string fileRoot;
  static const std::string conditionsRoot;

  public:
    static struct DAQWorkerArgs * DefaultArgs()
    {
      struct DAQWorkerArgs * args = new DAQWorkerArgs;
      assert( args != NULL );

      args->runNumber = 42;
      args->subRunNumber = 42;
      args->numberOfGates = 100;
      args->runMode = Modes::OneShot;  
      args->detector = Detectors::UnknownDetector;
      args->detectorConfigCode = 0;  // number of FEBs
      args->ledLevel = 0;
      args->ledGroup = 0;
      args->hardwareInitLevel = 1; // default to VME init, do not touch FEBs 
      args->networkPort = 65535;
      args->etFileName = fileRoot + "etsys/MinervaDAQ_RawData";
      args->logFileName = fileRoot + "logs/MinervaDAQ_Log.txt";
      args->samPyFileName = fileRoot + "sam/MinervaDAQ_SAM.metadata.py";
      args->samJSONFileName = fileRoot + "sam/MinervaDAQ_SAM.metadata.json";
      args->metadataFileName = fileRoot + "rawdata/MinervaDAQ.metadata.json"; //Needs to be in same directory as rawdata per DUNE requirements
      args->dataFileName = fileRoot + "rawdata/MinervaDAQ_RawData.dat";
      args->dataFileBaseName = "MinervaDAQ_RawData.dat";
      args->hardwareConfigFileName = "unknown"; 
      args->hostName = "localhost";
      args->lastTriggerFileName = conditionsRoot + "last_trigger.dat"; 
      args->globalGateLogFileName = conditionsRoot + "global_gate.dat";
      args->errDBFileName = conditionsRoot + "daqSQLiteDB.db";    

      return args;
    };

    static struct DAQWorkerArgs * ParseArgs( const int& argc, char * argv[], const std::string& controllerID )
    {
      struct DAQWorkerArgs * args = DAQArgs::DefaultArgs();

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
          args->runMode = (Modes::RunningModes)atoi(argv[optind]);
        }
        else if (sw=="-d") {
          optind++;
          args->detector = (Detectors::DetectorTypes)atoi(argv[optind]);
        }
        else if (sw=="-et") {
          optind++;
          std::string fileBaseName = argv[optind];
          args->etFileName   = fileRoot + "etsys/" + fileBaseName + "_RawData";
          args->logFileName  = fileRoot + "logs/" + fileBaseName + "_Controller" + 
            controllerID + "Log.txt";
          args->samPyFileName  = fileRoot + "sam/" + fileBaseName + "_SAM.metadata.py";
          args->samJSONFileName  = fileRoot + "sam/" + fileBaseName + "_SAM.metadata.json";
          args->dataFileBaseName = fileBaseName + "_RawData.dat";
          args->dataFileName = fileRoot + "rawdata/" + args->dataFileBaseName;
          args->metadataFileName = fileRoot + "rawdata/" + fileBaseName + ".metadata.json"; //Needs to be in same directory as rawdata per DUNE requirements
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
        else if (sw=="-h") {
          optind++;
          args->hostName = argv[optind];
        }
        else if (sw=="-lt") {
          optind++;
          args->lastTriggerFileName = conditionsRoot + argv[optind];
        }
        else if (sw=="-gg") {
          optind++;
          args->globalGateLogFileName = conditionsRoot + argv[optind];
        }
        else if (sw=="-db") {
          optind++;
          args->errDBFileName = conditionsRoot + argv[optind];
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
    
};


#endif
