#ifndef DBWorker_cxx
#define DBWorker_cxx
/*! \file DBWorker.cpp
*/

#include <fstream>
#include <sys/stat.h>

#include "DBWorker.h"
#include "VMEAddressTranslator.h"

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
  int rc = this->AcquireResources();
  dbWorker.debugStream() << "ctor status: " << rc;
}

//---------------------------------------------------------
DBWorker::~DBWorker()
{
  int rc = this->ReleaseResources();
  dbWorker.debugStream() << "dtor Status: " << rc;
}

//---------------------------------------------------------
int DBWorker::AcquireResources() 
{
  dbWorker.debugStream() << "AcquireResources...";
  const char * dbFileName = args->errDBFileName.c_str(); 
  char * vfsName = NULL;  
  int rc = 0;
  int flags = SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE; 

  sqlite3_initialize();
  rc = sqlite3_open_v2( dbFileName, &dataBase, flags, vfsName ); 
  if (SQLITE_OK != rc) {
    sqlite3_close( dataBase );
  }
  if (SQLITE_OK == rc) {
    dbIsAvailable = true;
  }
  dbWorker.debugStream() << " Open status = " << rc;

  struct stat sb;
  stat( dbFileName, &sb );
  dbWorker.debug("DB File exists? File size: %lld bytes", (long long) sb.st_size);
  if (0 == sb.st_size) {
    rc = this->CreateStandardTable();
  }
  if (SQLITE_OK != rc) {
    dbIsAvailable = false;
  }
  dbWorker.debugStream() << " Table status = " << rc;

  return rc;
}

//---------------------------------------------------------
int DBWorker::ReleaseResources()
{
  dbWorker.debugStream() << "ReleaseResources...";
  int rc = sqlite3_close( dataBase ); 
  dbWorker.debugStream() << "SQLite Close: " << rc;
  rc = sqlite3_shutdown();
  dbWorker.debugStream() << "SQLite Shutdown: " << rc;
  dbIsAvailable = false;

  return rc;
}

//---------------------------------------------------------
int DBWorker::CreateStandardTable() const
{
  if (!dbIsAvailable) return SQLITE_ERROR;

  sqlite3_stmt *stmt = NULL;

  const char * sqlstr = "CREATE TABLE HWERRORS ( \
    GLOBALGATE UNSIGNED BIG INT NOT NULL, \
    ETIMESTAMP TIMESTAMP, \
    CRATE INTEGER NOT NULL, \
    FEB INTEGER NOT NULL, \
    VMETYPE INTEGER NOT NULL, \
    ADDRESS UNSIGNED BIG INT NOT NULL, \
    CRIM INTEGER NOT NULL, \
    CROC INTEGER NOT NULL, \
    CHANNEL INTEGER NOT NULL, \
    MESSAGE TEXT, \
    PRIMARY KEY (GLOBALGATE));";

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
int DBWorker::AddErrorToDB( const FHWException & ex, 
    unsigned long long globalGate ) const
{
  if (!dbIsAvailable) return SQLITE_ERROR;

  int crateNumber = ex.getCrate();
  int feb = (int)ex.getFEBAddress();
  int vme = (int)ex.getVMECommunicatorType();
  sqlite3_int64 address = (sqlite3_int64)ex.getVMEAddress();
  const char * msg = const_cast<FHWException *>(&ex)->what(); // sadly, what() is non-const
  int crim = (int)VMEAddressTranslator::GetCRIMNumber( address );
  int croc = (int)VMEAddressTranslator::GetECROCNumber( address );
  int chnl = (int)VMEAddressTranslator::GetEChannelsNumber( address );
#ifndef GOFAST
#endif
  dbWorker.debugStream() << "AddErrorToDB: Crate = " << crateNumber << "; FEB = " << feb << 
    "; VME Type = " << vme << "; Address = " << address;
  dbWorker.debugStream() << " Parsed Address CRIM  Number = " << crim; 
  dbWorker.debugStream() << " Parsed Address ECROC Number = " << croc;
  dbWorker.debugStream() << " Parsed Address EChnl Number = " << chnl;
  dbWorker.debugStream() << " Global Gate: " << globalGate;
  dbWorker.debugStream() << " Message: " << msg;

  sqlite3_stmt *stmt = NULL;
  int idx = -1;
  const char * sqlstr = 
    "INSERT INTO HWERRORS VALUES ( \
    :globalGate, CURRENT_TIMESTAMP, :crate, :feb, :vmetype, :address, :crim, :croc, :channel, :message );"; 

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

  idx = sqlite3_bind_parameter_index( stmt, ":globalGate" );
  rc = sqlite3_bind_int( stmt, idx, globalGate );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":crate" );
  rc = sqlite3_bind_int( stmt, idx, crateNumber );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":feb" );
  rc = sqlite3_bind_int( stmt, idx, feb );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":vmetype" );
  rc = sqlite3_bind_int( stmt, idx, vme );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":address" );
  rc = sqlite3_bind_int64( stmt, idx, address );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":crim" );
  rc = sqlite3_bind_int( stmt, idx, crim );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":croc" );
  rc = sqlite3_bind_int( stmt, idx, croc );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":channel" );
  rc = sqlite3_bind_int( stmt, idx, chnl );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  idx = sqlite3_bind_parameter_index( stmt, ":message" );
  rc = sqlite3_bind_text( stmt, idx, msg, -1, SQLITE_STATIC );
  if (SQLITE_OK != rc) {
    dbWorker.errorStream() << "sqlite3_bind failed with rc = " << rc;
    return rc;
  }

  rc = sqlite3_step( stmt );
  if (( SQLITE_DONE != rc ) && ( SQLITE_ROW != rc )) {
    dbWorker.errorStream() << "sqlite3_step failed with rc = " << rc;
    return rc;
  }

  sqlite3_reset( stmt ); // reset probably unnecessary since we done anyway
  sqlite3_clear_bindings( stmt );  

  sqlite3_finalize( stmt );
  stmt = NULL;

  return SQLITE_OK;
}


#endif
