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

	// Initialize run parameters for MINERvA DAQ.
	for (int i = 0; i < 2; i++) {
		gates[i]   = 10;   // Run length in gates
		runMode[i] = 0;    // Running Mode (0==OneShot, etc.)
		runNum[i]  = 938;  // Run number
		subNum[i]  = 11;   // Subrun number
		detect[i]  = 0;    // Default to UnknownDetector
		sprintf(et_file,"testme");	
	}
        // Process the command line argument set.  
        // TODO - Be sure the command arg set for daq_master is up to date.
        int optind = 1;
        cout << "\n\nArguments to MINERvA DAQ: " << endl;
        while ((optind < argc) && (argv[optind][0]=='-')) {
                string sw = argv[optind];
                if (sw=="-r") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) runNum[i] = atoi(argv[optind]);
                        cout << "\tRun Number             = " << runNum[0] << endl;
                }
                else if (sw=="-s") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) subNum[i] = atoi(argv[optind]);
                        cout << "\tSubrun Number          = " << subNum[0] << endl;
                }
                else if (sw=="-g") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) gates[i] = atoi(argv[optind]);
                        cout << "\tTotal Gates            = " << gates[0] << endl;
                }
                else if (sw=="-m") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) runMode[i] = atoi(argv[optind]);
                        cout << "\tRunning Mode (encoded) = " << runMode[0] << endl;
                }
                else if (sw=="-d") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) detect[i] = atoi(argv[optind]);
                        cout << "\tDetector (encoded)     = " << detect[0] << endl;
                }
                else if (sw=="-et") {
                        optind++;
			sprintf(et_file,argv[optind]);	
                        cout << "\tET Filename            = " << et_file << endl;
                }
                else
                        cout << "Unknown switch: " << argv[optind] << endl;
                optind++;
        }
        cout << endl;

	make_socket(); //make up the communication socket

	/* Connect to the DAQ Server server */
	for (int i=0;i<daq_slaves;i++) {
		if (connect (socket_handle[i], (struct sockaddr*) &daq_client[i], sizeof (struct sockaddr_in)) == -1) {
			perror ("connect");
			return 1;
		}
	}

	cout << "writing data to socket..." << endl;
	write_setup_data(); //write setup data to the "slave" 

	read_server_response(); //read the "slave" response
	return 0;
}

int make_socket() {
	/*********************************************************************************/
	/* Create the socket for mnvonline0 (the "soldier" node). */
	socket_handle[0] = socket (PF_INET, SOCK_STREAM, 0);
	/* Store the server’s name in the socket address. */
	daq_client[0].sin_family = AF_INET;
	/* Convert from strings to numbers. */
	string hostname="mnvonline0.fnal.gov"; //this needs to be changed for the appropriate machine
	hostinfo = gethostbyname(hostname.c_str()); // we'd like to do this with ip's directly eventually...
	if (hostinfo == NULL) return 1;
	else daq_client[0].sin_addr = *((struct in_addr *) hostinfo->h_addr);
	daq_client[0].sin_port = htons (port);
	cout<<"success, made the client socket"<<endl;
	/*********************************************************************************/

	/*********************************************************************************/
	/* Create the socket for mnvonline1 (the "worker" node). */
	socket_handle[1] = socket (PF_INET, SOCK_STREAM, 0);
	/* Store the server’s name in the socket address. */
	daq_client[1].sin_family = AF_INET;
	/* Convert from strings to numbers. */
	hostname="mnvonline1.fnal.gov"; //this needs to be changed for the appropriate machine
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

		cout << " daq_master::write_setup_data() socket_handle: " << socket_handle[i] << endl;
		// daq_server expects the data to come in a very specific order!
		write( socket_handle[i], &gates[i],   sizeof(gates[i])); 
		write( socket_handle[i], &runMode[i], sizeof(runMode[i])); 
		write( socket_handle[i], &runNum[i],  sizeof(runNum[i])); 
		write( socket_handle[i], &subNum[i],  sizeof(subNum[i])); 
		write( socket_handle[i], &detect[i],  sizeof(detect[i])); 
		write( socket_handle[i], et_file,     sizeof(et_file));
		write( socket_handle[i], &done[i], 1);  //send the status
	}
	return 0;
}

int read_server_response() {
	for (int i=0;i<daq_slaves;i++) {
		read(socket_handle[i], &done[i], 1); //read back the status
		cout << " daq_master::read_server_response() done? " << done[0] << endl;  
	}
	return 0;
}
