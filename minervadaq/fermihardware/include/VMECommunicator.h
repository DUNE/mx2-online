/*! \file VMECommunicator.h 
 *
 * \brief The header file for the VMECommunicator class.
 *
 * This class is a base class for modules that can communicate via the VME protocol.
 */

#include "CAENVMEtypes.h"
#include "CAENVMElib.h"

#include "Controller.h"
#include "log4cppHeaders.h"

/*! \class VMECommunicator
 *  \brief A class which wraps the CAEN VME access functions.
 *
 */


class VMECommunicator {

  private:
    Controller*        controller;
    int                controllerHandle;
    log4cpp::Appender* commAppender;

  protected:
    unsigned int       address;             // this is the most basic address available 
                                            // (for channels, it will be the CROC address), bit-shifted
    CVAddressModifier  addressModifier;
    CVAddressModifier  bltAddressModifier;  // block transfers use a different address modifier
    CVDataWidth        dataWidth;
    CVDataWidth        dataWidthSwapped;
    CVDataWidth        dataWidthReg;        // use a different data width for talking to registers (as opposed to data)
    CVDataWidth        dataWidthSwappedReg; // use a different data width for talking to registers (as opposed to data)

    void exitIfError( int error, const std::string& msg );

  public:

    VMECommunicator( unsigned int address, log4cpp::Appender* appender, Controller* controller );
    ~VMECommunicator(); 

    Controller* GetController();

    int WriteCycle(int messageLength, unsigned char *send_message,  unsigned int address, 
        CVAddressModifier AM, CVDataWidth DW); /*!<Member function for writing to a VME address */

    int ReadCycle(unsigned char *received_message,  unsigned int address, 
        CVAddressModifier AM, CVDataWidth DW); /*!<Member function for reading from a VME address */

    int ReadBLT(unsigned char *received_message,  int blocks, unsigned int address, 
        CVAddressModifier AM, CVDataWidth DW); /*!<Member function for block-transfer reads */

    int WriteFIFOBLT(int messageLength, unsigned char *send_message,  unsigned int address, 
        CVAddressModifier AM, CVDataWidth DW); /*!<Member function for block-transfer writes to the FIFO */
};
