/*! daq_server.h: The include files needed for the network sockets slave (data server) process. */
#include <netinet/in.h> // constants and structs for internet domain names
#include <netdb.h>      // defines hostent struct
#include <sys/socket.h> // definitions and structs for sockets
#include <unistd.h>

struct sockaddr_in daq_service; // internet socket address, contains machine and port number
int socket_handle, gate_number;
bool done[1];

// *global* gates are tracked on the server node.
int gates[1];        // Run length in *gates*
int runMode[1];      // Running Mode - 0==OneShot, 1==NuMI, etc.
int runNum[1];       // Run Number
int subNum[1];       // Subrun Number
int detect[1];       // Detector Code (0==Unknown, 1==PMT Test Stand, etc.
int totSec[1];       // Run length in *seconds* - passed but ignored by the DAQ right now.
char conf_file[100]; // Config. File name for SlowControl
int detConf[1];      // Detector Config - # of FEB's
int ledLevel[1];     // LED light level (only stored in DAQ Header, not used).
int ledGroup[1];     // LED group (only stored in DAQ Header, not used).
char et_file[100];   // Really just the base file root (used for ET, SAM, logging).
// Official MINERvA Base file name: DD_RRRRRRRR_SSSS_YYYYY_vVV_TTTTTTTTTT
// D = Detector
// R = Run Number
// S = Sub-run Number
// Y = Run Type
// V = DAQ Version
// T = Date (YYMMDDHHMM - UTC)

const static unsigned short port=1090; //the port number for our TCP service

struct in_addr socket_address; // internet address - we'll let the computer tell us what it's address is

int make_socket(); // make the server socket the head node will hook up to 

int launch_minervadaq();

int server();

int read_setup_data(int connection);

int write_server_response(int connection);  // remember the readout nodes are data *servers*, 
                                            // but acquisition start signal clients
