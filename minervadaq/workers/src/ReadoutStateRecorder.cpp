#ifndef ReadoutStateRecorder_cxx
#define ReadoutStateRecorder_cxx

/*! \file 
 *
 * ReadoutStateRecorder.cpp:  
 */

#include "ReadoutStateRecorder.h"
#include "exit_codes.h"

log4cpp::Category& stateRecorderLogger = log4cpp::Category::getInstance(std::string("stateRecorderLogger"));

//---------------------------
ReadoutStateRecorder::ReadoutStateRecorder( const DAQWorkerArgs* theArgs, 
    log4cpp::Priority::Value priority ) :
  gate(0),
  triggerType(Triggers::UnknownTrigger),
  firstGate(0),
  globalGate(0),
  gateStartTime(0),
  gateFinishTime(0),
  MINOSSGATE(0),
  args(theArgs)
{
  stateRecorderLogger.setPriority(priority);
  this->GetGlobalGateFromFile();
  firstGate = globalGate + 1;
  stateRecorderLogger.debugStream() << "Created new ReadoutStateRecorder: " << *this;
}

//---------------------------
ReadoutStateRecorder::~ReadoutStateRecorder() 
{
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

//---------------------------
bool ReadoutStateRecorder::FinishGate()
{
  stateRecorderLogger.debugStream() << "ReadoutStateRecorder::FinishGate...";
  this->WriteGlobalGateToFile();
  this->WriteToSAMFile();
  this->WriteLastTriggerDataToFile();
  return true;
}

//---------------------------
Triggers::TriggerType ReadoutStateRecorder::GetNextTriggerType()
{
	using namespace Triggers;
	using namespace Modes;
  stateRecorderLogger.debugStream() << "GetNextTriggerType";
  triggerType = UnknownTrigger;
  switch (args->runMode) {
    case OneShot:
      triggerType = Pedestal;
      stateRecorderLogger.debugStream() << " Running Mode is OneShot.";
      break;
    case NuMIBeam:
      triggerType = NuMI;
      stateRecorderLogger.debugStream() << " Running Mode is NuMI Beam.";
      break;
    case PureLightInjection:
      triggerType = LightInjection;
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
    return; // throw? 
  }
  globalGateFile.close();
  stateRecorderLogger.debugStream() << "Put global gate " << globalGate;
}

//-----------------------------
std::tr1::shared_ptr<DAQHeader> ReadoutStateRecorder::GetDAQHeader( HeaderData::BankType bankType )
{
  stateRecorderLogger.debugStream() << "GetDAQHeader...";
  unsigned int minos = MINOSSGATE; 
  unsigned long long readoutTimeLong = gateFinishTime - gateStartTime;
  unsigned int readoutTime = (unsigned int)readoutTimeLong;
/* #ifndef GOFAST */
  stateRecorderLogger.debugStream() << " readoutTimeLong = " << readoutTimeLong;
  stateRecorderLogger.debugStream() << " readoutTime     = " << readoutTime;
  stateRecorderLogger.debugStream() << " MINOSSGATE      = " << MINOSSGATE;
/* #endif */

  // sadly, these are probably not useful anymore.
  unsigned short int error = 0;
  unsigned short nADCFrames  = 0; 
  unsigned short nDiscFrames = 0;
  unsigned short nFPGAFrames = 0;

  FrameHeader * frameHeader = new FrameHeader(0,0,0,bankType,0,0,0,daqHeaderSize);

  std::tr1::shared_ptr<DAQHeader> daqHeader( 
      new DAQHeader(args->detector, args->detectorConfigCode, args->runNumber, 
        args->subRunNumber, triggerType, args->ledGroup, args->ledLevel,
        globalGate, gate, gateStartTime, error, minos, readoutTime,
        frameHeader,  nADCFrames, nDiscFrames, nFPGAFrames)
      );

  delete frameHeader;
  return daqHeader;
}

//---------------------------------------------------------
void ReadoutStateRecorder::WriteToSAMFile()
{
  stateRecorderLogger.debugStream() << "Writing SAM File...";

  FILE *file;

  if ( (file=fopen((args->samFileName).c_str(), "w")) == NULL ) {
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
  fprintf(file,"fileName = '%s',\n", (args->dataFileName).c_str());
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
  fprintf(file,"applicationFamily=ApplicationFamily('online','v09','v08-01-01'),\n"); //online, DAQ Heder, CVSTag
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
  fprintf(file,"startTime=SamTime('%llu',SAM.SamTimeFormat_UTCFormat),\n", gateStartTime);
  fprintf(file,"endTime=SamTime('%llu',SAM.SamTimeFormat_UTCFormat),\n", gateFinishTime);
  fprintf(file,"eventCount=%d,\n", gate);
  fprintf(file,"firstEvent=%llu,\n", firstGate);
  fprintf(file,"lastEvent=%llu,\n", globalGate);
  fprintf(file,"lumBlockRangeList=LumBlockRangeList([LumBlockRange(%llu,%llu)])\n", firstGate, globalGate);
  fprintf(file,")\n");

  fclose(file);
}

//---------------------------------------------------------
void ReadoutStateRecorder::WriteLastTriggerDataToFile()
{
  FILE *file;

  if ( NULL == (file=fopen((args->lastTriggerFileName).c_str(),"w")) ) {
    stateRecorderLogger.errorStream() << "Error opening last trigger file for writing!";
    return; // throw
  }
  else {
    if (!(gate%10)) {
      stateRecorderLogger.infoStream() << "Writing info for trigger " << gate 
        << " to file " << args->lastTriggerFileName;
    }
  }

  fprintf(file, "run=%d\n",      args->runNumber);
  fprintf(file, "subrun=%d\n",   args->subRunNumber);
  fprintf(file, "number=%d\n",   gate);
  fprintf(file, "type=%d\n",     triggerType);
  fprintf(file, "time=%llu\n",   gateStartTime);

  fclose(file);
}

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
