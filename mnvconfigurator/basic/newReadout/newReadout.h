#ifndef newReadout_h
#define newReadout_h

// Minerva Headers
#include "acquire.h"
#include "MinervaDAQtypes.h"
#include "controller.h"
#include "feb.h"
#include "adctdc.h"
#include "readoutObject.h"

const CVRegisters ControllerStatusAddress = cvStatusReg;
const CVDataWidth DW                      = cvD16;
const CVDataWidth DWS                     = cvD16_swapped;
const CVAddressModifier AM                = cvA24_U_DATA;
const CVAddressModifier BLT_AM            = cvA24_U_BLT;
unsigned char sendMessage[]               = {0x01,0x01}; //Send to CROC to send FIFO message to FEB
unsigned char crocChanResetValue[]        = {0x02,0x02}; //Good for clear status reg., reset reg.
unsigned char crocDPMResetValue[]         = {0x08,0x08};
unsigned char crocClearAndResetValue[]    = {0x0A,0x0A};
unsigned char crocResetAndTestPulseMask[] = {0x0F,0x0F}; // enable reset (0F) and test pulse (2nd 0F) 

const int numberOfHits = 6;
const bool checkForMessRecvd      = true;
const bool doNotCheckForMessRecvd = false;

// A buffer for handling BLT data.
unsigned char *DPMData; 

// Initialize the CRIM for basic fiddling.
void InitCRIM(crim *theCrim, int runningMode=0);
// Initialize the CROC for basic fiddling.
void InitCROC(croc *theCroc);
// Function to build a list of FEB objects.
int MakeFEBList(channels *theChain, int nFEBs=11);

// Open a gate
int FastCommandOpenGate(croc *theCroc);

// Send a Clear and Reset to a CROC FE Channel
void SendClearAndReset(channels *theChain);  
// Read the status register on a CROC FE Channel - add a flag to see if we should check for the message recv'd.
int ReadStatus(channels *theChain, bool receiveCheck);

// Initialize list of readoutObjects
void InitializeReadoutObjects(std::list<readoutObject*> *objectList);

// send messages to a generic device using normal write cycle
// -> write the outgoing message from the device to the FE Channel FIFO, send the message
template <class X> void SendFrameData(X *device, channels *theChannel);

// send messages to a generic device using FIFO BLT write cycle
// -> write the outgoing message from the device to the FE Channel FIFO using BLT, send the message 
template <class X> void SendFrameDataFIFOBLT(X *device, channels *theChannel);

// recv messages for a generic device
// -> read DPM pointer, read BLT, store data in *device* buffer
// -> should be used primarily for debugging and for building the FEB list.
template <class X> int RecvFrameData(X *device, channels *theChannel);

// recv messages 
// -> read DPM pointer, read BLT, store data in *channel* buffer
int RecvFrameData(channels *theChannel);

#endif
