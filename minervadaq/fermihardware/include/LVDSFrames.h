#ifndef LVDSFrames_h
#define LVDSFrames_h

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

/*! \class LVDSFrames
 *
 * \brief The base class for all LVDS data exchange frames.
 *
 */

class LVDSFrames {
  protected:
    static const int MinHeaderLength;
    static const int NDiscrChPerTrip;
    unsigned char FrameID[2];        
    unsigned char frameHeader[9];    // a frame header, add this to the message
    unsigned char *outgoingMessage;  // the character string for the message sent to a device
    unsigned char broadcastCommand[1], febNumber[1], 
                  messageDirection[1], targetDevice[1], 
                  deviceFunction[1];
    int IncomingMessageLength, OutgoingMessageLength;

  public:
    LVDSFrames();
    virtual ~LVDSFrames() { };

    unsigned char *message; 
    void printMessageBufferToLog( int buffersize );

    void MakeDeviceFrameTransmit(Devices, Broadcasts, Directions, unsigned int, unsigned int); 
    void MakeHeader();
    virtual void MakeMessage();
    virtual int DecodeRegisterValues(int a) = 0;
    void DecodeHeader();
    bool CheckForErrors();

    inline unsigned char *GetOutgoingMessage() { return outgoingMessage; };
    inline void DeleteOutgoingMessage() { delete [] outgoingMessage; };

    void inline SetIncomingMessageLength(int a) { IncomingMessageLength = a; };
    int inline GetIncomingMessageLength() { return IncomingMessageLength; };
    int inline GetOutgoingMessageLength() { return OutgoingMessageLength; };
    int inline GetFEBNumber() { return (int)febNumber[0]; };
    int inline GetDeviceType() { return (int)targetDevice[0]; };

};

#endif
