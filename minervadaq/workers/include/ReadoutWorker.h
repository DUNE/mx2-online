#ifndef ReadoutWorker_h
#define ReadoutWorker_h
/*! 
  \file ReadoutWorker.h
  */

#include "log4cppHeaders.h"

#include "VMECrate.h"
#include "SequencerReadoutBlock.h"

#include "DAQHeader.h"
#include "RunHeader.h"

#include <fstream>
#include <string>
#include <sstream>

/*! 
  \class ReadoutWorker
  \brief Manage communication with the VME modules.
  \author Gabriel Perdue
  */
class ReadoutWorker {

  friend std::ostream& operator<<(std::ostream&, const ReadoutWorker&);

  static const int RunHeaderVersion;

  private: 

  std::vector<VMECrate*> crates;
  std::vector<const EChannels*> readoutChannels;
  std::vector<const EChannels*>::iterator currentChannel;

  const sig_atomic_t *const status;
  bool vmeInit;    
  Modes::RunningModes runningMode;

  CRIM* MasterCRIM() const;

  void EnableIRQ() const;
  bool WaitForIRQ() const;
  void AcknowledgeIRQ() const;
  void SendSoftwareGate() const;
  void ResetSequencerLatch() const;
  void ClearAndResetStatusRegisters() const;
  void OpenGateFastCommand() const;
  bool MicroSecondSleep(int us) const;
  void WaitForSequencerReadoutCompletion() const;

  static const unsigned int microSecondSleepDuration;

  public:

  explicit ReadoutWorker( log4cpp::Priority::Value priority, 
      sig_atomic_t *status, bool VMEInit=false); 
  ~ReadoutWorker();

  void AddCrate( unsigned int crateID );
  void InitializeCrates( Modes::RunningModes theRunningMode );
  std::vector<VMECrate*>* GetVMECrateVector();
  VMECrate* GetVMECrateVector( int index );
  void CleanupHardware();  

  unsigned int GetMINOSSGATE() const;
  unsigned long long GetNowInMicrosec() const;
  unsigned long long Trigger( Triggers::TriggerType triggerType );
  void ResetCurrentChannel();
  bool MoveToNextChannel();
  const EChannels * CurrentChannel() const;
  unsigned int GetNextDataBlockSize() const;
  std::tr1::shared_ptr<SequencerReadoutBlock> GetNextDataBlock( unsigned int blockSize ) const;
  std::tr1::shared_ptr<RunHeader> GetRunHeader( HeaderData::BankType bankType );

/*
12/10/2014 Geoff Savage
Additions for running in "cosmics" mode.
*/
    void FastCommandFEBTriggerRearm() const;
    void SendSoftwareRDFE() const;
    void ResetCosmicLatch () const;

    void InterruptInitialize();
    void InterruptResetToDefault();
    void InterruptClear() const;
    void InterruptEnable() const;
    int InterruptWait() const;
    unsigned long long TriggerCosmics( Triggers::TriggerType triggerType );

}; /* end class ReadoutWorker() */

#endif
