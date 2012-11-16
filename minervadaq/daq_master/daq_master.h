/*! daq_master.h: The include files needed for the network sockets master process. */
#include <netinet/in.h> // constants and structs for internet domain names
#include <netdb.h>      // defines hostent struct
#include <sys/socket.h> // definitions and structs for sockets
#include <unistd.h>
#include <arpa/inet.h>

struct sockaddr_in daq_client[2]; // internet socket address, contains machine and port number 
                                  // (one for each readout node).  "client" is a bit confusing 
                                  // because these are data servers, but set-up info clients.
int socket_handle[2];     // file descriptors (array subscripts in file descriptor table) for readout node sockets
struct hostent *hostinfo; // h_addr field contain's the host IP number
bool done[2];

// *global* gates are tracked on the server node.
int gates[2];        // Run length in *gates*
int runMode[2];      // Running Mode - 0==OneShot, 1==NuMI, etc.
int runNum[2];       // Run Number
int subNum[2];       // Subrun Number
int detect[2];       // Detector Code (0==Unknown, 1==PMT Test Stand, etc.
int totSec[2];       // Run length in *seconds* - passed but ignored by the DAQ right now.
char conf_file[100]; // Config. File name for SlowControl
int detConf[2];      // Detector Config - # of FEB's
int ledLevel[2];     // LED light level (only stored in DAQ Header, not used).
int ledGroup[2];     // LED group (only stored in DAQ Header, not used).
int initLevel[2];    // HW init level (0 does nothing, non-zero does something).
int netPort[2];      // ET Network Port
char et_file[100];   // Really just the base file root (used for ET, SAM, logging).
// Official MINERvA Base file name: DD_RRRRRRRR_SSSS_YYYYY_vVV_TTTTTTTTTT
// D = Detector
// R = Run Number
// S = Sub-run Number
// Y = Run Type
// V = DAQ Version
// T = Date (YYMMDDHHMM - UTC)

const int daq_slaves = 2;

const static unsigned short port=1090; //the port number for our TCP service

struct in_addr socket_address; // internet address - we'll let the computer tell us what it's address is
                               // in_addr contains only one field btw - one unsigned long called s_addr
int make_socket();

int write_setup_data();

int read_server_response(); // remember the readout nodes are data *servers*, 
                            // but acquisition start signal clients
