#ifndef ReadoutStateRecorder_h
#define ReadoutStateRecorder_h

#include "log4cppHeaders.h"


#include "DAQWorkerArgs.h"
#include "DAQHeader.h"

#include <fstream>
#include <string>
#include <sstream>
#include <tr1/memory>  // for shared_ptrs

/*! \class ReadoutStateRecorder
 */
class ReadoutStateRecorder {

  friend std::ostream& operator<<(std::ostream&, const ReadoutStateRecorder&);

	private: 

    int gate;
    int triggerType;
    unsigned long long globalGate;
    unsigned long long gateStartTime;
    unsigned long long gateFinishTime;

    const DAQWorkerArgs* args;

    void GetGlobalGateFromFile();
    void IncrememntGlobalGate();
    void WriteGlobalGateToFile();

    void WriteToSAMFile();
    void WriteLastTriggerDataToFile();

	public:

    explicit ReadoutStateRecorder( const DAQWorkerArgs* theArgs, 
        log4cpp::Priority::Value priority ); 
    ~ReadoutStateRecorder();

    bool BeginNextGate();
    bool FinishGate();

    std::tr1::shared_ptr<DAQHeader> GetDAQHeader( HeaderData::BankType bankType );

};

#endif
