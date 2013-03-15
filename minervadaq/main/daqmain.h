#ifndef daqmain_h
#define daqmain_h
/*! \file daqmain.h
*/

void SetUpSigAction();
void quitsignal_handler(int signum);

bool continueRunning;

#endif
