#ifndef LVDSFrame_h
#define LVDSFrame_h
/*! \file LVDSFrame.h
*/

#include <iostream>
#include <fstream>
#include <tr1/memory>  // for shared_ptrs

#include "FrameTypes.h"
#include "MinervaDAQSizes.h"
#include "TripTTypes.h"
#include "FlashTypes.h"
#include "log4cppHeaders.h"

/*! 
  \class LVDSFrame
  \brief The base class for all LVDS data exchange frames.
  \author Gabriel Perdue

  LVDSFrame is the base class for advanced frame types. It is not abstract 
  and is occasionally instantiated (e.g., when reading a SequencerReadoutBlock).
  */

class LVDSFrame {

  friend std::ostream& operator<<(std::ostream&, const LVDSFrame&);

  protected:
  unsigned char FrameID[2];        
  unsigned char frameHeader[ MinervaDAQSizes::FrameHeaderLengthOutgoing ];    
  unsigned char *outgoingMessage;  
  unsigned char *receivedMessage;  
  unsigned char febNumber[1], targetDevice[1], deviceFunction[1], 
                broadcastCommand[1], messageDirection[1];
  inline void DeleteOutgoingMessage() { delete [] outgoingMessage; outgoingMessage = NULL; };

  public:
  LVDSFrame();
  virtual ~LVDSFrame();

  void MakeDeviceFrameTransmit(FrameTypes::Devices, FrameTypes::Broadcasts, 
      FrameTypes::Directions, unsigned int, unsigned int); 
  void MakeOutgoingHeader();

  virtual void MakeMessage();
  virtual void DecodeRegisterValues();
  virtual unsigned int GetOutgoingMessageLength();

  unsigned short ReceivedMessageLength() const;
  unsigned short ReceivedMessageStatus() const;
  void DecodeHeader();
  bool CheckForErrors();
  void printReceivedMessageToLog();

  inline unsigned char *GetOutgoingMessage() const { return outgoingMessage; };
  inline unsigned char *GetReceivedMessage() const { return receivedMessage; };
  inline void SetReceivedMessage(unsigned char* buffer) { receivedMessage = buffer; };
  inline int GetFEBNumber() const { return (int)febNumber[0]; };
  inline int GetDeviceType() const { return (int)targetDevice[0]; };

};

#endif
