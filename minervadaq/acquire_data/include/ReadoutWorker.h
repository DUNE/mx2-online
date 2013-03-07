#ifndef ReadoutWorker_h
#define ReadoutWorker_h

#include "log4cppHeaders.h"

#include "VMEModuleTypes.h"
#include "Controller.h" 
#include "ECROC.h"
#include "CRIM.h"
#include "SequencerReadoutBlock.h"

#include "ReadoutTypes.h"

#include "DAQHeader.h"

#include <fstream>
#include <string>
#include <sstream>


/*! \class ReadoutWorker
 *  \brief The class containing all methods necessary for 
 *  requesting and manipulating data from the MINERvA detector.
 *
 *  This class contains all of the necessary functions 
 *  for acquiring and manipulating data from the MINERvA detector.
 *
 *  This class sets up the electronics, builds a list of FEB's on 
 *  each CROC channel, and executes the data acquisition sequence for each FEB
 *  on a channel.  These functions are called via an ReadoutWorker class object
 *  from the main routine.
 */
class ReadoutWorker {

  friend std::ostream& operator<<(std::ostream&, const ReadoutWorker&);

	private: 
		Controller *controller;
    std::vector<ECROC*> ecrocs;
    std::vector<CRIM*>  crims;

    std::vector<const EChannels*> readoutChannels;
    std::vector<const EChannels*>::iterator currentChannel;

    int crateID;  // == crate ID/Address for Controller
		bool vmeInit;    
    RunningModes runningMode;

    CRIM* masterCRIM();

    void ClearAndResetAllChannels();
    void OpenGateFastCommand();
    bool microSecondSleep(int us);

	public:

    explicit ReadoutWorker( int theCrateID, log4cpp::Priority::Value priority, bool VMEInit=false); 
    ~ReadoutWorker();

    const Controller* GetController() const;

    void AddECROC( unsigned int address, int nFEBchan0=11, int nFEBchan1=11, int nFEBchan2=11, int nFEBchan3=11 );
    void AddCRIM( unsigned int address );
    void InitializeCrate( RunningModes runningMode );

    void ResetCurrentChannel();
    unsigned long long Trigger();
    bool MoveToNextChannel();
    const EChannels * CurrentChannel() const;
    unsigned short GetNextDataBlockSize() const;
    std::tr1::shared_ptr<SequencerReadoutBlock> GetNextDataBlock( unsigned short blockSize ) const;
};

#endif
