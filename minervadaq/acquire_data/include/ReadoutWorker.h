#ifndef ReadoutWorker_h
#define ReadoutWorker_h
#include "MinervaDAQtypes.h"
#include "Controller.h" 
#include "ECROC.h"
#include "CRIM.h"
#include "log4cppHeaders.h"

#include "ReadoutTypes.h"

#include "MinervaEvent.h"
#include "event_builder.h"

#include <fstream>
#include <string>
#include <sstream>

log4cpp::Category& readoutLogger = log4cpp::Category::getInstance(std::string("readoutLogger"));

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

		log4cpp::Appender* rwAppender;

    int controllerID;  // == crate ID/Address
		bool vmeModuleInit;    

    CRIM* masterCRIM();

	public:

    ReadoutWorker( int controllerID, log4cpp::Appender* appender, log4cpp::Priority::Value priority, bool vmeInit=false); 
    ~ReadoutWorker();

    void InitializeCrate( RunningModes runningMode );

    Controller* GetController();

    void AddECROC( unsigned int address, int nFEBchan0=11, int nFEBchan1=11, int nFEBchan2=11, int nFEBchan3=11 );
    void AddCRIM( unsigned int address );
    /*
       void InitializeDaq(int id, RunningModes runningMode);

       void InitializeCrim(int address, int index, RunningModes runningMode); 
       void InitializeCroc(int address, int crocNo, int nFEBchain0=11, int nFEBchain1=11, int nFEBchain2=11, int nFEBchain3=11); 
       int SetupIRQ(int index);
       int ResetGlobalIRQEnable(int index);
       int BuildFEBList(int chainID, int crocNo, int nFEBs=11);
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
