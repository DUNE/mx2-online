#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <cerrno>
#include <cassert>

#include "daq_master.h"
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

// log4cpp Variables - Needed throughout the daq_master functions.
log4cpp::Appender* masterAppender;
log4cpp::Category& root   = log4cpp::Category::getRoot();
log4cpp::Category& master = log4cpp::Category::getInstance(std::string("master"));
                   
using namespace std;

int main(int argc, char* argv[]) {

	// Initialize run parameters for MINERvA DAQ.
	for (int i = 0; i < daq_slaves; i++) {
		gates[i]    = 10;  // Run length in gates
		runMode[i]  = 0;   // Running Mode (0==OneShot, etc.)
		runNum[i]    = 938; // Run number
		subNum[i]    = 11;  // Subrun number
		detect[i]    = 0;   // Default to UnknownDetector
		totSec[i]    = 117; // Random default.
		detConf[i]   = 8;   // Detector config - basically , number of FEB's.
		ledLevel[i]  = 0;   // Default to Zero PE (only for Header, not used)
		ledGroup[i]  = 8;   // Default to LEDALL (only for Header, not used)
		initLevel[i] = 1;   // Default to "init". 
	}
	sprintf(conf_file,"unknown");
	sprintf(et_file,"testme");	

	char log_filename[100];
	struct timeval hpnow; gettimeofday(&hpnow,NULL);
	sprintf(log_filename,"/work/data/logs/daq_master%d.txt",(int)hpnow.tv_sec);

        // Process the command line argument set.  
        int optind = 1;
        cout << "\n\nArguments to DAQ Master: " << endl;
        while ((optind < argc) && (argv[optind][0]=='-')) {
                string sw = argv[optind];
                if (sw=="-r") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) runNum[i] = atoi(argv[optind]);
                        cout << "\tRun Number                  = " << runNum[0] << endl;
                }
                else if (sw=="-s") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) subNum[i] = atoi(argv[optind]);
                        cout << "\tSubrun Number               = " << subNum[0] << endl;
                }
                else if (sw=="-g") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) gates[i] = atoi(argv[optind]);
                        cout << "\tTotal Gates                 = " << gates[0] << endl;
                }
		else if (sw=="-t") {
			optind++;
                        for (int i=0;i<daq_slaves;i++) totSec[i] = atoi(argv[optind]);
			cout << "\tTotal Seconds (ignored)     = " << totSec[0] << endl;
		}
                else if (sw=="-m") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) runMode[i] = atoi(argv[optind]);
                        cout << "\tRunning Mode (encoded)      = " << runMode[0] << endl;
                }
                else if (sw=="-d") {
                        optind++;
                        for (int i=0;i<daq_slaves;i++) detect[i] = atoi(argv[optind]);
                        cout << "\tDetector (encoded)          = " << detect[0] << endl;
                }
                else if (sw=="-et") {
                        optind++;
			sprintf(et_file,argv[optind]);
                        cout << "\tFileroot (ET, SAM, logging) = " << et_file << endl;
                }
		else if (sw=="-cf") {
			optind++;
			sprintf(conf_file,argv[optind]);
			cout << "\tHardware Config Filename    = " << conf_file << endl;
		}
		else if (sw=="-dc") {
			optind++;
			for (int i=0;i<daq_slaves;i++) detConf[i] = atoi(argv[optind]);
			cout << "\tDetector Config. Code       = " << detConf[0] << endl;
		}
		else if (sw=="-ll") {
			optind++;
			for (int i=0;i<daq_slaves;i++) ledLevel[i] = atoi(argv[optind]);
			cout << "\tLED Level (encoded)         = " << ledLevel[0] << endl;
		}
		else if (sw=="-lg") {
			optind++;
			for (int i=0;i<daq_slaves;i++) ledGroup[i] = atoi(argv[optind]);
			cout << "\tLED Group (encoded)         = " << ledGroup[0] << endl;
		}
		else if (sw=="-hw") {
			optind++;
			for (int i=0;i<daq_slaves;i++) initLevel[i] = atoi(argv[optind]);
			cout << "\tVME Card Init. Level        = " << initLevel[0] << endl;
		}
		else if (sw=="-p") {
			optind++;
			for (int i=0;i<daq_slaves;i++) netPort[i] = atoi(argv[optind]);
			cout << "\tET System Port              = " << netPort[0] << endl;
		}
                else
                        cout << "Unknown switch: " << argv[optind] << endl;
                optind++;
        }
        cout << endl;

	masterAppender = new log4cpp::FileAppender("default", log_filename);
	masterAppender->setLayout(new log4cpp::BasicLayout());
	root.addAppender(masterAppender);
	root.setPriority(log4cpp::Priority::DEBUG);
	master.setPriority(log4cpp::Priority::DEBUG);
	root.infoStream()   << "Starting DAQ Master. ";
	master.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";
	master.infoStream() << "Arguments to DAQ Master: ";
	master.infoStream() << "(Arguments passed to MINERvA DAQ.) ";
	master.infoStream() << "  Run Number             = " << runNum[0];
	master.infoStream() << "  Subrun Number          = " << subNum[0];
	master.infoStream() << "  Total Gates            = " << gates[0];
	master.infoStream() << "  Running Mode (encoded) = " << runMode[0];
	master.infoStream() << "  Detector (encoded)     = " << detect[0];
	master.infoStream() << "  DetectorConfiguration  = " << detConf[0];
	master.infoStream() << "  LED Level (encoded)    = " << ledLevel[0];
	master.infoStream() << "  LED Group (encoded)    = " << ledGroup[0];
	master.infoStream() << "  ET Filename            = " << et_file;
	master.infoStream() << "  Configuration File     = " << conf_file;
	master.infoStream() << "  VME Card Init. Level   = " << initLevel[0];
	master.infoStream() << "  ET System Port         = " << netPort[0];
	master.infoStream() << "See Event/MinervaEvent/xml/DAQHeader.xml for codes.";
	master.infoStream() << "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~";

	make_socket(); //make up the communication socket

	/* Connect to the DAQ Server server */
	for (int i = 0; i < daq_slaves; i++) {
		if (connect (socket_handle[i], (struct sockaddr*) &daq_client[i], sizeof (struct sockaddr_in)) == -1) {
			perror ("connect");
			return 1;
		}
	}

	cout << "Writing data to socket..." << endl;
	master.infoStream() << "Writing data to socket...";
	write_setup_data();     //write setup data to the "slave" 
	cout << "Reading server response..." << endl;
	master.infoStream() << "Reading server response...";
	read_server_response(); //read the "slave" response

	master.infoStream() << "Exiting.";
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
	cout << "Success, made the soldier socket!" << endl;
	master.infoStream() << "Success, made the soldier socket!";
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
	cout << "Success, made the worker socket!" << endl;
	master.infoStream() << "Success, made the worker socket!";
	/*********************************************************************************/
	return 0;
}

int write_setup_data() {
	master.infoStream() << "Writing setup date to slave nodes.";
	for (int i=0;i<daq_slaves;i++) {
		done[i] = false; //we are not yet ready to stop the DAQ

		cout << " daq_master::write_setup_data() socket_handle: " << socket_handle[i] << endl;
		// daq_server expects the data to come in a very specific order!
		write( socket_handle[i], &gates[i],     sizeof(gates[i])); 
		write( socket_handle[i], &runMode[i],   sizeof(runMode[i])); 
		write( socket_handle[i], &runNum[i],    sizeof(runNum[i])); 
		write( socket_handle[i], &subNum[i],    sizeof(subNum[i])); 
		write( socket_handle[i], &detect[i],    sizeof(detect[i])); 
		write( socket_handle[i], &totSec[i],    sizeof(totSec[i])); 
		write( socket_handle[i], conf_file,     sizeof(conf_file));
		write( socket_handle[i], &detConf[i],   sizeof(detConf[i])); 
		write( socket_handle[i], &ledLevel[i],  sizeof(ledLevel[i])); 
		write( socket_handle[i], &ledGroup[i],  sizeof(ledGroup[i])); 
		write( socket_handle[i], &initLevel[i], sizeof(initLevel[i])); 
		write( socket_handle[i], &netPort[i],   sizeof(netPort[i])); 
		write( socket_handle[i], et_file,       sizeof(et_file));
		write( socket_handle[i], &done[i], 1);  //send the status
	}
	master.infoStream() << "Finished writing setup date to slave nodes.";
	return 0;
}

int read_server_response() {
	for (int i=0;i<daq_slaves;i++) {
		read(socket_handle[i], &done[i], 1); //read back the status
		cout << " daq_master::read_server_response() done? " << done[0] << endl;  
		master.infoStream() << " daq_master::read_server_response() done? " << done[0];  
	}
	return 0;
}
