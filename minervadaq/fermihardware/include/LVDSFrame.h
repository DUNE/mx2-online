#ifndef LVDSFrame_h
#define LVDSFrame_h

#include <iostream>
#include <fstream>

#include "FrameTypes.h"
#include "MinervaDAQtypes.h"
#include "TripTTypes.h"
#include "FlashTypes.h"
#include "log4cppHeaders.h"

/*********************************************************************************
 * Class for creating general Frame header objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

/*! \class LVDSFrame
 *
 * \brief The base class for all LVDS data exchange frames.
 *
 */

class LVDSFrame {
  protected:
    unsigned char FrameID[2];        
    unsigned char frameHeader[9];    
    unsigned char *outgoingMessage;  
    unsigned char *receivedMessage;  
    unsigned char febNumber[1], targetDevice[1], deviceFunction[1], 
                  broadcastCommand[1], messageDirection[1];

  public:
    LVDSFrame();
    virtual ~LVDSFrame();

    void MakeDeviceFrameTransmit(Devices, Broadcasts, Directions, unsigned int, unsigned int); 
    void MakeOutgoingHeader();

    virtual void MakeMessage();
    virtual void DecodeRegisterValues();
    virtual unsigned int GetOutgoingMessageLength();

    unsigned short ReceivedMessageLength();
    unsigned short ReceivedMessageStatus();
    void DecodeHeader();
    bool CheckForErrors();
    void printReceivedMessageToLog();

    inline unsigned char *OutgoingMessage() { return outgoingMessage; };
    inline unsigned char *ReceivedMessage() { return receivedMessage; };
    inline int GetFEBNumber() { return (int)febNumber[0]; };
    inline int GetDeviceType() { return (int)targetDevice[0]; };

};

#endif
