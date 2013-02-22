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
    unsigned char broadcastCommand[1], febNumber[1], 
                  messageDirection[1], targetDevice[1], 
                  deviceFunction[1];
    unsigned int IncomingMessageLength, OutgoingMessageLength; 

  public:
    LVDSFrame();
    virtual ~LVDSFrame() { };

    unsigned char *message; 
    void printMessageBufferToLog( int buffersize );

    void MakeDeviceFrameTransmit(Devices, Broadcasts, Directions, unsigned int, unsigned int); 
    void MakeOutgoingHeader();
    virtual void MakeMessage();
    /* virtual void DecodeRegisterValues(); */
    virtual int DecodeRegisterValues(int a) = 0;
    void DecodeHeader();
    bool CheckForErrors();

    inline unsigned char *GetOutgoingMessage() { return outgoingMessage; };
    inline void DeleteOutgoingMessage() { delete [] outgoingMessage; };

    inline void SetIncomingMessageLength(int a) { IncomingMessageLength = a; };
    inline int GetIncomingMessageLength() { return IncomingMessageLength; };
    inline int GetOutgoingMessageLength() { return OutgoingMessageLength; };
    inline int GetFEBNumber() { return (int)febNumber[0]; };
    inline int GetDeviceType() { return (int)targetDevice[0]; };

};

#endif
