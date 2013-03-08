#ifndef VMECrate_h
#define VMECrate_h

#include "log4cppHeaders.h"

#include "VMEModuleTypes.h"
#include "Controller.h" 
#include "ECROC.h"
#include "CRIM.h"

#include "ReadoutTypes.h"

class VMECrate {

	friend std::ostream& operator<<(std::ostream&, const VMECrate&);

	private:
		Controller *controller;
    std::vector<ECROC*> ecrocs;
    std::vector<CRIM*>  crims;

    int crateID;  // == crate ID/Address for Controller
		bool vmeInit;    
    RunningModes runningMode;

	public:
		explicit VMECrate( int theCrateID, log4cpp::Priority::Value priority, bool VMEInit=false );
		~VMECrate();

    void AddECROC( unsigned int address, int nFEBchan0=11, int nFEBchan1=11, int nFEBchan2=11, int nFEBchan3=11 );
    void AddCRIM( unsigned int address );
    void Initialize( RunningModes runningMode );

		void SendSoftwareRDFE() const;
		void WaitForSequencerReadoutCompletion() const;
		void EnableSequencerReadout() const; 
		void DisableSequencerReadout() const;  
    void ClearAndResetStatusRegisters() const;
    void OpenGateFastCommand() const;

    std::vector<ECROC*>* GetECROCVector();
    ECROC* GetECROCVector( int index );

    std::vector<CRIM*>* GetCRIMVector();
    CRIM* GetCRIMVector( int index );

};
#endif
