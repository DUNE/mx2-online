#ifndef Controller_cpp
#define Controller_cpp

#include "Controller.h"

/*********************************************************************************
 * Class for creating CAEN VME V2718 Controller objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Gabriel Perdue, The University of Rochester
 **********************************************************************************/

log4cpp::Category& ctrlLog = log4cpp::Category::getInstance(std::string("ctrl"));

Controller::Controller(int addr, int id, log4cpp::Appender* appender) {
  address         = addr;
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
  ctrlLog.setPriority(log4cpp::Priority::DEBUG);
}

unsigned int Controller::GetAddress() 
{
  return address;
}

CVAddressModifier Controller::GetAddressModifier() 
{
  return addressModifier;
}

CVDataWidth Controller::GetDataWidth() 
{
  return dataWidth;
}

CVBoardTypes Controller::GetControllerType() 
{
  return controllerType;
}

CVBoardTypes Controller::GetBridgeType() 
{
  return bridgeType;
}

int Controller::GetHandle() 
{
  return handle;
}

int Controller::GetID() 
{
  return controller_id;
}


void Controller::ReportError(int error)
{
  switch(error) {
    case cvSuccess:
      ctrlLog.critStream() << "VME Error: Success!?";  
      break;					
    case cvBusError: 
      ctrlLog.critStream() << "VME Error: Bus Error!";  
      break;	
    case cvCommError: 
      ctrlLog.critStream() << "VME Error: Comm Error!";  
      break;	
    case cvGenericError: 
      ctrlLog.critStream() << "VME Error: Generic Error!";  
      break;	
    case cvInvalidParam: 
      ctrlLog.critStream() << "VME Error: Invalid Parameter!";  
      break;	
    case cvTimeoutError: 
      ctrlLog.critStream() << "VME Error: Timeout Error!";  
      break;	
    default:
      ctrlLog.critStream() << "VME Error: Unknown Error!";  
      break;			
  }
}


int Controller::ContactController() 
{
  /*! \fn
   *
   * This function will try to contact the CAEN v2718 Controller via the internally 
   * mounted a2818 pci card & read the status register of the Controller.
   */
  int error; // The error returned by the CAEN libraries.

  // Initialize the Controller.
  try {
    error = CAENVME_Init(controllerType, (unsigned short) boardNumber,
        (unsigned short) pciSlotNumber, &handle); 
    if (error) throw error;
  } catch (int e) {
    ReportError(e);
    ctrlLog.critStream() << "Unable to contact the v2718 VME controller!";
    ctrlLog.critStream() << "Are you sure the a2818 module is loaded?  Check /proc/a2818.";
    ctrlLog.critStream() << "If there is no entry for /proc/a2818, execute the following: ";
    ctrlLog.critStream() << "  cd /work/software/CAENVMElib/driver/v2718";
    ctrlLog.critStream() << "  sudo sh a2818_load.2.6";
    return e;
  } 
  ctrlLog.infoStream() << "Controller " << controller_id << " is initialized.";

  // Get the firmware version of the controller card.
  try {
    error = CAENVME_BoardFWRelease(handle, firmware); 
    if (error) throw error;
  } catch (int e) {
    ReportError(e);
    ctrlLog.critStream() << "Unable to obtain the controller firmware version!";
    return e;
  }
  ctrlLog.infoStream() << "The controller firmware version is: " << firmware; 

  // Get the status of the controller.
  CVRegisters registerAddress = cvStatusReg; 
  try {
    shortBuffer = new unsigned short;
    error = CAENVME_ReadRegister(handle, registerAddress, shortBuffer); //check controller status
    if (error) throw error;
  } catch (int e) {
    ReportError(e);
    ctrlLog.critStream() << "Unable to read the status register!";
    delete shortBuffer;
    return e;
  } 

  // Clean up memory.
  delete shortBuffer;

  return 0;
} 





#endif
