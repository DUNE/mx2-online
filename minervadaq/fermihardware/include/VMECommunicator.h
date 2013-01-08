/*! \file VMECommunicator.h 
 *
 * \brief The header file for the VMECommunicator class.
 *
 * This class is a base class for modules that can communicate via the VME protocol.
 */

#include "CAENVMEtypes.h"
#include "CAENVMElib.h"

#include "log4cppHeaders.h"

/*! \class VMECommunicator
 *  \brief A class which wraps the CAEN VME access functions.
 *
 */

class VMECommunicator {

  private:

  protected:
    unsigned int      address;
    CVAddressModifier addressModifier;
    CVDataWidth       dataWidth;
    CVDataWidth       dataWidthSwapped;

    log4cpp::Appender* commAppender;

  public:

    VMECommunicator( unsigned int address, log4cpp::Appender* appender=0 );
    ~VMECommunicator() { }; 

    unsigned int      GetAddress();
    CVAddressModifier GetAddressModifier();
    CVDataWidth       GetDataWidth();
    CVDataWidth       GetDataWidthSwapped();


    int WriteCycle(int handle, int ml, unsigned char *send_message,  unsigned int address, 
        CVAddressModifier AM, CVDataWidth DW); /*!<Member function for writing to a VME address */

    int ReadCycle(int handle, unsigned char *received_message,  unsigned int address, 
        CVAddressModifier AM, CVDataWidth DW); /*!<Member function for reading from a VME address */

    int ReadBLT(int handle, unsigned char *received_message,  int blocks, unsigned int address, 
        CVAddressModifier AM, CVDataWidth DW); /*!<Member function for block-transfer reads */

    int WriteFIFOBLT(int handle, int ml, unsigned char *send_message,  unsigned int address, 
        CVAddressModifier AM, CVDataWidth DW); /*!<Member function for block-transfer writes to the FIFO */
};
