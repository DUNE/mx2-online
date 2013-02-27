#ifndef ReadoutWorker_h
#define ReadoutWorker_h

#include "log4cppHeaders.h"

#include "MinervaDAQtypes.h"
#include "Controller.h" 
#include "ECROC.h"
#include "CRIM.h"
#include "SequencerReadoutBlock.h"

#include "ReadoutTypes.h"

#include "MinervaEvent.h"
#include "event_builder.h"

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
	private: 
		Controller *controller;
    std::vector<ECROC*> ecrocs;
    std::vector<CRIM*>  crims;

    std::vector<const EChannels*> readoutChannels;
    std::vector<const EChannels*>::iterator currentChannel;

    int crateID;  // == crate ID/Address for Controller
		bool vmeInit;    

    CRIM* masterCRIM();

	public:

    explicit ReadoutWorker( int theCrateID, log4cpp::Priority::Value priority, bool VMEInit=false); 
    ~ReadoutWorker();

    const Controller* GetController() const;

    void AddECROC( unsigned int address, int nFEBchan0=11, int nFEBchan1=11, int nFEBchan2=11, int nFEBchan3=11 );
    void AddCRIM( unsigned int address );
    void InitializeCrate( RunningModes runningMode );

    void Reset();
    void Trigger();
    bool MoveToNextChannel();
    const EChannels * CurrentChannel() const;
    unsigned short GetNextDataBlockSize() const;
    std::tr1::shared_ptr<SequencerReadoutBlock> GetNextDataBlock( unsigned short blockSize ) const;

    /*
       int TriggerDAQ(unsigned short int triggerBit, int crimID); // Note, be careful about the master CRIM.
       int WaitOnIRQ(sig_atomic_t const & continueFlag);
       int AcknowledgeIRQ();
       unsigned int GetMINOSSGATE();
       */

    /*! Function which fills an event structure for further data handling by the event builder; templated */
    /*
       template <class X> void FillEventStructure(event_handler *evt, int bank, X *frame, 
       channels *channelTrial);
       bool ContactEventBuilder(event_handler *evt, int thread, et_att_id attach, et_sys_id sys_id);
       void FillEventStructure(event_handler *evt, int bank, channels *theChannel);
       */

};

#endif
