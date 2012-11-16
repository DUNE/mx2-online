#ifndef controller_h
#define controller_h

/* system specific headers here */
#include <iostream>
#include <cstdlib> //this gives us access to "sleep" so we can
				//pause and wait for something to happen if needed.
#include <vector>
#include <fstream>

/* CAEN VME specific headers here */
#include "CAENVMEtypes.h"
#include "CAENVMElib.h"

/* custom headers here */
#include "crim.h"
#include "croc.h"
#include "log4cppHeaders.h"

/*********************************************************************************
* Class for creating CAEN VME V2718 Controller objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
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

		std::vector<crim*> interfaceModule; /*!< A vector of CROC Interface Module (CRIM) objects. */
		std::vector<croc*> readOutController;  /*!< A vector of CROC objects. */
		std::vector<channels*> feChannels;  /*!< A vector of CROC FE channel objects. */
		/*! these are the controller registers for the VME controller */
		unsigned short status, control, irq, irqMask, input, output,
			clearOutput, inputMux, inputMuxClear, outPutMux;
		char firmware[1];
		int transferBytes, crocVectorLength, crimVectorLength, feChannelsVectorLength, controller_id;

		// log4cpp appender for printing log statements.
		log4cpp::Appender* ctrlAppender;

	public: 

		unsigned short *shortBuffer; /*!<a short buffer for registers*/
		int handle; /*!<a device handle returned by the initialization function*/

		/*! the specialty constructor */
		controller(int a, int id, log4cpp::Appender* appender) { 
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
			ctrlAppender    = appender; 
			controllerLog.setPriority(log4cpp::Priority::DEBUG);
		};
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
			ctrlAppender = new log4cpp::FileAppender("default", "/work/data/logs/config.txt");
			ctrlAppender->setLayout(new log4cpp::BasicLayout());
			log4cpp::Category::getRoot().addAppender(ctrlAppender);
			log4cpp::Category::getRoot().setPriority(log4cpp::Priority::DEBUG);
			controllerLog.setPriority(log4cpp::Priority::DEBUG);
		};

		/*! the specialty destructor */
		~controller() {
			for (std::vector<crim*>::iterator p=interfaceModule.begin();
				p!=interfaceModule.end();p++) delete (*p);
			interfaceModule.clear();
			for (std::vector<croc*>::iterator p=readOutController.begin();
				p!=readOutController.end();p++) delete (*p);
			readOutController.clear();
			for (std::vector<channels*>::iterator p=feChannels.begin();
				p!=feChannels.end();p++) delete (*p);
			feChannels.clear();
		};

		/*! Get functions */
		int inline GetAddress() {return address;};
		CVAddressModifier inline GetAddressModifier() {return addressModifier;};
		CVDataWidth inline GetDataWidth() {return dataWidth;};
		CVBoardTypes inline GetControllerType() {return controllerType;};
		CVBoardTypes inline GetBridgeType() {return bridgeType;};
		int inline GetHandle() {return handle;};
		int inline GetID() {return controller_id;};

		/*! Object assignment functions */
		void MakeCrim(unsigned int a);        //make *one* interface module, w/id==1
		void MakeCrim(unsigned int a, int b); //make up each interface module
		void MakeCroc(unsigned int a, int b); //make up each croc

		// By convention (& hopefully construction), the first CRIM (indexed to 1) 
		// will always be the MASTER CRIM (the interrupt handler we poll or IACK).
		crim *GetCrim();       // Return the pointer to the *first* CRIM.
		crim *GetCrim(int a);  // Return the pointer to the requested CRIM.
		croc *GetCroc(int a);  // Return the pointer to the requested CROC.
		std::vector<croc*> inline *GetCrocVector() {return &readOutController;};
		std::vector<crim*> inline *GetCrimVector() {return &interfaceModule;};

		void inline SetDataWidth(CVDataWidth a) {dataWidth=a;}; 

		/*! wrapper functions for contacting the controller & getting information back */
		int ContactController();
		int GetCardStatus();      //get card status for the *first* crim in the list
		int GetCardStatus(int a); //get card status for the requested croc in the list
		int GetCrimStatus(int a); //get card status for the requested crim in the list
		int GetCrocStatus(int a); //get card status for the requested croc in the list
		int inline GetCrocVectorLength() {return crocVectorLength;};
		void SetCrocVectorLength() {crocVectorLength = readOutController.size();};
		int inline GetCrimVectorLength() {return crimVectorLength;};
		void SetCrimVectorLength() {crimVectorLength = interfaceModule.size();};
		int inline GetFEChannelsVectorLength() {return feChannelsVectorLength;};
		void SetFEChannelsVectorLength() {feChannelsVectorLength = interfaceModule.size();};
		
		void ReportError(int error);


};
#endif
