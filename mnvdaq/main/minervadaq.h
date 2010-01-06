/* header file for minervadaq main. */
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
void TriggerDAQ(acquire_data *daq, unsigned short int triggerType, RunningModes runningMode, controller *tmpController); 
/*! the function which governs the entire data acquisition sequence */
void TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id,int thread, 
              et_att_id  attach, et_sys_id  sys_id); //the data taking routine

/* some logging files for debugging purposes */
std::ofstream take_data_extime_log; /*!<an output file for tiing data */
std::ofstream trigger_log; /*!<an output file for trigger debuggin */

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

#if MASTER&&(!SINGLE_PC) // Soldier Node
/* minervadaq server for "master" (soldier node) DAQ */
struct sockaddr_in          gate_done_service;
struct sockaddr_in          global_gate_service;
int                         gate_done_socket_handle;
int                         global_gate_socket_handle;
struct hostent *            worker_node_info; // server on worker node
const static unsigned short gate_done_port   = 1095; //the port number for our TCP service
const static unsigned short global_gate_port = 1096; //the port number for our TCP service
#endif

#if (!MASTER)&&(!SINGLE_PC) // Worker Node
/* minervadaq client for "slave" (worker node) DAQ */
struct sockaddr_in          gate_done_service;
struct sockaddr_in          global_gate_service;
int                         gate_done_socket_handle;
int                         global_gate_socket_handle;
struct hostent *            soldier_node_info; // server on soldier node
const static unsigned short gate_done_port   = 1095; //the port number for our TCP service
const static unsigned short global_gate_port = 1096; //the port number for our TCP service
#endif
