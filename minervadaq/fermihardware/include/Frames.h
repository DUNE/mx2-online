#ifndef Frames_h
#define Frames_h

/* system headers go here */
#include <iostream>
#include <fstream>

/* custom headers go here */
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

/*! \class Frames
 *
 * \brief The base class for all LVDS data exchange frames.
 *
 */

class Frames {
  /*! This class makes up the general base frames for use in communicating
   *  through the crate & cards.  
   */
  protected:
    static const int MinHeaderLength;
    static const int ADCFrameLength;
    static const int NDiscrChPerTrip;
    unsigned char FrameID[2];        // Starts out Empty, filled on return of message
    unsigned char frameHeader[9];    // a frame header, add this to the message
    unsigned char *outgoingMessage;  // the character string for the message sent to a device
    unsigned char broadcastCommand[1], febNumber[1], 
                  messageDirection[1], targetDevice[1], 
                  deviceFunction[1];
    int IncomingMessageLength, OutgoingMessageLength;

  public:
    Frames();
    virtual ~Frames() { };

    unsigned char *message; //the message that will be sent or received. mostly received...
    void printMessageBufferToLog( int buffersize );

    /*! transmission frame...These are for sending messages out */
    void MakeDeviceFrameTransmit(Devices, Broadcasts, Directions, unsigned int, unsigned int); 
    void MakeHeader();
    virtual void MakeMessage();
    virtual int DecodeRegisterValues(int a) = 0;
    void DecodeHeader();
    bool CheckForErrors();

    inline unsigned char *GetOutgoingMessage() {return outgoingMessage;};
    void DeleteOutgoingMessage() {delete [] outgoingMessage;};

    void inline SetIncomingMessageLength(int a) {IncomingMessageLength = a;};
    int inline GetIncomingMessageLength() {return IncomingMessageLength;};
    int inline GetOutgoingMessageLength() {return OutgoingMessageLength;};
    int inline GetFEBNumber() {return (int)febNumber[0];};
    int inline GetDeviceType() {return (int) targetDevice[0];};

};

#endif
