#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <cerrno>
#include <cassert>

#include "daq_master.h"

/*! \fn
*  The MINERvA DAQ client
*  The client-server model for DAQ acquisition across machines 
*  uses internet sockets to transfer data from the "master" 
*  node to two "slave" nodes.  The "slave" nodes will be
*  executing the acquisition sequence.
*  
*  This is the client.  It interfaces with the DAQ servers 
*  running on the "slave" machines.  I know that sounds strange...
*
*/

using namespace std;

int main(int argc, char* argv[]) {
	if (argc<3) {
		cout << "Usage: daq_master <et_filename> <gates-to-acquire>" << endl;
		return -1;
	}
	for (int i=0;i<daq_slaves;i++) {
		gates[i] = atoi(argv[2]); 
		cout << "gates: " << gates[i] << endl;
	}

	sprintf(et_file,argv[1]);

	make_socket(); //make up the communication socket

	/* Connect to the DAQ Server server */
	for (int i=0;i<daq_slaves;i++) {
		if (connect (socket_handle[i], (struct sockaddr*) &daq_client[i], sizeof (struct sockaddr_in)) == -1) {
			perror ("connect");
			return 1;
		}
	}

	cou t<< "writing data to socket..." << endl;
	write_setup_data(); //write setup data to the "slave" 

	read_server_response(); //read the "slave" response
	return 0;
}

int make_socket() {
	/*********************************************************************************/
	/* Create the socket for minervatest03 (the "soldier" node). */
	socket_handle[0] = socket (PF_INET, SOCK_STREAM, 0);
	/* Store the server’s name in the socket address. */
	daq_client[0].sin_family = AF_INET;
	/* Convert from strings to numbers. */
	string hostname="minervatest03.fnal.gov"; //this needs to be changed for the appropriate machine
	hostinfo = gethostbyname(hostname.c_str()); // we'd like to do this with ip's directly eventually...
	if (hostinfo == NULL) return 1;
	else daq_client[0].sin_addr = *((struct in_addr *) hostinfo->h_addr);
	daq_client[0].sin_port = htons (port);
	cout<<"success, made the client socket"<<endl;
	/*********************************************************************************/

	/*********************************************************************************/
	/* Create the socket for minervatest02 (the "worker" node). */
	socket_handle[1] = socket (PF_INET, SOCK_STREAM, 0);
	/* Store the server’s name in the socket address. */
	daq_client[1].sin_family = AF_INET;
	/* Convert from strings to numbers. */
	hostname="minervatest02.fnal.gov"; //this needs to be changed for the appropriate machine
	hostinfo = gethostbyname(hostname.c_str());
	if (hostinfo == NULL) return 1;
	else daq_client[1].sin_addr = *((struct in_addr *) hostinfo->h_addr);
	daq_client[1].sin_port = htons (port);
	/*********************************************************************************/
	return 0;
}

int write_setup_data() {
	for (int i=0;i<daq_slaves;i++) {
		done[i] = false; //we are not yet ready to stop the DAQ

		cout<<"socket_handle: "<<socket_handle[i]<<endl;
		write(socket_handle[i],&gates[i], sizeof(gates[i])); //send the number of gates
		write(socket_handle[i], et_file, sizeof(et_file));
		write(socket_handle[i], &done[i], 1);  //send the status
	}
	return 0;
}

int read_server_response() {
	for (int i=0;i<daq_slaves;i++) {
		read(socket_handle[i], &done[i], 1); //read back the status
		cout<<"done? "<<done[0]<<endl;  
	}
	return 0;
}
