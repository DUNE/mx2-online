#ifndef ReadoutWorker_h
#define ReadoutWorker_h

#include "log4cppHeaders.h"

#include "VMECrate.h"
#include "SequencerReadoutBlock.h"

#include "DAQHeader.h"

#include <fstream>
#include <string>
#include <sstream>


/*! \class ReadoutWorker
 */
class ReadoutWorker {

  friend std::ostream& operator<<(std::ostream&, const ReadoutWorker&);

	private: 

    std::vector<VMECrate*> crates;
    std::vector<const EChannels*> readoutChannels;
    std::vector<const EChannels*>::iterator currentChannel;

    const bool *const status;
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

    static const unsigned int microSecondSleepDuration;

	public:

    explicit ReadoutWorker( log4cpp::Priority::Value priority, 
        bool *status, bool VMEInit=false); 
    ~ReadoutWorker();

    void AddCrate( unsigned int crateID );
    void InitializeCrates( Modes::RunningModes theRunningMode );
    std::vector<VMECrate*>* GetVMECrateVector();
    VMECrate* GetVMECrateVector( int index );

    unsigned int GetMINOSSGATE() const;
    unsigned long long GetNowInMicrosec() const;
    unsigned long long Trigger( Triggers::TriggerType triggerType );
    void ResetCurrentChannel();
    bool MoveToNextChannel();
    const EChannels * CurrentChannel() const;
    unsigned short GetNextDataBlockSize() const;
    std::tr1::shared_ptr<SequencerReadoutBlock> GetNextDataBlock( unsigned short blockSize ) const;
};

#endif
