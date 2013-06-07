#ifndef Controller_cpp
#define Controller_cpp
/*! \file Controller.cpp
*/

#include "Controller.h"

log4cpp::Category& ctrlLog = log4cpp::Category::getInstance(std::string("ctrl"));

//-------------------------------
/*! 
  \param addr     We set an address on the module.
  \param crateNum This should be the order of the controller in a chain (if there is >1).
  */
Controller::Controller(int addr, int crateNum) {
  address         = addr;
  addressModifier = cvA24_U_DATA; // default address modifier
  dataWidth       = cvD16;    // default data width
  controllerType  = cvV2718;  // this is the only controller board we have
  bridgeType      = cvA2818;  // this is the only PCI card we have
  slotNumber      = 0; // by construction ????
  pciSlotNumber   = 0; // link - probably always 0. Changes if we add more PCI cards.
  crateNumber     = crateNum;   // TODO: cleanup
  boardNumber     = crateNumber; 
  handle          = -1;
  firmware[0]     = 0;
  ctrlLog.setPriority(log4cpp::Priority::DEBUG);
}

//-------------------------------
//! Release the Controller when finished so other hardware can access it.
Controller::~Controller()
{
  int error = CAENVME_End(handle);
  if (error) ReportError(error);
}

//-------------------------------
unsigned int Controller::GetAddress() const
{
  return address;
}

//-------------------------------
CVAddressModifier Controller::GetAddressModifier() const
{
  return addressModifier;
}

//-------------------------------
CVDataWidth Controller::GetDataWidth() const
{
  return dataWidth;
}

//-------------------------------
CVBoardTypes Controller::GetControllerType() const
{
  return controllerType;
}

//-------------------------------
CVBoardTypes Controller::GetBridgeType() const
{
  return bridgeType;
}

//-------------------------------
int Controller::GetHandle() const
{
  return handle;
}

//-------------------------------
int Controller::GetCrateNumber() const
{
  return crateNumber;
}


//-------------------------------
std::string Controller::ReportError(int error) const
{
  std::string retval;
  switch(error) {
    case cvSuccess:
      retval = "VME Error: Success!?";  
      break;					
    case cvBusError: 
      retval = "VME Error: Bus Error!";  
      break;	
    case cvCommError: 
      retval = "VME Error: Comm Error!";  
      break;	
    case cvGenericError: 
      retval = "VME Error: Generic Error!";  
      break;	
    case cvInvalidParam: 
      retval = "VME Error: Invalid Parameter!";  
      break;	
    case cvTimeoutError: 
      retval = "VME Error: Timeout Error!";  
      break;	
    default:
      retval = "VME Error: Unknown Error!";  
      break;			
  }
  ctrlLog.critStream() << retval;
  return retval;
}

//-------------------------------
/*!
  This function will try to contact the CAEN v2718 Controller via the internally 
  mounted a2818 pci card & read the status register of the Controller.
  */
int Controller::Initialize() 
{
  int error;
  unsigned int registerBuffer;

  try {
    error = CAENVME_Init(controllerType, (unsigned short)boardNumber,
        (unsigned short)pciSlotNumber, &handle); 
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
  ctrlLog.infoStream() << "Controller " << crateNumber << " is initialized.";

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
    error = CAENVME_ReadRegister(handle, registerAddress, &registerBuffer); //check controller status
    if (error) throw error;
  } catch (int e) {
    ReportError(e);
    ctrlLog.critStream() << "Unable to read the status register!";
    return e;
  } 

  return 0;
} 





#endif
