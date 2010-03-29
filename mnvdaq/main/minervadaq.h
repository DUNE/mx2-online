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
              et_att_id  attach, et_sys_id  sys_id); //the data taking routine
/*! Get the Global Gate value indexed in /work/conditions/global_gate.dat */
int inline GetGlobalGate();
/*! Put the Global Gate value into /work/conditions/global_gate.dat */
void inline PutGlobalGate(int ggate);
/*! Write the (complete, as of trigger X) SAM metadata */
int WriteSAM(const char samfilename[], 
	const unsigned long long firstEvent, const unsigned long long lastEvent, 
	const std::string datafilename, const int detector, const char configfilename[], 
	const int runningMode, const int eventCount, const int runNum, const int subNum, 
	const unsigned long long startTime, const unsigned long long stopTime);
/*! Synch readout nodes - write */ //TODO - use templated function
void SynchWrite(int socket_handle, unsigned long long data[]);
void SynchWrite(int socket_handle, bool data[]);
/*! Synch readout nodes - listen */ //TODO - use templated function
void SynchListen(int socket_connection, unsigned long long data[]); 
void SynchListen(int socket_connection, bool data[]); 

/* some logging files for debugging purposes */
#if TIME_ME
std::ofstream take_data_extime_log; /*!<an output file for tiing data */
#endif
std::ofstream trigger_log; /*!<an output file for trigger debuggin */

// Socket Communication Functions
void CreateSocketPair(int &gate_done_socket_handle, int &global_gate_socket_handle);
void SetupSocketService(struct sockaddr_in &socket_service, struct hostent *node_info, 
	std::string hostname, const int port );

// Socket Communication Vars.
bool               gate_done[1]; // signal for end of event readout completion from the worker -> soldier
unsigned long long global_gate_data[1]; // signal for end of trigger from the worker -> soldier
bool               ready_to_go[1];

// End of Gate service vars.
struct in_addr     gate_done_socket_address;
int                gate_done_socket_connection; 
bool               gate_done_socket_is_live;

// Global Gate service vars.
struct in_addr     global_gate_socket_address;
int                global_gate_socket_connection; 
bool               global_gate_socket_is_live;


// TODO - cycle between a set of ports
unsigned short gate_done_port   = 1110;
unsigned short global_gate_port = 1120; 

#if MASTER&&(!SINGLEPC) // Soldier Node
/* minervadaq server for "master" (soldier node) DAQ */
struct sockaddr_in          gate_done_service;
struct sockaddr_in          global_gate_service;
int                         gate_done_socket_handle;
int                         global_gate_socket_handle;
struct hostent *            worker_node_info; // server on worker node
#endif

#if (!MASTER)&&(!SINGLEPC) // Worker Node
/* minervadaq client for "slave" (worker node) DAQ */
struct sockaddr_in          gate_done_service;
struct sockaddr_in          global_gate_service;
int                         gate_done_socket_handle;
int                         global_gate_socket_handle;
struct hostent *            soldier_node_info; // server on soldier node
#endif
