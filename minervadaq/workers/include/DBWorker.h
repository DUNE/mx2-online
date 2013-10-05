#ifndef DBWorker_h
#define DBWorker_h
/*! \file DBWorker.h
*/

#include <sqlite3.h>

#include "log4cppHeaders.h"
#include "DAQWorkerArgs.h"
#include "FHWException.h"

/*! 
  \class DBWorker
  \brief Manage SQLite database logging.
  \author Gabriel Perdue
  */
class DBWorker {

  private:  
    const DAQWorkerArgs* args;

    sqlite3 *dataBase;
    bool dbIsAvailable;

    int AcquireResources();
    int ReleaseResources();
    int CreateTable(const char * sqlstr) const;

  public:
    explicit DBWorker( const DAQWorkerArgs* theArgs, log4cpp::Priority::Value priority );
    ~DBWorker();

    int CreateStandardRunsTable() const;
    int CreateStandardHWErrorsTable() const;
    int AddErrorToDB( const FHWException & ex,
        unsigned long long globalGate,
        int run, int subrun ) const;
    int AddRunDataToDB( unsigned long long firstGate,
        unsigned long long globalGate,
	int run, int subrun, unsigned long long subRunStartTime,
	unsigned long long subRunFinishTime, int runmode, std::string logFileName ) const;

};

#endif
