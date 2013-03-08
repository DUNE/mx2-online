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
  triggerType(0),
  globalGate(0),
  gateStartTime(0),
  gateFinishTime(0),
  args(theArgs)
{
  stateRecorderLogger.setPriority(priority);
  stateRecorderLogger.debugStream() << "Created new ReadoutStateRecorder: " << *this;
}

//---------------------------
ReadoutStateRecorder::~ReadoutStateRecorder() 
{
}


//---------------------------
bool ReadoutStateRecorder::BeginNextGate()
{
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
  this->WriteGlobalGateToFile();
  this->WriteToSAMFile();
  this->WriteLastTriggerDataToFile();
  return true;
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
  unsigned short int error = 0;
  unsigned int minos = 0;        // TODO - MINOS Time from CRIM
  unsigned int readoutTime = 0;  // TODO fix this
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
