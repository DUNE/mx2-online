/*! \file acquire.h 
 *
 * \brief The header file for the CAEN VME library access functions.
 *
 * These functions are just for coding convenience in other places.
 *
 */

/*! 
 *  CAEN VME specific headers here 
 *  */
#include "CAENVMEtypes.h"
#include "CAENVMElib.h"

#include <boost/thread/mutex.hpp>

/*! \class acquire
 *  \brief A class which wraps the CAEN VME access functions.
 *
 *  This class wraps the CAEN Read and Write functions needed for the 
 *  DAQ to access data from the VME bus.  This is done primarily for convenience and 
 *  allows a uniform method for accessing Read and Write functions 
 *
 *  */

class acquire {
  private:
    boost::mutex mutex; /*!<A boost Multiple Exclusion for threaded operation */
  public:
  /*! Default Constructor */
  acquire() { };
  /*! Default Destructor */
  ~acquire() { }; 
  int WriteCycle(int handle, int ml, unsigned char *send_message,  unsigned int address, 
                 CVAddressModifier AM, CVDataWidth DW); /*!<Member function for writing to a VME address */
  int ReadCycle(int handle, unsigned char *received_message,  unsigned int address, 
                 CVAddressModifier AM, CVDataWidth DW); /*!<Member function for reading from a VME address */
  int ReadBLT(int handle, unsigned char *received_message,  int blocks, unsigned int address, 
              CVAddressModifier AM, CVDataWidth DW); /*!<Member function for block-transfer reads */
};
