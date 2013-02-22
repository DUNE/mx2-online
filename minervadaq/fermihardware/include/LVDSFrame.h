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
    static const int MinHeaderLength;
    static const int NDiscrChPerTrip;
    unsigned char FrameID[2];        
    unsigned char frameHeader[9];    // a frame header, add this to the message
    unsigned char *outgoingMessage;  // the character string for the message sent to a device
    unsigned char broadcastCommand[1], febNumber[1], 
                  messageDirection[1], targetDevice[1], 
                  deviceFunction[1];
    int IncomingMessageLength, OutgoingMessageLength; // careful, these break things
                                                      // if operations are done in a non-standard 
                                                      // order. TODO: get rid of these for a 
                                                      // different mechanism

  public:
    LVDSFrame();
    virtual ~LVDSFrame() { };

    unsigned char *message; 
    void printMessageBufferToLog( int buffersize );

    void MakeDeviceFrameTransmit(Devices, Broadcasts, Directions, unsigned int, unsigned int); 
    void MakeOutgoingHeader();
    virtual void MakeMessage();
    virtual void DecodeRegisterValues();
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
