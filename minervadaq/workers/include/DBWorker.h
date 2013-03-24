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

  public:
    explicit DBWorker( const DAQWorkerArgs* theArgs, log4cpp::Priority::Value priority );
    ~DBWorker();

    int CreateStandardTable() const;
    int AddErrorToDB( FHWException & ex ) const;
};

#endif
