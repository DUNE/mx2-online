#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <cerrno>

#include "daq_server.h"

/*! \fn
 *  The MINERvA DAQ server
 *  The client-server model for DAQ acquisition across machines 
 *  uses internet sockets to transfer data from the "master" 
 *  node to two "slave" nodes.  The "slave" nodes will be
 *  executing the acquisition sequence.
 *  
 *  This is the server.  It executes the data acquisition sequence on
 *  its own node.   Then it sends a signal back to the master to 
 *  inform it that the acquisition has completed.
 *
 *  This is modeled after client-server operation outlined in 
 *  Advanced Linux Programming by CodeSourcery LLC, published by New Riders Publishing.
 *  http://www.advancedlinuxprogramming.com/
 *
 */

using namespace std;

int main() {
  done[0] = false; //set the loop flag
  server(); //run the server  

  return 0; //success
}

int make_socket() {
   
  /* create a TCP socket */
  socket_handle = socket (PF_INET, SOCK_STREAM, 0);
  if (socket_handle == -1) {
    perror("socket");
    exit(EXIT_FAILURE);
  }

  socket_address.s_addr = htonl(INADDR_ANY); //bind to the local address
  
  memset (&daq_service, 0, sizeof (daq_service));
  daq_service.sin_family = AF_INET;
  daq_service.sin_port = htons(port);
  daq_service.sin_addr = socket_address;

  /* Bind the socket to that address. */
  if ((bind (socket_handle, (const sockaddr*)&daq_service, sizeof (daq_service)))) {
    perror ("bind");
    exit(EXIT_FAILURE);
  }

  return 0; //success
}

int launch_minervadaq() {
  stringstream process_gates;
  process_gates<<gates[0];
  string command = "$DAQROOT/bin/minervadaq ./"+string(et_file)+" "+process_gates.str()+" > log_file";
  cout<<"launch_minervadaq command: "<<command<<endl;
  if ((system(command.c_str())!=-1)) {
    perror("run_minervadaq failed");
    exit(EXIT_FAILURE);
  }
  return 0; //success
}

int server() {
  /* first make the socket */
  if (make_socket()) {
    perror("make_socket"); 
    exit(EXIT_FAILURE);
  }
  /* Listen on our new socket for connections */
  if (listen (socket_handle, 10)) {
    perror("listen");
    exit(EXIT_FAILURE);
  }
  while (!done[0]) {
    struct sockaddr_in remote_address;
    socklen_t address_length;
    int master_connection, minervadaq_connection;
    address_length = sizeof (remote_address);
    master_connection = accept (socket_handle, (sockaddr*)&remote_address, &address_length);
    if (master_connection == -1) {
      /* The call to accept failed. */
      if (errno == EINTR)
        /* The call was interrupted by a signal. Try again. */
        continue;
      else
        /* Something else went wrong. */
        perror("accept");
        exit(EXIT_FAILURE);
    }
    read_setup_data(master_connection); //read the daq setup data from the "master"
    /* sending the "done" value from the master to the slaves triggers the acquitision sequence */
    int success = launch_minervadaq();
    if (!success) {
      perror ("minervadaq");
      exit(EXIT_FAILURE);
    } 
    write_server_response(master_connection); //write that we are done back to the "master"
    close(master_connection); 
  }
  /* successful completion, close the connection */

  /* close the server socket */
  close(socket_handle);
 
  return 0; //success
}

int read_setup_data(int master_connection) {
    /********************************************************************************/
    cout<<"sizeof(gates): "<<sizeof(gates)<<endl;
    if ((read(master_connection,gates,sizeof(gates)))!=sizeof(gates)) { 
      perror("server read error: gates"); //read in the number of gates to process
      exit(EXIT_FAILURE);
    }
    cout<<"Number of gates to process: "<<gates[0]<<endl;
    /********************************************************************************/

    /********************************************************************************/
    if ((read(master_connection,et_file,sizeof(et_file)))!=sizeof(et_file)) {  //read in the ET filename for data storage
      perror("server read error: et_file"); //read in the number of gates to process
      exit(EXIT_FAILURE);
    }
    cout<<"Name of ET file: "<<et_file<<endl;
    /********************************************************************************/

    /********************************************************************************/
    if ((read (master_connection, done, sizeof (done)))!=sizeof(done)) { //read "done" from the master
      perror("server read error: done"); //read in the number of gates to process
      exit(EXIT_FAILURE);
    }
    cout<<"Are we done? "<<done[0]<<endl;
    /********************************************************************************/
  return 0;
}

int write_server_response(int connection) {
  done[0] = true;
  write(connection,done,1); //we're done!
  return 0;
}

