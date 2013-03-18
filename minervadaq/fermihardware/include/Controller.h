#ifndef Controller_h
#define Controller_h
/*! \file Controller.h
*/

#include <iostream>
#include <cstdlib> 
#include <vector>
#include <fstream>

#include "CAENVMEtypes.h"
#include "CAENVMElib.h"

#include "log4cppHeaders.h"

/*********************************************************************************
* Class for creating CAEN VME V2718 Controller objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Gabriel Perdue, The University of Rochester
**********************************************************************************/

/*! \class Controller
 *
 * \brief A class for handling data associated with a CAEN V2718 VME Controller.
 */
class Controller {
	private:
		unsigned int address, slotNumber, pciSlotNumber, boardNumber; /*!< Controller parameters at PC */

		CVBoardTypes      controllerType, bridgeType;  
		CVAddressModifier addressModifier;
		CVDataWidth       dataWidth;

		char firmware[1];
		int crateNumber;
		int handle; /*!<a device handle returned by the initialization function*/
		unsigned short *shortBuffer; /*!<a short buffer for messaging*/

		/*! these are the controller registers for the VME controller - basically unused, will implement someday? */
		unsigned short status, control, irq, irqMask, input, output,
			clearOutput, inputMux, inputMuxClear, outPutMux;

	public: 

		explicit Controller(int addr, int crateNum);
		~Controller();

		int Initialize();

		unsigned int GetAddress() const;
		CVAddressModifier GetAddressModifier() const;
		CVDataWidth GetDataWidth() const;
		CVBoardTypes GetControllerType() const;
		CVBoardTypes GetBridgeType() const;
		int GetHandle() const;
		int GetCrateNumber() const;

		void ReportError(int error) const;


};
#endif
