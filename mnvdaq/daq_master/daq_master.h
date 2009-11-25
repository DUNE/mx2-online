/*! The include files needed for the network
 *  sockets 
 */
#include <netinet/in.h>
#include <netdb.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>

struct sockaddr_in daq_client[2];
int socket_handle[2];
struct hostent *hostinfo;
bool done[2];
int gates[2];
char et_file[100]; //I don't know how long this name really is

const int daq_slaves = 2;

const static unsigned short port=1090; //the port number for our TCP service

struct in_addr socket_address; //we'll let the computer tell us what it's address is

int make_socket();

int write_setup_data();

int read_server_response();
