#ifndef controller_cpp
#define controller_cpp

#include "controller.h"

/*********************************************************************************
 * Class for creating CAEN VME V2718 Controller objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * April 22, 2009
 *
 **********************************************************************************/

int controller::ContactController() {
  /*! \fn
 *
 * OK, here we go.  We're going to try to contact the
 *   v2718 controller via the pci card & get the status
 *   of the controller 
 */

 int error; //the error returned by the CAEN libraries

  try {
    error = CAENVME_Init(controllerType,(unsigned short) boardNumber,
                         (unsigned short) pciSlotNumber, &handle); //initialize the controller
    if (error) throw error;
  } catch (int e) {
    log_file<<"Unable to contact the v2718 VME controller"<<std::endl; 
    log_file<<"The error code was: "<<e<<std::endl;
    return e;
  } 
  log_file<<"The controller is now initialized."<<std::endl; 

  /* now get the firmware version */
  try {
   error = CAENVME_BoardFWRelease(handle, firmware); //report the firmware version for the controller
   if (error) throw error;
  } catch (int e) {
   log_file<<"Unable to obtain the firmware version"<<std::endl;
   log_file<<"The error code was: "<<e<<std::endl;
   return e;
  }
  log_file<<"The controller firmware version is: "<<firmware<<std::endl; 

  /* now tell me the status of the controller */
  CVRegisters registerAddress = cvStatusReg; //the address of the status register
  try {
    shortBuffer = new unsigned short;
    error = CAENVME_ReadRegister(handle, registerAddress, shortBuffer); //check controller status
    if (error) throw error;
  } catch (int e) {
    log_file<<"Unable to obtain status register: "<<std::endl;
    log_file<<"The error code was: "<<e<<std::endl;
    delete shortBuffer;
    return e;
  } 
  /* return the value of the controller status */

  delete shortBuffer;
  return 0;
} 


int controller::GetCardStatus() {
  /*! \fn
 * crim version, assuming a 1-crim set-up -> i.e., only access *first* element in crim vector 
 * this function returns the status of the crim associated with the current
 * controller object. 
 * */
  if (interfaceModule.size() < 1) { return 1; } // No crims!
  long_m registerAddress = interfaceModule[0]->GetStatusRegisterAddress(); //the status address for
                   //this controller object's crim (timing module)
  int error; //error returned by the CAEN libraries
  shortBuffer = new unsigned short; //hold the crim status in a short
  try {
    error = CAENVME_ReadCycle(handle,registerAddress,shortBuffer,interfaceModule[0]->GetAddressModifier(),
      interfaceModule[0]->GetDataWidth()); //read off the status of the crim
    if (error) throw error;
  } catch (int e) {
    log_file<<"Unable to obtain status register: "<<std::endl;
    log_file<<"The error code was: "<<e<<std::endl;
    delete shortBuffer; //clean up 
    return e;
  }
  delete shortBuffer; //clean up 
  return 0;
} 


int controller::GetCrimStatus(int a) {
  /*! \fn
 * the vector crim version 
 * this function returns the status of the selected crim (a) associated with the current
 * controller object from its vector of crim's. 
 * \param a the CRIM index number ((internal to DAQ code, not a physical quanitiy)
 */
  bool foundModule = false;
  for (std::vector<crim*>::iterator p=interfaceModule.begin(); 
     p!=interfaceModule.end();p++) { //loop over all the crims associated with this controller object
    if ((*p)->GetCrimID()==a) { //select the crim requested
      foundModule = true;
	  long_m registerAddress = (*p)->GetStatusRegisterAddress(); //the status address for
	                   //this controller object's crim (timing module)
      int error; //error from the CAEN libraries
      shortBuffer = new unsigned short; //a short to hold the status message
      try {
        error = CAENVME_ReadCycle(handle,registerAddress,shortBuffer,(*p)->GetAddressModifier(),
          (*p)->GetDataWidth()); //read off the status of the crim
        if (error)  throw error;
      } catch (int e) {
        log_file<<"Unable to obtain status register: "<<std::endl;
        log_file<<"The errror code was: "<<e<<std::endl;
        delete shortBuffer; //clean up 
        continue;
      } 
      delete shortBuffer; //clean up 
    } 
  }
  if (!foundModule) { return 1; }
  return 0;
} 


int controller::GetCardStatus(int a) {
  /*! \fn
 * This function returns the status of the selected croc (a) associated with the current
 * controller object from its vector of croc's - it is redundant but included for backwards 
 * compatibility. 
 * \param a the CROC index number (internal to DAQ code, not a physical quanitiy)
 */ 
	return controller::GetCrocStatus(a);
}


int controller::GetCrocStatus(int a) {
  /*! \fn
 * the croc version 
 * this function returns the status of the selected croc (a) associated with the current
 * controller object from its vector of croc's. 
 * \param a the CROC index number (internal to DAQ code, not a physical quanitiy)
 */
  bool foundModule = false;
  for (std::vector<croc*>::iterator p=readOutController.begin(); 
     p!=readOutController.end();p++) { //loop over all the crocs associated with this controller object
    if ((*p)->GetCrocID()==a) { //select the croc requested
      foundModule = true;
      for (int i=0;i<4;i++) { //we only have 4 channels per croc; loop over all channels
        unsigned int location = (*p)->GetChannel(i)->GetStatusAddress(); //get this croc's status register address
        int error; //error from the CAEN libraries
        shortBuffer = new unsigned short; //a short to hold the status message
        try {
          error = CAENVME_ReadCycle(handle,location,shortBuffer,addressModifier,dataWidth); //read off the status message
          if (error)  throw error;
          //the channel is available, take care of keeping track of that
          (*p)->SetChannelAvailable(i); //load that this channel is available for later polling
          (*p)->GetChannel(i)->SetChannelStatus((*shortBuffer)); //make note of the channel's status
        } catch (int e) {
          log_file<<"Unable to obtain status register: "<<std::endl;
          log_file<<"The errror code was: "<<e<<std::endl;
          delete shortBuffer; //clean up 
          continue;
        } 
        delete shortBuffer; //clean up 
      }
      unsigned int location = (*p)->GetTimingAddress(); //get this croc's status register address
      int error; //error from the CAEN libraries
      //shortBuffer = new unsigned short; //a short to hold the status message
      unsigned short timing_setup = ((*p)->GetTimingRegister()); 
      try {
        error = CAENVME_WriteCycle(handle,location,&timing_setup,addressModifier,dataWidth); //read off the status message
        if (error)  throw error;
        //the channel is available, take care of keeping track of that
      } catch (int e) {
        log_file<<"Unable to obtain timing register: "<<std::endl;
        log_file<<"The errror code was: "<<e<<std::endl;
        delete shortBuffer; //clean up 
        continue;
      }  
    }
  }
  if (!foundModule) { return 1; }
  return 0;
} 


void controller::MakeCrim(unsigned int crimAddress, int id) {
    /*! \fn
 *
 * a function to make a crim object which belongs to the current controller object 
 * \param crimAddress the physical VME address of the crim
 * \param id an index for use in DAQ code, internal
 */
    crim *tmp = new crim(crimAddress,id,addressModifier,dataWidth);
    interfaceModule.push_back(tmp);
}


void controller::MakeCrim(unsigned int crimAddress) {
    /*! \fn
 * a function to make a crim object which belongs to the current controller object 
 * \param crimAddress the physical VME address of the crim
 *    - If we do not supply an id, a crim with id==1 is created.
 */

    crim *tmp = new crim(crimAddress,(int)1,addressModifier,dataWidth);
    interfaceModule.push_back(tmp);
}


void controller::MakeCroc(unsigned int crocAddress, int a) {
  /*! \fn
 *
 * a function to make a croc object numbered (a) which belongs to the current 
 *  controller object 
 *  \param crocAddress the physical VME address of the CROC
 *  \param a an internal index for the CROC for use in DAQ code only
 */
  croc *tmp = new croc(crocAddress, a, addressModifier,dataWidth, cvD16_swapped);
  readOutController.push_back(tmp); //add this croc to a vector of croc objects belonging to thics 
                                    //controller object
}


croc *controller::GetCroc(int a) {
  /*! \fn
 * a function to return a specified croc from the vector of croc's belonging to this
 * controller object 
 * \param a an internal index for the CROC for use in DAQ code only
 */
  std::vector<croc*>::iterator p; //an iterator over the vector of croc's
  croc *tmp = 0; //a temporary croc object (we need to return one no matter what)
  for (p=readOutController.begin();p!=readOutController.end();p++) { //loop over all croc objects in the vector
    int id=(*p)->GetCrocID(); //extract & check the croc's id number
    if (id==a) tmp=(*p); //assign that croc fro return by the function
  }
  return tmp; //return the pointer to the croc extracted from the vector
}


crim *controller::GetCrim() {
  /*! \fn 
 *  Returns a pointer to a CRIM object, if only one CRIM is in a crate
 *
 */
	crim *tmp = 0; // temp object, have to return something...
	if (interfaceModule.size() > 0) { tmp = interfaceModule[0]; }
	return tmp;
}


crim *controller::GetCrim(int a) {
  /*! \fn
 * a function to return a specified crim from the vector of crim's belonging to this
   * controller object 
   * \param a the internal CRIM index
   */
  std::vector<crim*>::iterator p; //an iterator over the vector of crim's
  crim *tmp = 0; //a temporary crim object (we need to return one no matter what)
  for (p=interfaceModule.begin();p!=interfaceModule.end();p++) { //loop over all crim objects in the vector
    int id=(*p)->GetCrimID(); //extract & check the crim's id number
    if (id==a) tmp=(*p); //assign that crim for return by the function
  }
  return tmp; //return the pointer to the crim extracted from the vector
}

#endif
