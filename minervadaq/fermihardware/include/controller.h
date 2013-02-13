#ifndef controller_h
#define controller_h

#include <iostream>
#include <cstdlib> 
#include <vector>
#include <fstream>

#include "CAENVMEtypes.h"
#include "CAENVMElib.h"

#include "crim.h"
#include "croc.h"
#include "ecroc.h"
#include "log4cppHeaders.h"

/*********************************************************************************
* Class for creating CAEN VME V2718 Controller objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
**********************************************************************************/

// Further category hierarchy.
log4cpp::Category& controllerLog = log4cpp::Category::getInstance(std::string("controller"));


/*! \class controller
 *
 * \brief A class for handling data associated with a CAEN V2718 VME controller 
 */
class controller {
	private:
		unsigned int address, slotNumber, pciSlotNumber, boardNumber; /*!< controller parameters at PC */

		/*! CAEN VME data */
		CVBoardTypes controllerType, bridgeType;  
		CVAddressModifier addressModifier;
		CVDataWidth dataWidth;

		std::vector<crim*> interfaceModules; 
		std::vector<croc*> readOutControllers;  
		std::vector<ecroc*> eReadOutControllers; 

		/*! these are the controller registers for the VME controller */
		unsigned short status, control, irq, irqMask, input, output,
			clearOutput, inputMux, inputMuxClear, outPutMux;
		char firmware[1];
		int transferBytes, controller_id;

	public: 

		unsigned short *shortBuffer; /*!<a short buffer for registers*/
		int handle; /*!<a device handle returned by the initialization function*/

		/*! the specialty constructor */
		controller(int a, int id) { 
			address         = a;
			addressModifier = cvA24_U_DATA; // default address modifier
			dataWidth       = cvD16;    // default data width
			controllerType  = cvV2718;  // this is the only controller board we have
			bridgeType      = cvA2818;  // this is the only PCI card we have
			slotNumber      = 0; // by construction 
			pciSlotNumber   = 0; // link - probably always 0.
			boardNumber     = 0; // we basically use controller_id for this...
			handle          = -1;
			firmware[0]     = 0;
			controller_id   = id; //an internal ID used for sorting data
			controllerLog.setPriority(log4cpp::Priority::DEBUG);
		};

		/*! the specialty destructor */
		~controller() {
			for (std::vector<crim*>::iterator p=interfaceModules.begin();
				p!=interfaceModules.end();p++) delete (*p);
			interfaceModules.clear();
			for (std::vector<croc*>::iterator p=readOutControllers.begin();
				p!=readOutControllers.end();p++) delete (*p);
			readOutControllers.clear();
		};

		/*! Get functions */
		int inline GetAddress() {return address;};
		CVAddressModifier inline GetAddressModifier() {return addressModifier;};
		CVDataWidth inline GetDataWidth() {return dataWidth;};
		CVBoardTypes inline GetControllerType() {return controllerType;};
		CVBoardTypes inline GetBridgeType() {return bridgeType;};
		int inline GetHandle() {return handle;};
		int inline GetID() {return controller_id;};

		void MakeCrim(unsigned int vmeAddress, int crimID); // Address should already be shifted.
		void MakeCroc(unsigned int vmeAddress, int crocID); // Address should already be shifted.
		void MakeECroc(unsigned int vmeAddress, int crocID); // Address should already be shifted.

		// By convention (& hopefully construction), the first CRIM (indexed to 1) 
		// will always be the MASTER CRIM (the interrupt handler we poll or IACK).
		crim *GetCrim();             // Return the pointer to the *first* CRIM. (Worth doing fast.)
		crim *GetCrim(int crimID);   // Return the pointer to the requested CRIM.
		croc *GetCroc(int crocID);   // Return the pointer to the requested CROC.
		ecroc *GetECroc(int crocID);  // Return the pointer to the requested CROC.
		std::vector<crim*> inline *GetCrimVector() {return &interfaceModules;};
		std::vector<croc*> inline *GetCrocVector() {return &readOutControllers;};
		std::vector<ecroc*> inline *GetECrocVector() {return &eReadOutControllers;};

		void inline SetDataWidth(CVDataWidth a) {dataWidth=a;}; 

		int ContactController();
		int GetCrimStatus(int crimID); 
		int GetCrocStatus(int crocID); 
		int GetECrocStatus(int crocID); 
		int GetCrimVectorLength();
		int GetCrocVectorLength(); 
		int GetECrocVectorLength(); 
		
		void ReportError(int error);


};
#endif
