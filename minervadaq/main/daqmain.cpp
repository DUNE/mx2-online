#ifndef daqmain_cxx
#define daqmain_cxx

#include <fstream>
#include <iostream>
#include <sstream>

#include "daqmain.h"

// log4cpp message levels:
//	emergStream(), fatalStream(), alert..., crit..., error..., warn..., notice..., info..., debug...
log4cpp::Appender* baseAppender;
log4cpp::Category& rootCat = log4cpp::Category::getRoot();
log4cpp::Category& daqmain = log4cpp::Category::getInstance(std::string("daqmain"));

int main( int argc, char * argv[] ) 
{
  int runNumber = 1;
  int subRunNumber = 0;
  int numberOfGates = 100;
  int runMode = 0;  // encoded (RunningMode)
  int detector;
  int detectorConfigCode;
  int ledLevel;
  int ledGroup;
  int hardwareInitLevel; 
  int networkPort;
  std::string etFileName;
  std::string logFileName;
  std::string samFileName;
  std::string hardwareConfigFileName;


  return 0;
}

#endif
