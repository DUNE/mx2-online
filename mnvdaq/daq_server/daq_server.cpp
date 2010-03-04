#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <cerrno>

#include "daq_server.h"
// log4cpp Headers
#include "log4cpp/Portability.hh"
#include "log4cpp/Category.hh"
#include "log4cpp/Appender.hh"
#include "log4cpp/FileAppender.hh"
#include "log4cpp/OstreamAppender.hh"
#include "log4cpp/SyslogAppender.hh"
#include "log4cpp/Layout.hh"
#include "log4cpp/BasicLayout.hh"
#include "log4cpp/Priority.hh"
#include "log4cpp/NDC.hh"

#include <ctime>
#include <sys/time.h>

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

// log4cpp Variables - Needed throughout the daq_server functions.
log4cpp::Appender* serverAppender;
log4cpp::Category& root      = log4cpp::Category::getRoot();
log4cpp::Category& slavenode = log4cpp::Category::getInstance(std::string("slavenode"));

using namespace std;

int main() {
	
	char log_filename[100];
	struct timeval hpnow; gettimeofday(&hpnow,NULL);
	sprintf(log_filename,"/work/data/logs/daq_server%d.txt",(int)hpnow.tv_sec);

	serverAppender = new log4cpp::FileAppender("default", log_filename);
	serverAppender->setLayout(new log4cpp::BasicLayout());
	root.addAppender(serverAppender);
	root.setPriority(log4cpp::Priority::DEBUG);
	slavenode.setPriority(log4cpp::Priority::DEBUG);	
	root.infoStream()   << "Starting DAQ Server. ";

	done[0] = false; // Set the loop flag.
	slavenode.infoStream() << " Launching server process, waiting for connection...";
	server();        // Run the server.  

	slavenode.infoStream() << "Exiting.";
	return 0;        // Success!
}


int make_socket() {

	/* create a TCP socket */
	socket_handle = socket (PF_INET, SOCK_STREAM, 0); // address domain, type, protocol
                                                      // types are basically TCP (STREAM) an UDP (DGRAM)
	if (socket_handle == -1) {
		slavenode.fatalStream() << "Error creating socket handle in daq_server::make_socket()!";
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
		slavenode.fatalStream() << "Error binding to socket address in daq_server::make_socket()!";
		perror ("bind");
		exit(EXIT_FAILURE);
	}
	slavenode.infoStream() << "Successfully made socket with handle " << socket_handle;

	return 0; //success
}


/* Write setup information to the command line - this starts a run */
int launch_minervadaq() {
	stringstream process_gates, rmode, runn, subr, dtctr, totsec, detconf, 
		ledlevel, ledgroup, initlevel;
	process_gates << gates[0];
	rmode         << runMode[0];
	runn          << runNum[0];
	subr          << subNum[0];
        dtctr         << detect[0];
	totsec        << totSec[0];
	detconf       << detConf[0];
	ledlevel      << ledLevel[0];
	ledgroup      << ledGroup[0];
	initlevel     << initLevel[0];
	string command = "$DAQROOT/bin/minervadaq -et " + string(et_file) + " " +
		"-g " + process_gates.str() + " " + 
		"-m " + rmode.str() + " " + 
		"-r " + runn.str() + " " + 
		"-s " + subr.str() + " " +  
		"-d " + dtctr.str() + " " + 
		"-t " + totsec.str() + " " + 
		"-cf " + string(conf_file) + " " +
		"-dc " + detconf.str() + " " + 
		"-ll " + ledlevel.str() + " " + 
		"-lg " + ledgroup.str() + " " + 
		"-hw " + initlevel.str(); 
		// + " " + "> /work/data/logs/minervadaq_log.txt";
	cout << "launch_minervadaq command: " << command << endl;
	slavenode.infoStream() << "launch_minervadaq command: " << command;
	if ((system(command.c_str())!=-1)) {
		slavenode.fatalStream() << "Error in daq_server::launch_minervadaq()!  run_minervadaq failed!";
		perror("run_minervadaq failed");
		exit(EXIT_FAILURE);
	}
	return 0; //success
}


int server() {
	/* first make the socket */
	if (make_socket()) {
		slavenode.fatalStream() << "Error in daq_server::server()!  Failed to make the socket!";
		perror("make_socket"); 
		exit(EXIT_FAILURE);
	}
	/* Listen on our new socket for connections */
	if (listen (socket_handle, 10)) {
		slavenode.fatalStream() << "Error in daq_server::server()!  Listener failed!";
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
			slavenode.fatalStream() << "Error in daq_server::server()!  launch_minervadaq() failed!";
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

	slavenode.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
	slavenode.infoStream() << "Setup Data: ";

	/********************************************************************************/
	// Read the number of gates to process.
	if ((read(master_connection,gates,sizeof(gates)))!=sizeof(gates)) { 
		perror("server read error: gates"); 
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing gates data!";
		exit(EXIT_FAILURE);
	}
	cout << " Number of Gates        : " << gates[0] << endl;
	
	/********************************************************************************/
	// Read the run mode.
	if ((read(master_connection,runMode,sizeof(runMode)))!=sizeof(runMode)) { 
		perror("server read error: run mode"); 
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing run mode data!";
		exit(EXIT_FAILURE);
	}
	cout << " Running Mode (encoded) : " << runMode[0] << endl;

	/********************************************************************************/
	// Read the run number.
	if ((read(master_connection,runNum,sizeof(runNum)))!=sizeof(runNum)) { 
		perror("server read error: run number"); 
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing run number data!";
		exit(EXIT_FAILURE);
	}
	cout << " Run Number             : " << runNum[0] << endl;

	/********************************************************************************/
	// Read the subrun number.
	if ((read(master_connection,subNum,sizeof(subNum)))!=sizeof(subNum)) { 
		perror("server read error: subrun number"); 
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing subrun number data!";
		exit(EXIT_FAILURE);
	}
	cout << " Subrun Number          : " << subNum[0] << endl;

	/********************************************************************************/
	// Read the detector type.
	if ((read(master_connection,detect,sizeof(detect)))!=sizeof(detect)) { 
		perror("server read error: detector type"); 
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing detector type data!";
		exit(EXIT_FAILURE);
	}
	cout << " Detector Type (encoded): " << detect[0] << endl;

	/********************************************************************************/
	// Read the run length in seconds (ignored by the DAQ)
	if ((read(master_connection,totSec,sizeof(totSec)))!=sizeof(totSec)) {
		perror("server read error: run time length");
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing run length data!";
		exit(EXIT_FAILURE);
	}
	cout << " Run Length (seconds)   : " << totSec[0] << endl;

	/********************************************************************************/
	// Read the name of the slow control config file
	if ((read(master_connection,conf_file,sizeof(conf_file)))!=sizeof(conf_file)) {
		perror("server read error: conf_file");
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing configuration file data!";
		exit(EXIT_FAILURE);
	}
	cout << " Name of config file    : " << conf_file << endl;

	/********************************************************************************/
	// Read the detector config (# of FEB's)
	if ((read(master_connection,detConf,sizeof(detConf)))!=sizeof(detConf)) {
		perror("server read error: detector config");
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing detector configuration data!";
		exit(EXIT_FAILURE);
	}
	cout << " Detector Config (#FEBs): " << detConf[0] << endl;

	/********************************************************************************/
	// Read the LED level
	if ((read(master_connection,ledLevel,sizeof(ledLevel)))!=sizeof(ledLevel)) {
		perror("server read error: LED Level");
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing LED level data!";
		exit(EXIT_FAILURE);
	}
	cout << " LED Level (encoded)    : " << ledLevel[0] << endl;

	/********************************************************************************/
	// Read the LED group
	if ((read(master_connection,ledGroup,sizeof(ledGroup)))!=sizeof(ledGroup)) {
		perror("server read error: LED Group");
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing LED group data!";
		exit(EXIT_FAILURE);
	}
	cout << " LED Group (encoded)    : " << ledGroup[0] << endl;

	/********************************************************************************/
	// Read the HW init level
	if ((read(master_connection,initLevel,sizeof(initLevel)))!=sizeof(initLevel)) {
		perror("server read error: VME Card Init. Level");
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing HW init. level data!";
		exit(EXIT_FAILURE);
	}
	cout << " VME Card Init. Level   : " << initLevel[0] << endl;

	/********************************************************************************/
	// Read the ET filename for data storagea
	if ((read(master_connection,et_file,sizeof(et_file)))!=sizeof(et_file)) {  
		perror("server read error: et_file"); 
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing ET fileroot data!";
		exit(EXIT_FAILURE);
	}
	cout << " Name of ET file        : " << et_file << endl;

	/********************************************************************************/
	// Read "done" from the master.
	if ((read (master_connection, done, sizeof (done)))!=sizeof(done)) { 
		perror("server read error: done"); 
		slavenode.fatalStream() << "Error in daq_server::read_setup_data() parsing message done signal!";
		exit(EXIT_FAILURE);
	}
	cout << " Are we done (finished argument parsing)? " << done[0] << endl;

	slavenode.infoStream() << " Run Number             : " << runNum[0];
	slavenode.infoStream() << " Subrun Number          : " << subNum[0];
	slavenode.infoStream() << " Number of Gates        : " << gates[0];
	slavenode.infoStream() << " Run Length (seconds)   : " << totSec[0];
	slavenode.infoStream() << " Running Mode (encoded) : " << runMode[0];
	slavenode.infoStream() << " Detector Type (encoded): " << detect[0];
	slavenode.infoStream() << " Detector Config (#FEBs): " << detConf[0];
	slavenode.infoStream() << " LED Level (encoded)    : " << ledLevel[0];
	slavenode.infoStream() << " LED Group (encoded)    : " << ledGroup[0];
	slavenode.infoStream() << " Name of ET file        : " << et_file;
	slavenode.infoStream() << " Name of config file    : " << conf_file;
	slavenode.infoStream() << " VME Card Init. Level   : " << initLevel[0];
	slavenode.infoStream() << "See Event/MinervaEvent/xml/DAQHeader.xml for codes.";
	slavenode.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";

	return 0;
}


int write_server_response(int connection) {
	done[0] = true;
	write(connection,done,1); //we're done!
	slavenode.infoStream() << "Writing server response - done!";
	return 0;
}

