#ifndef DBWorker_cxx
#define DBWorker_cxx
/*! \file DBWorker.cpp
*/

#include <fstream>

#include "DBWorker.h"

log4cpp::Category& dbWorker = 
log4cpp::Category::getInstance(std::string("dbWorker"));

//---------------------------------------------------------
DBWorker::DBWorker( const DAQWorkerArgs* theArgs, 
    log4cpp::Priority::Value priority ) :
  args(theArgs),
  dataBase(NULL),
  dbIsAvailable(false)
{
  dbWorker.setPriority(priority);

  const char * dbFileName = args->errDBFileName.c_str(); 
  char * vfsName = NULL;  
  int rc = 0;
  int flags = SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE; 

  sqlite3_initialize();
  rc = sqlite3_open_v2( dbFileName, &dataBase, flags, vfsName ); 

  if (SQLITE_OK != rc) {
    sqlite3_close( dataBase );
  }
  else {
    dbIsAvailable = true;
  }
}

//---------------------------------------------------------
DBWorker::~DBWorker()
{
  sqlite3_close( dataBase ); 
  sqlite3_shutdown();
}

//---------------------------------------------------------
int DBWorker::CreateStandardTable() const
{
  if (!dbIsAvailable) return SQLITE_ERROR;

  sqlite3_stmt *stmt = NULL;

  const char * sqlstr = "CREATE TABLE HWERRORS (        \
                         ETIMESTAMP   TIMESTAMP,        \
                         CRATE        INTEGER NOT NULL, \
                         FEB          INTEGER NOT NULL, \
                         VMETYPE      INTEGER NOT NULL, \
                         ADDRESS      UNSIGNED BIG INT NOT NULL, \
                         MESSAGE      TEXT,             \
                         PRIMARY KEY (ETIMESTAMP));";

  int rc = sqlite3_prepare_v2(
      dataBase,
      sqlstr,
      -1,
      &stmt,
      NULL);
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_prepare failed with rc = " << rc;
    return rc;
  }

  rc = sqlite3_step( stmt );
  if (SQLITE_DONE != rc) {
    dbWorker.errorStream() << "sqlite3_step failed with rc = " << rc;
    return rc;
  }

  sqlite3_finalize(stmt);
  return SQLITE_OK;
}

//---------------------------------------------------------
int DBWorker::AddErrorToDB( FHWException & ex ) const
{
  if (!dbIsAvailable) return SQLITE_ERROR;

  int crateNumber = ex.getCrate();
  int feb = (int)ex.getFEBAddress();
  int vme = (int)ex.getVMECommunicatorType();
  sqlite3_int64 address = (sqlite3_int64)ex.getVMEAddress();
  const char * msg = ex.what();
#ifndef GOFAST
#endif
  dbWorker.debugStream() << "AddErrorToDB: Crate = " << crateNumber << "; FEB = " << feb << 
    "; VME Type = " << vme << "; Address = " << address;
  dbWorker.debugStream() << " Message: " << msg;

  sqlite3_stmt *stmt = NULL;
  int idx = -1;
  const char * sqlstr = 
    "INSERT INTO HWERRORS VALUES ( \
    CURRENT_TIMESTAMP, :crate, :feb, :vmetype, :address, :message );"; 

    int rc = sqlite3_prepare_v2( 
        dataBase,
        sqlstr,
        -1, 
        &stmt, 
        NULL );

  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_prepare failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":crate" );
  sqlite3_bind_int( stmt, idx, crateNumber );

  idx = sqlite3_bind_parameter_index( stmt, ":feb" );
  sqlite3_bind_int( stmt, idx, feb );

  idx = sqlite3_bind_parameter_index( stmt, ":vmetype" );
  sqlite3_bind_int( stmt, idx, vme );

  idx = sqlite3_bind_parameter_index( stmt, ":address" );
  sqlite3_bind_int64( stmt, idx, address );

  idx = sqlite3_bind_parameter_index( stmt, ":message" );
  sqlite3_bind_text( stmt, idx, msg, -1, SQLITE_STATIC );

  /* SQLITE_API int sqlite3_bind_int64(sqlite3_stmt*, int, sqlite3_int64); */

  rc = sqlite3_step( stmt );
  if (( SQLITE_DONE != rc ) && ( SQLITE_ROW != rc )) {
    dbWorker.errorStream() << "sqlite3_step failed with rc = " << rc;
    return rc;
  }

  sqlite3_finalize( stmt );

  return SQLITE_OK;
}


#endif
