#ifndef ECROC_h
#define ECROC_h
/*! \file ECROC.h
*/

#include <list>
#include <fstream>
#include "CAENVMEtypes.h"
#include "EChannels.h"
#include "VMEModuleTypes.h"
#include "ReadoutTypes.h"

/*! 
  \class ECROC
  \brief The class which controls data for CROC-Es. 
  \author Gabriel Perdue
  */

class ECROC : public VMECommunicator {

  private:
    std::vector<EChannels*> ECROCChannels; 

    unsigned int timingSetupAddress;
    unsigned int resetAndTestPulseMaskAddress;
    unsigned int channelResetAddress;
    unsigned int fastCommandAddress;
    unsigned int testPulseAddress;
    unsigned int rdfePulseDelayAddress;
    unsigned int rdfePulseCommandAddress;

    unsigned short channelResetRegisterMessage;
    unsigned short testPulseRegisterMessage;

    void MakeChannels(); 

    static const unsigned short RDFEDelayRegisterDelayMask;
    static const unsigned short RDFEDelayRegisterEnableMask;
    static const unsigned short RDFEDelayRegisterEnableBit;

    void SetSequencerDelayeRegister( unsigned short registerConfig ) const;
    void SequencerDelayEnableDisable( unsigned short bit ) const;

  public:
    explicit ECROC( unsigned int address, const Controller* controller); 
    ~ECROC(); 

    void Initialize(Modes::RunningModes runningMode) const;
    virtual unsigned int GetAddress() const; 
    unsigned int GetCROCNumber() const;

    EChannels *GetChannel( unsigned int i ); 
    std::vector<EChannels*>* GetChannelsVector(); 
    void ClearEmptyChannels();

    void SetupTimingRegister( VMEModuleTypes::ECROCClockModes clockMode, 
        unsigned short testPulseDelayEnabled, 
        unsigned short testPulseDelayValue) const; 
    void SetupResetAndTestPulseRegister( unsigned short resetEnable, 
        unsigned short testPulseEnable ) const; 
    void InitializeRegisters( VMEModuleTypes::ECROCClockModes clockMode, 
        unsigned short testPulseDelayValue,
        unsigned short testPulseDelayEnabled, 
        unsigned short sequencerDelayValue,
	Modes::RunningModes runningMode) const; 

    void FastCommandOpenGate() const;
    void ClearAndResetStatusRegisters() const;
    void SendSoftwareRDFE() const; // manually start sequencer readout
    void WaitForSequencerReadoutCompletion() const;

    void ResetEventCounter() const;
    void EnableSequencerReadout() const;
    void DisableSequencerReadout() const;
    void ConfigureForStandardDataTaking() const;
    void UseSinglePipelineReadout() const;

    unsigned short ReadSequencerPulseDelayRegister() const;
    void SequencerDelayDisable() const;
    void SequencerDelayEnable() const;
    void SetSequencerDelayValue( unsigned short delay ) const; // 9 lowest bits

/*
12/10/2014 Geoff Savage
Additions for running in "cosmics" mode.
*/
    void FastCommandFEBTriggerRearm() const;
};

#endif
