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

/*********************************************************************************
 * Class for creating CAEN VME V2718 Controller objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * April 22, 2009
 *
 **********************************************************************************/

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

    std::vector<crim*> interfaceModule; /*!< a vector of CROC interface module objects */
    std::vector<croc*> readOutController;  /*!< a vector of CROC objects */
    /*! these are the controller registers for the VME controller */
    unsigned short status, control, irq, irqMask, input, output,
      clearOutput, inputMux, inputMuxClear, outPutMux;
    char firmware[1];
    int transferBytes, crocVectorLength, crimVectorLength, controller_id;
    std::ofstream &log_file; /*!<a log file fo debugging output */

  public: 
    unsigned short *shortBuffer; /*!<a short buffer for registers*/
    int handle; /*!<a device handle returned by the initialization function*/

    /*! the specialty constructor */
    controller(int a, int id, std::ofstream &lf):log_file(lf) { 
      // really we should pass the boardNumber; address is not much used
      address = a;
      addressModifier = cvA24_U_DATA; //default address modifier
      dataWidth = cvD16; //default data width
      controllerType = cvV2718;  //this is the only controller board we have
      bridgeType = cvA2818;  //this is the only PCI card we have
      slotNumber=0; //by construction 
      pciSlotNumber=0; //don't really know at the moment, will have to check & fix (link)
      boardNumber = 0;
      handle = -1;
      firmware[0]=0;
      controller_id = id; //an internal ID used for sorting data 

    };

    /*! the specialty destructor */
    ~controller() {
       for (std::vector<crim*>::iterator p=interfaceModule.begin();
            p!=interfaceModule.end();p++) delete (*p);
       interfaceModule.clear();
       for (std::vector<croc*>::iterator p=readOutController.begin();
            p!=readOutController.end();p++) delete (*p);
       readOutController.clear();
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

    crim *GetCrim();       //return the pointer to the *first* crim
    crim *GetCrim(int a);  //return the pointer to the requested crim
    croc *GetCroc(int a);  //return the pointer to the requested croc

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
};
#endif
