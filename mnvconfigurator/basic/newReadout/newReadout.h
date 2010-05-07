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

// Initialize the CRIM for basic fiddling.
void InitCRIM(controller *daqController, acquire *daqAcquire, crim *myCrim, int runningMode=0);
// Initialize the CROC for basic fiddling.
void InitCROC(controller *daqController, acquire *daqAcquire, croc *myCroc);
// Function to build a list of FEB objects.
int BuildFEBList(controller *daqController, acquire *daqAcquire, croc *myCroc, int chainID, int nFEBs=11);

// Send a Clear and Reset to a CROC FE Channel
void SendClearAndReset(controller *daqController, acquire *daqAcquire, channels *theChain);  
// Read the status register on a CROC FE Channel - add a flag to see if we should check for the message recv'd.
int ReadStatus(controller *daqController, acquire *daqAcquire, channels *theChain, bool receiveCheck);


#endif
