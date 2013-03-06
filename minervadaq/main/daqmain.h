#ifndef daqmain_h
#define daqmain_h


void SetUpSigAction();
void quitsignal_handler(int signum);

bool continueRunning;

#endif
