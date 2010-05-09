/*! The include files needed for the network
 *  sockets 
 */
#include <netinet/in.h>
#include <netdb.h>
#include <sys/socket.h>
#include <unistd.h>

struct sockaddr_in daq_service;
int socket_handle, gate_number;
bool done[1];
int gates[1];
char et_file[100]; //I don't know how long this name really is

const static unsigned short port=1090; //the port number for our TCP service

struct in_addr socket_address; //we'll let the computer tell us what it's address is

int make_socket();

int launch_minervadaq();

int server();

int read_setup_data(int connection);

int write_server_response(int connection);

