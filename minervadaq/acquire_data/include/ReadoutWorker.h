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

		bool vmeInit;    
    RunningModes runningMode;

    CRIM* MasterCRIM() const;

    void ClearAndResetStatusRegisters();
    void OpenGateFastCommand();
    bool MicroSecondSleep(int us);

	public:

    explicit ReadoutWorker( log4cpp::Priority::Value priority, bool VMEInit=false); 
    ~ReadoutWorker();

    void AddCrate( unsigned int crateID );
    void InitializeCrates( RunningModes theRunningMode );
    std::vector<VMECrate*>* GetVMECrateVector();
    VMECrate* GetVMECrateVector( int index );

    unsigned int GetMINOSSGATE() const;
    unsigned long long GetNowInMicrosec() const;
    unsigned long long Trigger();
    void ResetCurrentChannel();
    bool MoveToNextChannel();
    const EChannels * CurrentChannel() const;
    unsigned short GetNextDataBlockSize() const;
    std::tr1::shared_ptr<SequencerReadoutBlock> GetNextDataBlock( unsigned short blockSize ) const;
};

#endif
