#ifndef controller_cpp
#define controller_cpp

#include "controller.h"

/*********************************************************************************
* Class for creating CAEN VME V2718 Controller objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
**********************************************************************************/

void controller::ReportError(int error)
{
	switch(error) {
		case cvSuccess:
			controllerLog.critStream() << "VME Error: Success!?";  
			std::cout                  << "VME Error: Success!?" << std::endl;  
			break;					
		case cvBusError: 
			controllerLog.critStream() << "VME Error: Bus Error!";  
			std::cout                  << "VME Error: Bus Error!" << std::endl; 
			break;	
		case cvCommError: 
			controllerLog.critStream() << "VME Error: Comm Error!";  
			std::cout                  << "VME Error: Comm Error!" << std::endl; 
			break;	
		case cvGenericError: 
			controllerLog.critStream() << "VME Error: Generic Error!";  
			std::cout                  << "VME Error: Generic Error!" << std::endl; 
			break;	
		case cvInvalidParam: 
			controllerLog.critStream() << "VME Error: Invalid Parameter!";  
			std::cout                  << "VME Error: Invalid Parameter!" << std::endl; 
			break;	
		case cvTimeoutError: 
			controllerLog.critStream() << "VME Error: Timeout Error!";  
			std::cout                  << "VME Error: Timeout Error!" << std::endl; 
			break;	
		default:
			controllerLog.critStream() << "VME Error: Unknown Error!";  
			std::cout                  << "VME Error: Unknown Error!" << std::endl; 
			break;			
	}
}


int controller::ContactController() 
{
/*! \fn
 *
 * This function will try to contact the CAEN v2718 controller via the internally 
 * mounted a2818 pci card & read the status register of the controller.
 */
	int error; // The error returned by the CAEN libraries.

	// Initialize the controller.
	try {
		error = CAENVME_Init(controllerType, (unsigned short) boardNumber,
			(unsigned short) pciSlotNumber, &handle); 
		if (error) throw error;
	} catch (int e) {
		ReportError(e);
		std::cout << "Unable to contact the v2718 VME controller!" << std::endl; 
		std::cout << "Are you sure the a2818 module is loaded?  Check /proc/a2818." << std::endl;
		std::cout << "If there is no entry for /proc/a2818, execute the following: " << std::endl;
		std::cout << "  cd /work/software/CAENVMElib/driver/v2718" << std::endl;
		std::cout << "  sudo sh a2818_load.2.6" << std::endl;
		controllerLog.critStream() << "Unable to contact the v2718 VME controller!";
		controllerLog.critStream() << "Are you sure the a2818 module is loaded?  Check /proc/a2818.";
		controllerLog.critStream() << "If there is no entry for /proc/a2818, execute the following: ";
		controllerLog.critStream() << "  cd /work/software/CAENVMElib/driver/v2718";
		controllerLog.critStream() << "  sudo sh a2818_load.2.6";
		return e;
	} 
	std::cout << "Controller " << controller_id << " is initialized." << std::endl; 
	controllerLog.infoStream() << "Controller " << controller_id << " is initialized.";

	// Get the firmware version of the controller card.
	try {
		error = CAENVME_BoardFWRelease(handle, firmware); 
		if (error) throw error;
	} catch (int e) {
		ReportError(e);
		std::cout << "Unable to obtain the controller firmware version!" << std::endl;
		controllerLog.critStream() << "Unable to obtain the controller firmware version!";
		return e;
	}
	std::cout << "The controller firmware version is: " << firmware << std::endl; 
	controllerLog.infoStream() << "The controller firmware version is: " << firmware; 

	// Get the status of the controller.
	CVRegisters registerAddress = cvStatusReg; 
	try {
		shortBuffer = new unsigned short;
		error = CAENVME_ReadRegister(handle, registerAddress, shortBuffer); //check controller status
		if (error) throw error;
	} catch (int e) {
		ReportError(e);
		std::cout << "Unable to read the status register!" << std::endl;
		controllerLog.critStream() << "Unable to read the status register!";
		delete shortBuffer;
		return e;
	} 

	// Clean up memory.
	delete shortBuffer;

	return 0;
} 


int controller::GetCardStatus() 
{
/*! \fn
 * CRIM version, assuming a 1-crim set-up -> i.e., only access *first* element in the card vector. 
 * This function returns the status of the crim associated with the current controller object.  This 
 * is basically a LEGACY function.  Do not use it except to access the "master" CRIM! 
 */
	if (interfaceModule.size() < 1) { return 1; } // No crims!
	long_m registerAddress = interfaceModule[0]->GetStatusRegisterAddress(); 
	int error; //error returned by the CAEN libraries
	shortBuffer = new unsigned short; //hold the crim status in a short
	try {
		error = CAENVME_ReadCycle(handle,registerAddress,shortBuffer,
			interfaceModule[0]->GetAddressModifier(),
			interfaceModule[0]->GetDataWidth()); 
		if (error) throw error;
	} catch (int e) {
		std::cout << "Error in controller()::GetCardStatus()!" << std::endl;
		controllerLog.critStream() << "Error in controller()::GetCardStatus()!";
		ReportError(e);
		delete shortBuffer; //clean up 
		return e;
	}
	delete shortBuffer; //clean up 
	return 0;
} 


int controller::GetCrimStatus(int a) 
{
/*! \fn
 * The vector CRIM version: this function returns the status of the selected crim (a) associated 
 * with the current controller object from its vector of crim's. 
 * \param a the CRIM index number ((internal to DAQ code, not a physical quanitiy)
 */
	bool foundModule = false;
	//loop over all the crims associated with this controller object
	for (std::vector<crim*>::iterator p=interfaceModule.begin(); p!=interfaceModule.end(); p++) { 
		//select the crim requested
		if ((*p)->GetCrimID()==a) { 
			foundModule = true;
			long_m registerAddress = (*p)->GetStatusRegisterAddress(); 
			int error; //error from the CAEN libraries
			shortBuffer = new unsigned short; //a short to hold the status message
			try {
				error = CAENVME_ReadCycle(handle, registerAddress, shortBuffer,
					(*p)->GetAddressModifier(),
					(*p)->GetDataWidth()); 
				if (error)  throw error;
			} catch (int e) {
				std::cout << "Error in controller()::GetCrimStatus() for Addr " << 
					((*p)->GetCrimAddress()>>16) << std::endl;
				controllerLog.critStream() << "Error in controller()::GetCrimStatus() for Addr " << 
					((*p)->GetCrimAddress()>>16);
				ReportError(e);
				foundModule = false;
				delete shortBuffer; //clean up 
				continue;
			} 
			delete shortBuffer; //clean up 
		} 
	}
	if (!foundModule) { return 1; }
	return 0;
} 


int controller::GetCardStatus(int a) 
{
/*! \fn
 * This function returns the status of the selected croc (a) associated with the current
 * controller object from its vector of croc's - it is redundant but included for backwards 
 * compatibility.  It is a LEGACY function and should not be called anymore.
 * \param a the CROC index number (internal to DAQ code, not a physical quanitiy)
 */ 
	return controller::GetCrocStatus(a);
}


int controller::GetCrocStatus(int a) 
{
/*! \fn
 * The croc version: this function returns the status of the selected croc (a) associated with the 
 * current controller object from its vector of croc's.  It does so by reading the status register 
 * of each front end channel.  If they are all okay, the croc is okay!  
 * \param a the CROC index number (internal to DAQ code, not a physical quanitiy)
 */
	bool foundModule = false;
	//loop over all the crocs associated with this controller object
	for (std::vector<croc*>::iterator p=readOutController.begin(); p!=readOutController.end();p++) { 
		//select the croc requested
		if ((*p)->GetCrocID()==a) { 
			foundModule = true;
			//we have 4 channels per croc; loop over all channels
			for (int i=0;i<4;i++) { 
				unsigned int location = (*p)->GetChannel(i)->GetStatusAddress(); 
				int error; //error from the CAEN libraries
				shortBuffer = new unsigned short; //a short to hold the status message
				try {
					error = CAENVME_ReadCycle(handle,location,shortBuffer,addressModifier,dataWidth); 
					if (error)  throw error;
					//the channel is available, take care of keeping track of that
					(*p)->SetChannelAvailable(i); //load that this channel is available for later polling
					(*p)->GetChannel(i)->SetChannelStatus((*shortBuffer)); 
				} catch (int e) {
					std::cout << "Error in controller()::GetCrocStatus() for Addr " << 
						((*p)->GetCrocAddress()>>16) << " Channel " << (i+1)  << std::endl;
					controllerLog.critStream() << "Error in controller()::GetCrocStatus() for Addr " << 
						((*p)->GetCrocAddress()>>16) << " Channel " << (i+1);
					ReportError(e);
					foundModule = false;
					delete shortBuffer; //clean up 
					continue;
				} 
				delete shortBuffer; //clean up 
			}  
		}
	}
	if (!foundModule) { return 1; }
	return 0;
} 


void controller::MakeCrim(unsigned int crimAddress, int id) 
{
/*! \fn
 * This function instantiates a crim software object belonging to the current controller object.
 * \param crimAddress the physical VME address of the crim.
 * \param id an index for use in DAQ code, internal.
 */
	crim *tmp = new crim(crimAddress, id, addressModifier, dataWidth);
	interfaceModule.push_back(tmp);
	controllerLog.infoStream() << "Added a CRIM with id=" << id << " and Address=" << (crimAddress>>16);
}


void controller::MakeCrim(unsigned int crimAddress) 
{
/*! \fn
 * This function instantiates a crim object belonging to the current controller object - it is 
 * LEGACY code and should not be called.  A crim with id==1 is created. 
 * \param crimAddress the physical VME address of the crim
 */
	crim *tmp = new crim(crimAddress, (int)1, addressModifier, dataWidth);
	interfaceModule.push_back(tmp);
	controllerLog.infoStream() << "Added a CRIM with id=1 and Address=" << (crimAddress>>16);
}


void controller::MakeCroc(unsigned int crocAddress, int a) 
{
/*! \fn
 * This function instantiates a croc object with index (a) belonging to the current controller object.
 *  \param crocAddress the physical VME address of the CROC
 *  \param a an internal index for the CROC for use in DAQ code only
 */
	croc *tmp = new croc(crocAddress, a, addressModifier, dataWidth, cvD16_swapped);
	readOutController.push_back(tmp); 
	controllerLog.infoStream() << "Added a CROC with id=" << a << " and Address=" << 
		(crocAddress>>16);
}


croc *controller::GetCroc(int a) 
{
/*! \fn
 * This function returns a croc specified by INDEX from the vector of croc's belonging to this 
 * controller object. 
 * \param a an internal index for the CROC for use in DAQ code only
 */
	std::vector<croc*>::iterator p; //an iterator over the vector of croc's
	croc *tmp = 0; //a temporary croc object (we need to return one no matter what)
	//loop over all croc objects in the vector
	for (p=readOutController.begin();p!=readOutController.end();p++) { 
		int id=(*p)->GetCrocID(); //extract & check the croc's id number
		if (id==a) tmp=(*p); //assign that croc fro return by the function
	}
	return tmp; //return the pointer to the croc extracted from the vector
	// TODO - Add error handling if we don't find the croc.
}


crim *controller::GetCrim() 
{
/*! \fn 
 * Returns a pointer to the *first* CRIM object.  This is by convention & construction 
 * the master CRIM for a given crate and is our designated interrupt handler. 
 */
	crim *tmp = 0; // temp object, have to return something...
	if (interfaceModule.size() > 0) { 
		tmp = interfaceModule[0]; 
	} else {
		controllerLog.critStream() << "Error in controller::GetCrim()!";
		std::cout << "Error in controller::GetCrim()!" << std::endl;
		std::cout << "CRIM interfaceModule vector has size zero!" << std::endl;
		exit (-1);
	}  
	return tmp;
}


crim *controller::GetCrim(int a) 
{
/*! \fn
 * This function returns a crim specified by INDEX from the vector of crim's belonging to this 
 * controller object. 
 * \param a the internal CRIM index
 */
	std::vector<crim*>::iterator p; //an iterator over the vector of crim's
	crim *tmp = 0; //a temporary crim object (we need to return one no matter what)
	//loop over all crim objects in the vector
	for (p=interfaceModule.begin();p!=interfaceModule.end();p++) { 
		int id=(*p)->GetCrimID(); //extract & check the crim's id number
		if (id==a) tmp=(*p); //assign that crim for return by the function
	}
	return tmp; //return the pointer to the crim extracted from the vector
	// TODO - Add error handling in case we don't find the CRIM.
}

#endif
