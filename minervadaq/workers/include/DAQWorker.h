#ifndef DAQWorker_h
#define DAQWorker_h
/*! \file DAQWorker.h
*/

#include "log4cppHeaders.h"
#include "DAQWorkerArgs.h"
#include "EventHandler.h"
#include "DBWorker.h"
#include "ReadoutWorker.h"
#include "ReadoutStateRecorder.h"
#include "et.h"          // the event transfer stuff
#include "et_private.h"  // event transfer private data types
#include "et_data.h"     // data structures 

/* #include <cstddef> */
/* #include <cstdlib> */
/* #include <assert.h> */

/*! 
  \class DAQWorker
  \brief Orchestrate data acquisition by being the central hub for other
  worker classes.
  \author Gabriel Perdue
  */
class DAQWorker {

  private:  
    const DAQWorkerArgs* args;
    const sig_atomic_t *const status;
    bool declareEventsToET;

    ReadoutStateRecorder* stateRecorder;
    ReadoutWorker* readoutWorker;
    DBWorker* dbWorker;

    void DissolveDataBlock( std::tr1::shared_ptr<SequencerReadoutBlock> block );

    et_att_id      attach; 
    et_sys_id      sys_id; 
    bool ContactEventBuilder( EventHandler *handler );
    void DeclareDAQHeaderToET( HeaderData::BankType bankType = HeaderData::DAQBank );

    template <class X> void DeclareDataBlock( X *dataBlock );
    template <class X> struct EventHandler * CreateEventHandler( X *dataBlock );
    void DestroyEventHandler( struct EventHandler * handler );

    bool BeginNextGate();
    bool FinishGate();

  public:
    explicit DAQWorker( const DAQWorkerArgs* theArgs, 
        log4cpp::Priority::Value priority, sig_atomic_t *status );
    ~DAQWorker();

    int SetUpET();  
    void InitializeHardware();  
    void CleanupHardware();  
    void TakeData();
    bool CloseDownET();
    bool SendSentinel();
    int WriteExceptionToDB( const FHWException & ex );
};

#endif
