#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <cerrno>

#include "daq_server.h"

/*! \fn
*  The MINERvA DAQ Server.
*
*  The client-server model for DAQ acquisition across machines 
*  uses internet sockets to transfer data from the "master" 
*  node to two "slave" nodes.  The "slave" nodes will be
*  executing the acquisition sequence.
*  
*  This is the server.  It executes the data acquisition sequence 
*  on its own node.   Then it sends a signal back to the master to 
*  inform it that the acquisition has completed.
*
*  This is modeled after client-server operation outlined in 
*  Advanced Linux Programming by CodeSourcery LLC, published by 
*  New Riders Publishing.
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
	socket_handle = socket (PF_INET, SOCK_STREAM, 0); // address domain, type, protocol
                                                      // types are basically TCP (STREAM) an UDP (DGRAM)
	if (socket_handle == -1) {
		perror("socket");
		exit(EXIT_FAILURE);
	}

	socket_address.s_addr = htonl(INADDR_ANY); //bind to the local address

	// build the daq_service address information 
	memset (&daq_service, 0, sizeof (daq_service));
	daq_service.sin_family = AF_INET;  // indicate that this is an Internet namespace address
	daq_service.sin_port = htons(port); // convert port number to network byte order (see ip man page)
	daq_service.sin_addr = socket_address; // internet address as a 32-bit IP number

	/* Bind the socket to that address. */
	if ((bind (socket_handle, (const sockaddr*)&daq_service, sizeof (daq_service)))) {
		perror ("bind");
		exit(EXIT_FAILURE);
	}

	return 0; //success
}


/* Write setup information to the command line - this starts a run */
int launch_minervadaq() {
	stringstream process_gates, rmode, runn, subr, dtctr;
	process_gates << gates[0];
	rmode         << runMode[0];
	runn          << runNum[0];
	subr          << subNum[0];
        dtctr         << detect[0];
	string command = "$DAQROOT/bin/minervadaq -et " + string(et_file) + " " +
		"-g " + process_gates.str() + " " + 
		"-r " + runn.str() + " " + 
		"-s " + subr.str() + " " +  
		"-m " + rmode.str() + " " + 
		"-d " + dtctr.str() + " " + 
		"> log_file";
	cout << "launch_minervadaq command: " << command << endl;
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
		struct sockaddr_in remote_address; // internet socket address, contains machine and port number
		socklen_t address_length;
		int master_connection, minervadaq_connection; // file descriptors ("handles")
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
#if DEBUG_GENERAL
	cout << " daq_server::read_setup_data() sizeof(gates): " << sizeof(gates) << endl;
#endif
	/********************************************************************************/
	// Read the number of gates to process.
	if ((read(master_connection,gates,sizeof(gates)))!=sizeof(gates)) { 
		perror("server read error: gates"); 
		exit(EXIT_FAILURE);
	}
	cout << " Number of Gates        : " << gates[0] << endl;
	
	/********************************************************************************/
	// Read the run mode.
	if ((read(master_connection,runMode,sizeof(runMode)))!=sizeof(runMode)) { 
		perror("server read error: run mode"); 
		exit(EXIT_FAILURE);
	}
	cout << " Running Mode (encoded) : " << runMode[0] << endl;

	/********************************************************************************/
	// Read the run number.
	if ((read(master_connection,runNum,sizeof(runNum)))!=sizeof(runNum)) { 
		perror("server read error: run number"); 
		exit(EXIT_FAILURE);
	}
	cout << " Run Number             : " << runNum[0] << endl;

	/********************************************************************************/
	// Read the subrun number.
	if ((read(master_connection,subNum,sizeof(subNum)))!=sizeof(subNum)) { 
		perror("server read error: subrun number"); 
		exit(EXIT_FAILURE);
	}
	cout << " Subrun Number          : " << subNum[0] << endl;

	/********************************************************************************/
	// Read the detector type.
	if ((read(master_connection,detect,sizeof(detect)))!=sizeof(detect)) { 
		perror("server read error: detector type"); 
		exit(EXIT_FAILURE);
	}
	cout << " Detector Type (encoded): " << detect[0] << endl;

	/********************************************************************************/
	// Read the ET filename for data storagea
	if ((read(master_connection,et_file,sizeof(et_file)))!=sizeof(et_file)) {  
		perror("server read error: et_file"); 
		exit(EXIT_FAILURE);
	}
	cout << " Name of ET file        : " << et_file << endl;

	/********************************************************************************/
	// Read "done" from the master.
	if ((read (master_connection, done, sizeof (done)))!=sizeof(done)) { 
		perror("server read error: done"); 
		exit(EXIT_FAILURE);
	}
	cout << " Are we done (finished argument parsing)? " << done[0] << endl;

	return 0;
}


int write_server_response(int connection) {
	done[0] = true;
	write(connection,done,1); //we're done!
	return 0;
}

