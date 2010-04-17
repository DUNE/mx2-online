/* header file for minervadaq main. */
#include <string>
/*! The include files needed for the network
 *  sockets 
 */
#include <netinet/in.h>
#include <netdb.h>
#include <sys/socket.h>
#include <unistd.h>


boost::mutex main_mutex; /*!< A BOOST multiple exclusion for use in threaded operation */

bool data_ready, evt_record_available;   /*!<data status variables */
/*! a function for selecting a trigger and waiting on it */
int TriggerDAQ(acquire_data *daq, unsigned short int triggerType, RunningModes runningMode, controller *tmpController); 
/*! the function which governs the entire data acquisition sequence */
int TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id,int thread, 
              et_att_id  attach, et_sys_id  sys_id, bool readFPGA=true, int nReadoutADC=8); 
/*! Get the Global Gate value indexed in /work/conditions/soldierToWorker.dat */
int inline GetGlobalGate();
/*! Put the Global Gate value into /work/conditions/soldierToWorker.dat */
void inline PutGlobalGate(int ggate);
/*! Write the (complete, as of trigger X) SAM metadata */
int WriteSAM(const char samfilename[], 
	const unsigned long long firstEvent, const unsigned long long lastEvent, 
	const std::string datafilename, const int detector, const char configfilename[], 
	const int runningMode, const int eventCount, const int runNum, const int subNum, 
	const unsigned long long startTime, const unsigned long long stopTime);
/*! Synch readout nodes - write */ //TODO - return an int!
template <typename Any> void SynchWrite(int socket_handle, Any *data);
/*! Synch readout nodes - listen */ //TODO - return an int!
template <typename Any> void SynchListen(int socket_connection, Any *data); 

/* some logging files for debugging purposes */
#if TIME_ME
std::ofstream take_data_extime_log; /*!<an output file for tiing data */
#endif
std::ofstream trigger_log; /*!<an output file for trigger debuggin */

// Socket Communication Functions
void CreateSocketPair(int &workerToSoldier_socket_handle, int &soldierToWorker_socket_handle);
void SetupSocketService(struct sockaddr_in &socket_service, struct hostent *node_info, 
	std::string hostname, const int port );

// Socket Communication Vars.
bool               gate_done_data[1];       // end of gate complete signal from the worker -> soldier 
unsigned long long global_gate_data[1];     // temp
unsigned short int workerToSoldier_trig[1]; // trigger check the worker -> soldier 
unsigned short int soldierToWorker_trig[1]; // trigger check the soldier -> worker 

// worker to soldier service vars.
struct in_addr     workerToSoldier_socket_address;
int                workerToSoldier_socket_connection; 
bool               workerToSoldier_socket_is_live;

// soldier to worker service vars.
struct in_addr     soldierToWorker_socket_address;
int                soldierToWorker_socket_connection; 
bool               soldierToWorker_socket_is_live;


// Base values for cycle between set of ports.
unsigned short workerToSoldier_port = 1110;
unsigned short soldierToWorker_port = 1120; 

#if MASTER&&(!SINGLEPC) // Soldier Node
/* minervadaq server for "master" (soldier node) DAQ */
struct sockaddr_in          workerToSoldier_service;
struct sockaddr_in          soldierToWorker_service;
int                         workerToSoldier_socket_handle;
int                         soldierToWorker_socket_handle;
struct hostent *            worker_node_info; // server on worker node
#endif

#if (!MASTER)&&(!SINGLEPC) // Worker Node
/* minervadaq client for "slave" (worker node) DAQ */
struct sockaddr_in          workerToSoldier_service;
struct sockaddr_in          soldierToWorker_service;
int                         workerToSoldier_socket_handle;
int                         soldierToWorker_socket_handle;
struct hostent *            soldier_node_info; // server on soldier node
#endif
