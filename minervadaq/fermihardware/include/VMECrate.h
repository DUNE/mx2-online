#ifndef VMECrate_h
#define VMECrate_h
/*! \file VMECrate.h 
*/

#include "log4cppHeaders.h"

#include "VMEModuleTypes.h"
#include "Controller.h" 
#include "ECROC.h"
#include "CRIM.h"

#include "ReadoutTypes.h"

/*! 
  \class VMECrate
  \brief Container for ECROC and CRIM vectors.
  \author Gabriel Perdue
  */

class VMECrate {

  friend std::ostream& operator<<(std::ostream&, const VMECrate&);

  private:
  Controller *controller;
  std::vector<ECROC*> ecrocs;
  std::vector<CRIM*>  crims;

  int crateID;  /*!< == crate ID/Address for Controller */
  bool vmeInit;    
  Modes::RunningModes runningMode;

  public:
  explicit VMECrate( int theCrateID, 
      log4cpp::Priority::Value priority, bool VMEInit=false );
  ~VMECrate();

  void AddECROC( unsigned int address, 
      int nFEBchan0=11, int nFEBchan1=11, int nFEBchan2=11, int nFEBchan3=11 );
  void AddCRIM( unsigned int address );
  void Initialize( Modes::RunningModes runningMode );
  int GetCrateID() { return(crateID);}

  // ECROC methods
  void SendSoftwareRDFE() const;
  void WaitForSequencerReadoutCompletion() const;
  void ResetEventCounter() const; 
  void EnableSequencerReadout() const; 
  void DisableSequencerReadout() const;  
  void ConfigureForStandardDataTaking() const;
  void UseSinglePipelineReadout() const;
  void ClearAndResetStatusRegisters() const;
  void OpenGateFastCommand() const;
  void SequencerDelayDisable() const;
  void SequencerDelayEnable() const;
  void SetSequencerDelayValue( unsigned short delay ) const; // 9 lowest bits

  std::vector<ECROC*>* GetECROCVector();
  ECROC* GetECROCVector( int index );

  // CRIM methods
  void SendSoftwareGate() const;
  void ResetSequencerLatch() const;

  std::vector<CRIM*>* GetCRIMVector();
  CRIM* GetCRIMVector( int index );

/*
12/10/2014 Geoff Savage
Additions for running in "cosmics" mode.
FastCommandFEBTriggerRearm()
*/
    void FastCommandFEBTriggerRearm() const;
}; /* end class VMECrate */

#endif
