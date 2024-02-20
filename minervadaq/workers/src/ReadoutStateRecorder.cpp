#ifndef ReadoutStateRecorder_cxx
#define ReadoutStateRecorder_cxx
/*! \file ReadoutStateRecorder.cpp:  
*/
/*
11/21/2014 Geoff Savage
Remove the 1 second sleeps when trigger for OneShot and
PureLightInjection at MTEST.  We had been modifying this file
each time we created a new DAQ version.
*/
#include "ReadoutStateRecorder.h"
#include "exit_codes.h"
#include <unistd.h>

log4cpp::Category& stateRecorderLogger = log4cpp::Category::getInstance(std::string("stateRecorderLogger"));

const int ReadoutStateRecorder::DAQHeaderVersion = 9;

//---------------------------
ReadoutStateRecorder::ReadoutStateRecorder( const DAQWorkerArgs* theArgs, 
    log4cpp::Priority::Value priority ) :
  gate(0),
  triggerType(Triggers::UnknownTrigger),
  firstGate(0),
  globalGate(0),
  gateStartTime(0),
  gateFinishTime(0),
  subRunStartTime(0),
  subRunFinishTime(0),
  MINOSSGATE(0),
  args(theArgs)
{
  stateRecorderLogger.setPriority(priority);
  this->GetGlobalGateFromFile();
  firstGate = globalGate + 1;
  daqUtils = new DAQWorkerUtils( args );
  subRunStartTime = daqUtils->GetTimeInMicrosec();
  stateRecorderLogger.debugStream() << "Created new ReadoutStateRecorder: " << *this;
}

//---------------------------
ReadoutStateRecorder::~ReadoutStateRecorder() 
{
  delete daqUtils;
}

//---------------------------
void ReadoutStateRecorder::SetGateStartTime( unsigned long long theStartTime )
{
  this->gateStartTime = theStartTime;
}

//---------------------------
void ReadoutStateRecorder::SetGateFinishTime( unsigned long long theFinishTime )
{
  this->gateFinishTime = theFinishTime;
}

//---------------------------
void ReadoutStateRecorder::SetMINOSSGATE( unsigned int gateTime )
{
  this->MINOSSGATE = gateTime;
}

//---------------------------
//! Incremement the gate counters and check the gate is in bounds for the run.
bool ReadoutStateRecorder::BeginNextGate()
{
  stateRecorderLogger.debugStream() << "ReadoutStateRecorder::BeginNextGate...";
  gate++;
  this->GetGlobalGateFromFile();
  this->IncrememntGlobalGate();
  stateRecorderLogger.debugStream() << (*this);
  if (!(gate % 10)) 
    stateRecorderLogger.infoStream() << "Taking data for gate " << gate;

  if (gate <= args->numberOfGates) 
    return true;

  return false;
}

bool ReadoutStateRecorder::MoreGates()
{
  int nextGate=0;
  nextGate = gate+1;

  if (nextGate <= args->numberOfGates) 
    return true;

  return false;
}

//---------------------------
//! Log the global gate, write the SAM metadata, and write the last trigger.
/*!
  The last trigger data is used by the Run Control to display information 
  about the last recorded gate to the shifter.
  */
bool ReadoutStateRecorder::FinishGate()
{
  stateRecorderLogger.debugStream() << "ReadoutStateRecorder::FinishGate...";
  subRunFinishTime = daqUtils->GetTimeInMicrosec();
  this->WriteGlobalGateToFile();
  this->WriteToSAMPYFile();
  this->WriteToSAMJSONFile();
  this->WriteLastTriggerDataToFile();
  this->WriteLastTriggerDataToFileMTest();
  return true;
}

//---------------------------
Modes::RunningModes ReadoutStateRecorder::GetRunMode() const
{
  return args->runMode;
}

//---------------------------
//! Calculate the next Triggers::TriggerType based on the gate and mode.
Triggers::TriggerType ReadoutStateRecorder::GetNextTriggerType() 
{
  using namespace Triggers;
  using namespace Modes;
  stateRecorderLogger.debugStream() << "GetNextTriggerType";
  triggerType = UnknownTrigger;
  switch (args->runMode) {
    case OneShot:
      triggerType = Pedestal;
      //     usleep(50000); //0.05 second sleep 
      //sleep(1);
      //usleep(500000); //0.5 second sleep // Chnged Sleep -- Nur 07/28/2017
#ifndef MTEST
      //sleep(1);
      //usleep(500000); //0.5 second sleep // Chnged Sleep -- Nur 07/28/2017      
#endif
      stateRecorderLogger.debugStream() << " Running Mode is OneShot.";
      break;
    case NuMIBeam:
      triggerType = NuMI;
      stateRecorderLogger.debugStream() << " Running Mode is NuMI Beam.";
      break;
    case PureLightInjection:
      triggerType = LightInjection;
#ifndef MTEST
      //sleep(1);
      //usleep(500000); //0.5 second sleep // Chnged Sleep -- Nur 07/28/2017
      usleep(2000000); // 2 second sleep Howard, Jack, Geoff 25Aug22
#endif
      stateRecorderLogger.debugStream() << " Running Mode is PureLightInjection.";
      break;
    case MixedBeamPedestal:
      triggerType = NuMI;
      if (1 == gate % 2 ) triggerType = Pedestal;
      stateRecorderLogger.debugStream() << " Running Mode is MixedBeamPedestal.";
      break;
    case MixedBeamLightInjection:
      triggerType = NuMI;
      if (1 == gate % 2 ) triggerType = LightInjection;
      stateRecorderLogger.debugStream() << " Running Mode is MixedBeamLightInjection.";
      break;
    case Cosmics:
      triggerType = Cosmic;
      stateRecorderLogger.debugStream() << " Running Mode is Cosmic.";
      break;
    case MTBFBeamMuon:
      triggerType = MTBFMuon;
      stateRecorderLogger.debugStream() << " Running Mode is MTBFBeamMuon.";
      break;
    case MTBFBeamOnly:
      triggerType = MTBFBeam;
      stateRecorderLogger.debugStream() << " Running Mode is MTBFBeamOnly.";
      break;
    default:
      stateRecorderLogger.critStream() << "Error in ReadoutWorker::logRunningMode()! Undefined Running Mode!";
  }
  stateRecorderLogger.debugStream() << (*this);
  return triggerType;
}

//---------------------------
unsigned long long ReadoutStateRecorder::GetFirstGate() const
{
  return firstGate;
}

//---------------------------
unsigned long long ReadoutStateRecorder::GetGlobalGate() const
{
  return globalGate;
}

//---------------------------
unsigned long long ReadoutStateRecorder::GetSubRunStartTime() const
{
  return (subRunStartTime/1000000L);
}

//---------------------------
unsigned long long ReadoutStateRecorder::GetSubRunFinishTime() const
{
  return (subRunFinishTime/1000000L);
}

//---------------------------
void ReadoutStateRecorder::GetGlobalGateFromFile()
{
  std::fstream globalGateFile((args->globalGateLogFileName).c_str());
  try {
    if (!globalGateFile) throw (!globalGateFile);
    globalGateFile >> globalGate;
  } 
  catch (bool e) {
    stateRecorderLogger.errorStream() << "Error opening global gate data!";
  }
  globalGateFile.close();
  stateRecorderLogger.debugStream() << "Got global gate " << globalGate;
}

//---------------------------
void ReadoutStateRecorder::IncrememntGlobalGate()
{
  globalGate++;
}

//---------------------------
void ReadoutStateRecorder::WriteGlobalGateToFile()
{
  std::fstream globalGateFile((args->globalGateLogFileName).c_str());
  try {
    if (!globalGateFile) throw (!globalGateFile);
    globalGateFile << globalGate;
  } 
  catch (bool e) {
    stateRecorderLogger.errorStream() << "Error opening global gate data!";
    return; 
  }
  globalGateFile.close();
  stateRecorderLogger.debugStream() << "Put global gate " << globalGate;
}

//-----------------------------
//! Allocate and return a DAQHeader using member variable data.
std::tr1::shared_ptr<DAQHeader> ReadoutStateRecorder::GetDAQHeader( HeaderData::BankType bankType )
{
  stateRecorderLogger.debugStream() << "GetDAQHeader...";
  unsigned int minos = MINOSSGATE; 
  unsigned long long readoutTimeLong = gateFinishTime - gateStartTime;
  unsigned int readoutTime = (unsigned int)readoutTimeLong;
#ifndef GOFAST
#endif
  stateRecorderLogger.debugStream() << " readoutTimeLong = " << readoutTimeLong;
  stateRecorderLogger.debugStream() << " readoutTime     = " << readoutTime;
  stateRecorderLogger.debugStream() << " MINOSSGATE      = " << MINOSSGATE;

  // sadly, these are probably not useful anymore.
  unsigned short int error = 0;
  unsigned short nADCFrames  = 0; 
  unsigned short nDiscFrames = 0;
  unsigned short nFPGAFrames = 0;

  FrameHeader * frameHeader = new FrameHeader(0,0,0,bankType,0,DAQHeaderVersion,0,daqHeaderSize);
  std::tr1::shared_ptr<DAQHeader> daqHeader( 
      new DAQHeader(args->detector, args->detectorConfigCode, args->runNumber, 
        args->subRunNumber, triggerType, args->ledLevel, args->ledGroup,
        globalGate, gate, gateStartTime, error, minos, readoutTime,
        frameHeader,  nADCFrames, nDiscFrames, nFPGAFrames)
      );

  delete frameHeader;
  return daqHeader;
}

//---------------------------------------------------------
void ReadoutStateRecorder::WriteToSAMPYFile()
{
  stateRecorderLogger.debugStream() << "Writing SAM Py File...";

  FILE *file;

  if ( (file=fopen((args->samPyFileName).c_str(), "w")) == NULL ) {
    stateRecorderLogger.errorStream() << "Error opening SAM file for writing!";
    return;
  }

  fprintf(file,"from SamFile.SamDataFile import SamDataFile\n\n");
  fprintf(file,"from SamFile.SamDataFile import ApplicationFamily\n");
  fprintf(file,"from SamFile.SamDataFile import CRC\n");
  fprintf(file,"from SamFile.SamDataFile import SamTime\n");
  fprintf(file,"from SamFile.SamDataFile import RunDescriptorList\n");
  fprintf(file,"from SamFile.SamDataFile import SamSize\n\n");
  fprintf(file,"import SAM\n\n");
  fprintf(file,"metadata = SamDataFile(\n");
  fprintf(file,"fileName = '%s',\n", (args->dataFileBaseName).c_str());
  fprintf(file,"fileType = SAM.DataFileType_ImportedDetector,\n");
  fprintf(file,"fileFormat = 'binary',\n");
  fprintf(file,"crc=CRC(666L,SAM.CRC_Adler32Type),\n");
  fprintf(file,"group='minerva',\n");
#if MTEST
  fprintf(file,"dataTier='binary-raw-test',\n");
#else
  fprintf(file,"dataTier='binary-raw',\n");
#endif
  fprintf(file,"runNumber=%d%04d,\n", args->runNumber, args->subRunNumber);
  fprintf(file,"applicationFamily=ApplicationFamily('online','v09','%s'),\n", GIT_VERSION); //online, DAQ Heder, CVSTag
  fprintf(file,"fileSize=SamSize('0B'),\n");
  fprintf(file,"filePartition=1L,\n");
  switch (args->detector) { // Enumerations set by the DAQHeader class.
    case 0:
      fprintf(file,"runType='unknowndetector',\n");
      break;
    case 1:
      fprintf(file,"runType='pmtteststand',\n");
      break;
    case 2:
      fprintf(file,"runType='trackingprototype',\n");
      break;
    case 4:
      fprintf(file,"runType='testbeam',\n");
      break;
    case 8:
      fprintf(file,"runType='frozendetector',\n");
      break;
    case 16:
      fprintf(file,"runType='upstreamdetector',\n");
      break;
    case 32:
      fprintf(file,"runType='minerva',\n");
      break;
    case 64:
      fprintf(file,"runType='teststand',\n");
      break;
    default:
      fprintf(file,"runType='errordetector',\n");
  }
  fprintf(file,"params = Params({'Online':CaseInsensitiveDictionary");
  fprintf(file,"({'triggerconfig':'%s',", (args->hardwareConfigFileName).c_str() );
  switch ((int)args->runMode) {
    case 0: //OneShot:
      fprintf(file,"'triggertype':'oneshot',})}),\n");
      fprintf(file,"datastream='pdstl',\n");
      break;
    case 1: //NuMIBeam:
      fprintf(file,"'triggertype':'numibeam',})}),\n");
      fprintf(file,"datastream='numib',\n");
      break;
    case 2: //Cosmics:
      fprintf(file,"'triggertype':'cosmics',})}),\n");
      fprintf(file,"datastream='cosmc',\n");
      break;
    case 3: //PureLightInjection:
      fprintf(file,"'triggertype':'purelightinjection',})}),\n");
      fprintf(file,"datastream='linjc',\n");
      break;
    case 4: //MixedBeamPedestal:
      fprintf(file,"'triggertype':'mixedbeampedestal',})}),\n");
      fprintf(file,"datastream='numip',\n");
      break;
    case 5: //MixedBeamLightInjection:
      fprintf(file,"'triggertype':'mixedbeamlightinjection',})}),\n");
      fprintf(file,"datastream='numil',\n");
      break;
    case 6: //MTBFBeamMuon:
      fprintf(file,"'triggertype':'mtbfbeammuon',})}),\n");
      fprintf(file,"datastream='bmuon',\n");
      break;
    case 7: //MTBFBeamOnly:
      fprintf(file,"'triggertype':'mtbfbeamonly',})}),\n");
      fprintf(file,"datastream='bonly',\n");
      break;
    default:
      fprintf(file,"'triggertype':'errortype',})}),\n");
      fprintf(file,"datastream='errorstream',\n");
  }
  fprintf(file,"startTime=SamTime('%llu',SAM.SamTimeFormat_UTCFormat),\n", (subRunStartTime/1000000L));
  fprintf(file,"endTime=SamTime('%llu',SAM.SamTimeFormat_UTCFormat),\n", (subRunFinishTime/1000000L));
  fprintf(file,"eventCount=%d,\n", gate);
  fprintf(file,"firstEvent=%llu,\n", firstGate);
  fprintf(file,"lastEvent=%llu,\n", globalGate);
  fprintf(file,"lumBlockRangeList=LumBlockRangeList([LumBlockRange(%llu,%llu)])\n", firstGate, globalGate);
  fprintf(file,")\n");

  fclose(file);
}

//---------------------------------------------------------
void ReadoutStateRecorder::WriteToSAMJSONFile()
{
  stateRecorderLogger.debugStream() << "Writing SAM JSON File...";

  FILE *file;

  if ( (file=fopen((args->samJSONFileName).c_str(), "w")) == NULL ) {
    stateRecorderLogger.errorStream() << "Error opening SAM file for writing!";
    return;
  }

  fprintf(file,"{\n");
  fprintf(file,"\"file_name\": \"%s\",\n", (args->dataFileBaseName).c_str());
  fprintf(file,"\"file_type\": \"importedDetector\",\n");
  fprintf(file,"\"file_format\": \"binary\",\n");
  fprintf(file,"\"crc\": {\"crc_value\": 666, \"crc_type\":\"adler 32 crc type\"},\n");
  fprintf(file,"\"group\": \"minerva\",\n");
#if MTEST
  fprintf(file,"\"data_tier\": \"binary-raw-test\",\n");
#else 
  fprintf(file,"\"data_tier\": \"binary-raw\",\n");
#endif
  char runType[50];
  switch (args->detector) { // Enumerations set by the DAQHeader class.
    case 0:
      sprintf(runType, "unknowndetector");
      break;
    case 1: 
      sprintf(runType, "pmtteststand");
      break;
    case 2:
      sprintf(runType, "trackingprototype");
      break;
    case 4:
      sprintf(runType, "testbeam");
      break;
    case 8:
      sprintf(runType, "frozendetector");
      break;
    case 16:
      sprintf(runType, "upstreamdetector");
      break;
    case 32:
      sprintf(runType, "minerva");
      break;
    case 64:
      sprintf(runType, "teststand");
      break;
    default:
      sprintf(runType, "errordetector");
  }
  fprintf(file,"\"runs\": [ [%d, %d, \"%s\"] ],\n", args->runNumber, args->subRunNumber, runType);
  fprintf(file,"\"application\": [\"online\", \"v09\", \"%s\"],\n", GIT_VERSION); //online, DAQ Heder, CVSTag
  fprintf(file,"\"file_size\": 1,\n");
  fprintf(file,"\"file_partition\": 1,\n");
  fprintf(file,"\"online.triggerconfig\": \"%s\",\n", (args->hardwareConfigFileName).c_str() );
  switch ((int)args->runMode) {
    case 0: //OneShot:
      fprintf(file,"\"online.triggertype\": \"oneshot\",\n");
      fprintf(file,"\"data_stream\": \"pdstl\",\n");
      break;
    case 1: //NuMIBeam:
      fprintf(file,"\"online.triggertype\": \"numibeam\",\n");
      fprintf(file,"\"data_stream\": \"numib\" ,\n");
      break;
    case 2: //Cosmics:
      fprintf(file,"\"online.triggertype\": \"cosmics\",\n");
      fprintf(file,"\"data_stream\": \"cosmc\",\n");
      break;
    case 3: //PureLightInjection:
      fprintf(file,"\"online.triggertype\": \"purelightinjection\",\n");
      fprintf(file,"\"data_stream\": \"linjc\",\n");
      break;
    case 4: //MixedBeamPedestal:
      fprintf(file,"\"online.triggertype\": \"mixedbeampedestal\",\n");
      fprintf(file,"\"data_stream\": \"numip\",\n");
      break;
    case 5: //MixedBeamLightInjection:
      fprintf(file,"\"online.triggertype\": \"mixedbeamlightinjection\",\n");
      fprintf(file,"\"data_stream\": \"numil\",\n");
      break;
    case 6: //MTBFBeamMuon:
      fprintf(file,"\"online.triggertype\": \"mtbfbeammuon\",\n");
      fprintf(file,"\"data_stream\": \"bmuon\",\n");
      break;
    case 7: //MTBFBeamOnly:
      fprintf(file,"\"online.triggertype\": \"mtbfbeamonly\",\n");
      fprintf(file,"\"data_stream\": \"bonly\",\n");
      break;
    default:
      fprintf(file,"\"online.triggertype\": \"errortype\",\n");
      fprintf(file,"\"data_stream\": \"errorstream\",\n");
  }
  fprintf(file,"\"start_time\": %llu,\n", (subRunStartTime/1000000L));
  fprintf(file,"\"end_time\": %llu,\n", (subRunFinishTime/1000000L));
  fprintf(file,"\"event_count\": %d,\n", gate);
  fprintf(file,"\"first_event\": %llu,\n", firstGate);
  fprintf(file,"\"last_event\": %llu,\n", globalGate);
  fprintf(file,"\"lum_block_ranges\": [[%llu, %llu]]\n", firstGate, globalGate);
  fprintf(file,"}\n");

  fclose(file);
}

//---------------------------------------------------------
//! Log basic information about the last successful readout gate.
void ReadoutStateRecorder::WriteLastTriggerDataToFile()
{
  FILE *file;

  if ( NULL == (file=fopen((args->lastTriggerFileName).c_str(),"w")) ) {
    stateRecorderLogger.errorStream() << "Error opening last trigger file for writing!";
    return; 
  }
  else {
    if (!(gate%10)) {
      stateRecorderLogger.infoStream() << "Writing info for trigger " << gate << " to file " << args->lastTriggerFileName;
    }
  }

  fprintf(file, "run=%d\n",      args->runNumber);
  fprintf(file, "subrun=%d\n",   args->subRunNumber);
  fprintf(file, "number=%d\n",   gate);
  fprintf(file, "type=%d\n",     triggerType);
  fprintf(file, "time=%llu\n",   gateStartTime);

  fclose(file);
} // WriteLastTriggerDataToFile()

//---------------------------------------------------------
//! Log basic information about the last successful readout gate.
void ReadoutStateRecorder::WriteLastTriggerDataToFileMTest()
{
  FILE *file;

  std::string filename = "/home/nfs/minerva/daq/last_trigger.dat";

  if ( NULL == (file=fopen(filename.c_str(),"w")) ) {
    stateRecorderLogger.errorStream() << "Error opening " << filename << "for writing!";
    return; 
  }
  else {
    if (!(gate%10)) {
      stateRecorderLogger.infoStream() << "Writing info for trigger " << gate 
        << " to file " << filename;
    }
  }

  stateRecorderLogger.infoStream() << "MTest: write trigger info to last_trigger.dat - " << gate << " (gate)";
  fprintf(file, "run=%d\n",      args->runNumber);
  fprintf(file, "subrun=%d\n",   args->subRunNumber);
  fprintf(file, "number=%d\n",   gate);
  fprintf(file, "type=%d\n",     triggerType);
  fprintf(file, "time=%llu\n",   gateStartTime);

  fclose(file);
} // end WriteLastTriggerDataToFileMTest()

//-----------------------------
std::ostream& operator<<(std::ostream& out, const ReadoutStateRecorder& s)
{
  out << "Gate = " << s.gate << "; ";
  out << "Trigger Type = " << s.triggerType << "; ";
  out << "Globale Gate = " << s.globalGate << "; ";
  out << "Gate Start Time = " << s.gateStartTime << "; ";
  out << "Gate Finish Time = " << s.gateFinishTime << "; ";
  return out;
}


#endif
