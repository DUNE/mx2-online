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
/*! a function for setting the high voltage on FEB's */
void SetHV(acquire_data *daq, int i, int j); 
/*! a function for selecting a trigger and waiting on it */
void TriggerDAQ(acquire_data *daq, unsigned short int triggerType); // The triggering functions.
/*! the function which governs the entire data acquisition sequence */
void TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id,int thread, 
              et_att_id  attach, et_sys_id  sys_id); //the data taking routine

/* some logging files for debugging purposes */
std::ofstream take_data_extime_log; /*!<an output file for tiing data */
std::ofstream trigger_log; /*!<an output file for trigger debuggin */

bool gate_done[1];
struct in_addr socket_address;
#if MASTER&&(!SINGLE_PC)
/* minervadaq server for "master" DAQ */
struct sockaddr_in daq_service;
int socket_handle;
const static unsigned short port=1095; //the port number for our TCP service
#endif

#if (!MASTER)&&(!SINGLE_PC)
/* minervadaq client for "slave" DAQ */
struct sockaddr_in daq_service;
int socket_handle;
struct hostent *hostinfo;
const static unsigned short port=1095; //the port number for our TCP service
#endif
