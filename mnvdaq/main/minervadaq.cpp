/*! \file minervadaq.cpp
 * \brief  Main routine: minervadaq for acquiring data from the MINERvA detector. 
 *
 * Elaine Schulte
 * Rutgers University
 * August 4, 2009 
 *
 * 
 */

#include "acquire_data.h"
#include "eb_service.h"
#include "MinervaEvent.h"
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>

#include <boost/ref.hpp>
#include <boost/thread/mutex.hpp>
#include <ctime>
#include <sys/time.h>

#define THREAD_COUNT 4  /*!< a thread count variable if we aren't finding the number of threads needed any other way */
#if MASTER||SINGLE_PC
#define CONTROLLER_ID 0
#elif (!MASTER)&&(!SINGLE_PC)
#define CONTROLLER_ID 1
#endif

#include "minervadaq.h"

/*! The main routine which executes the data acquisition sequences for minervadaq. */

using namespace std;

int main(int argc, char *argv[]) 
{

	/****************************************************************************
	some loging files for the main routine                               
	***************************************************************************/
	string et_filename;
	ofstream gate_time_log;
	ofstream thread_launch_log;
	ofstream thread_return_log;
	thread_launch_log.open("thread_launch_log.csv");
	thread_return_log.open("thread_return_log.csv");
	gate_time_log.open("gate_time_log.csv");
	take_data_extime_log.open("take_data_extime_log.csv");

#if TIME_ME
	/********************************************************************************
	*   For Benchmark Execution Timing                                              
	*********************************************************************************/
	struct timeval start_time, stop_time;
	gettimeofday(&start_time, NULL);
#endif

	/*********************************************************************************/
	/*   An event_handler structure object for building event data blocks.           */
	/*********************************************************************************/
	event_handler event_data;
	evt_record_available = true;

	/*********************************************************************************/
	/*      Initialize some execution status variables                               */
	/*********************************************************************************/
	bool success = false; //initialize the success state of the DAQ on exit
	int record_gates = -1;

	/*********************************************************************************/
	/*  Make sure that an output filename and a number of events to record           */
	/*  were given on the command line.                                              */
	/*                                                                               */
	/*  If they were not, then ask the user to input them now.                       */
	/*********************************************************************************/
	if (argc!=3) {
		cout<<"You forgot to give me the number of gates you want recorded! No "<<endl;
		cout<<"matter how hard I try, I can't record any data if you don't tell "<<endl;
		cout<<"me how many gates you want!"<<endl;
		cout<<"Now GIVE ME A NUMBER OF GATES!"<<endl;
		cin>>record_gates;
		cout<<"And the file name..."<<endl;
		cin>>et_filename;
	} else {
		record_gates = atoi(argv[2]);
		et_filename.assign(argv[1]);
	}

	/*********************************************************************************/
	/* now set up ET for use in writing the first-pass memory mapped data file       */
	/* Setting up ET for use in remote mode for multi-PC operation                   */
	/*********************************************************************************/
	et_att_id  attach;
	et_sys_id  sys_id;
	et_id      *id;
	et_openconfig   openconfig;

	/* configuring the ET system is the first thing we must do */
	et_open_config_init(&openconfig);

#if MULTI_PC
	/* set remote host */
	et_open_config_setmode(openconfig, ET_HOST_AS_REMOTE); // remote only?

	/* set this ET client for remote */
	et_open_config_sethost(openconfig, "minervatest01.fnal.gov");  // remote only?
	// Set to the current host machine name. 
	// Currently (2009.November.26), setting IP addresses explicitly doesn't work quite right.

	/* set direct connection */
	et_open_config_setcast(openconfig, ET_DIRECT);  // remote only?

	/* set the server port */
	et_open_config_setserverport(openconfig, 1091); // multi-pc only?
#endif

	/* then we must open it */
	if (et_open(&sys_id, et_filename.c_str(), openconfig) != ET_OK) {
		printf("et_producer: et_open problems\n");
		exit(1);
	}

	/* clean up after yourself */
	et_open_config_destroy(openconfig);

	/* set the level of debug output that we want (everything) */
	et_system_setdebug(sys_id, ET_DEBUG_INFO);

	// This only works for local operation, not over the network for some reason!
	// Leave this commented out when working on networked running.  It can be 
	// commented back in for local running.  Overall, should be debugged...
	//------
#if SINGLE_PC
	// Set up the heartbeat to make sure ET starts correctly.
	unsigned int oldheartbeat, newheartbeat;
	id = (et_id *) sys_id;
	oldheartbeat = id->sys->heartbeat;
	int counter = 0; 
	do {
		system("sleep 1s");
		if (!counter) {
			newheartbeat = id->sys->heartbeat;
		} else {
			oldheartbeat=newheartbeat;
			newheartbeat = id->sys->heartbeat;
		}
		counter++;
	} while ((newheartbeat==oldheartbeat)&&(counter!=50)); 
	// Notify the user if ET did not start properly & exit.
	if (counter==50) {
		std::cout<<"ET System did not start properly!"<<std::endl;
		exit(-5);
	}   
#endif 
	//------

	/* attach to GRANDCENTRAL station since we are producing events */
	if (et_station_attach(sys_id, ET_GRANDCENTRAL, &attach) < 0) {
		printf("et_producer: error in station attach\n");
		system("sleep 10s");
		exit(1);
	} 

	/*********************************************************************************/
	/*  Now we need to synch up the "master" and "slave" DAQ's                       */
	/*********************************************************************************/
#if MASTER&&(!SINGLE_PC)
// #if MASTER
	/* create a TCP socket */
	socket_handle = socket (PF_INET, SOCK_STREAM, 0);
	std::cout<<"socket_handle: "<<socket_handle<<std::endl;
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
	if (listen (socket_handle, 10)) {
		perror("listen");
		exit(EXIT_FAILURE);
	}
#endif
// endif MASTER&&(!SINGLE_PC)

#if (!MASTER)&&(!SINGLE_PC)
	socket_handle = socket (PF_INET, SOCK_STREAM, 0);
	/* Store the server’s name in the socket address. */
	daq_service.sin_family = AF_INET;
	/* Convert from strings to numbers. */
	string hostname="minervatest03.fnal.gov"; //this needs to be changed for the appropriate machine
	// should point from worker to soldier node
	hostinfo = gethostbyname(hostname.c_str());
	if (hostinfo == NULL) return 1;
	else daq_service.sin_addr = *((struct in_addr *) hostinfo->h_addr);
	daq_service.sin_port = htons (port);
	if (connect(socket_handle, (struct sockaddr*) &daq_service, sizeof (struct sockaddr_in)) == -1) {
		perror ("connect");
		exit(EXIT_FAILURE) ;
	}
#endif
// endif (!MASTER)&&(!SINGLE_PC)


	/*********************************************************************************/
	/*   Make an acquire data object which contains the functions for                */
	/*   performing initialization and the acquisition sequence                      */
	/*********************************************************************************/
	acquire_data *daq = new acquire_data(et_filename); //get functions that manipulate data to & from electronics

	/*********************************************************************************/
	/*      Now initialize the DAQ electronics                                       */
	/*********************************************************************************/
#if THREAD_ME
	boost::thread electronics_init_thread(boost::bind(&acquire_data::InitializeDaq,daq)); //initialize the electronics
#else
	daq->InitializeDaq(CONTROLLER_ID);
#endif
// endif THREAD_ME

	/*********************************************************************************/
	/*  while the electronics are being initialized, we can get                      */
	/*       the event builder ready.                                                */
	/*                                                                               */
	/*  first thing's first:  Read in the event status file which contains things    */
	/*  like the global event number and run number to be used                       */
	/*********************************************************************************/
	ifstream run_status("run_status.dat");
	try {
		if (!run_status) throw (!run_status);
		run_status>>event_data.gate_info[0]>>event_data.run_info[2]>>event_data.run_info[3];
		event_data.run_info[0]=event_data.run_info[1]=event_data.run_info[4]=0;
	} catch (bool e) {
		cout<<"Error opening run_status.dat.  "<<endl;
		cout<<"You know, the one that tells me what the run number is!"<<endl;
		exit(-2000);
	}

	/*********************************************************************************/
	/*  now that we know the run number and global event number                      */
	/*  we can set about starting up an event builder.                               */
	/*********************************************************************************/
#if THREAD_ME
	electronics_init_thread.join(); //wait for the electronics initialization to finish 
#endif

	/*********************************************************************************/
	/*  for now we need to set the HV & a few other FEB settings here.  Ultimately,  */
	/*  these settings would be kept in a setup file and set using slow controls,    */
	/*  but I have neither the setup file nor the slow controls                      */
	/*********************************************************************************/
	controller *currentController = daq->GetController(); //get the controller object

	/*********************************************************************************/
	/*  Now, if we're going to set the high voltage using the main routine           */
	/*  we will let it tell us how many threads, if multi-threaded operation,        */
	/*  we will need to execute.  We will also set & monitor the high voltage        */
	/*  setting procedure here.                                                      */
	/*********************************************************************************/
#if DAQ_SET_HV&&THREAD_ME
#if DEBUG_THREAD
	cout<<"starting to set HV via threads"<<endl;
#endif
	/* make up enough threads to survice all of the croc channels on this controller */
	boost::thread *setup_threads[(currentController->GetCrocVectorLength()*4)]; 
	int thread_count=0;
	/*set the high voltage*/
	for (int i=1;i<=currentController->GetCrocVectorLength();i++) { //crocs start with 1
		croc *tmpCroc = currentController->GetCroc(i);
#if DEBUG_THREAD
		cout<<"got the croc!"<<endl;
#endif
		for (int j=0;j<4;j++) {
			if ((tmpCroc->GetChannelAvailable(j))&&(tmpCroc->GetChannel(j)->GetHasFebs())) {
#if DEBUG_TRHEAD
				cout<<"Launching thread on channel: "<<j<<endl;
#endif
				setup_threads[thread_count] = new boost::thread(boost::bind(&SetHV,boost::ref(daq),i,j));
				thread_count++; //figure out how many threads we actually need to service
			} 
		} 
	} 

	/*wait for the HV to finish setting*/
	for (int i=0;i<thread_count;i++) {
		setup_threads[i]->join();
	}   
#endif
// endif DAQ_SET_HV&&THREAD_ME

	/*********************************************************************************/
	/*       Monitor the high voltage setting                                        */
	/*********************************************************************************/
#if DAQ_SET_HV&&NO_THREAD
	for (int i=1;i<=currentController->GetCrocVectorLength();i++) { //crocs start with 1
		croc *tmpCroc = currentController->GetCroc(i);
		cout<<"got the croc!"<<endl;
		for (int j=0;j<4;j++) {
			if ((tmpCroc->GetChannelAvailable(j))&&(tmpCroc->GetChannel(j)->GetHasFebs())) {
				SetHV(daq,i,j);
			} 
		} 
	} 
#endif

	/*********************************************************************************/
	/*  At this point we are now set up and are ready to start the event acquiring   */
	/*  procedures.                                                                  */
	/*********************************************************************************/
#if DEBUG_ME
	cout<<"Getting ready to start taking data!"<<endl;
#endif

	/*********************************************************************************/
	/*   Make up the data-taking threads if in multi-threaded operation              */
	/*********************************************************************************/
#if THREAD_ME
	// int thread_count = THREAD_COUNT;
	boost::thread *data_threads[thread_count];
#endif

#if TAKE_DATA
#if DEBUG_ME
	cout<<"record gates: "<<record_gates<<endl;
#endif

	/*********************************************************************************/
	/*      The top of the Event Loop.  Events here are referred to as GATES.        */
	/*********************************************************************************/
	for (int gate=1;gate<=record_gates;gate++) {
#if TIME_ME
		struct timeval gate_start_time, gate_stop_time;
		gettimeofday(&gate_start_time, NULL);
#endif
#if DEBUG_ME
		cout<<"Got the gate: "<<gate<<endl;
#endif
#if RECORD_EVENT
		if (!(gate%100)) {
			cout<<"********************************************************************************"<<endl;
			cout<<"Acquiring Gate: "<<gate<<endl;
		}
#endif
		/**********************************************************************************/
		/*  Initialize the following data members of the event_handler structure          */
		/*    event_data:                                                                 */
		/*       event_data.gate_info[1]  the local gate number                           */
		/*       event_data.gate_info[2]  trig_time                                       */
		/*       event_data.gate_info[3]  error                                           */
		/*       event_data.gate_info[4]  minos                                           */
		/*       event_data.feb_info[0-9] 0: link_no, 1: crate_no, 2: croc_no,            */
		/*                                  3: chan_no, 4: bank 5: buffer length          */
		/*                                  6: feb number, 7: feb firmware, 8: hits       */
		/**********************************************************************************/
		event_data.gate_info[1]=gate; //record gate number
		event_data.gate_info[2]=event_data.gate_info[3]=event_data.gate_info[4]=0;
		for (int i=0;i<9;i++) {
			event_data.feb_info[i] = 0; //initialize feb information block 
		}

		/**********************************************************************************/
		/*  Set the data_ready flag to false, we have not yet taken any data              */
		/**********************************************************************************/
		data_ready = false; //no data is ready to be processed

		/**********************************************************************************/
		/*   reset the thread count if in threaded operation                              */
		/**********************************************************************************/
#if THREAD_ME
		thread_count = 0;
#endif
#if DEBUG_THREAD
		cout<<"Launching the trigger thread"<<endl;
#endif

		/**********************************************************************************/
		/*    Trigger the DAQ, either mode                                                */
		/**********************************************************************************/
#if THREAD_ME
		boost::thread trigger_thread(boost::bind(&TriggerMe,daq));
#elif NO_THREAD
		TriggerMe(daq);
#endif 

		/**********************************************************************************/
		/*   Execute TakeData or launch appropriate threads as appropriate                */
		/*   for the current running mode                                                 */
		/**********************************************************************************/
		/**********************************************************************************/
		/*   Make the an event_handler pointer for passing to functions which             */
		/*   require a pointer passed to them                                             */
		/**********************************************************************************/
		event_handler *evt = &event_data;

		/**********************************************************************************/
		/*  Initialize loop counter variables                                             */
		/**********************************************************************************/
		int croc_id;
		int no_crocs = currentController->GetCrocVectorLength(); 

		/**********************************************************************************/
		/*   Loop over crocs and then channels in the system.  Execute TakeData on each   */
		/*   Croc/channel combination of FEB's                                            */
		/**********************************************************************************/
		for (int i=0;i<no_crocs;i++) {
			croc_id = i+1;
			croc *tmpCroc = currentController->GetCroc(croc_id);
			for (int j=0;j<4;j++) {
				if ((tmpCroc->GetChannelAvailable(j))&&(tmpCroc->GetChannel(j)->GetHasFebs())) {
					/**********************************************************************************/
					/*      Threaded Option                                                           */
					/**********************************************************************************/
#if DEBUG_THREAD
					cout<<"launching data thread: "<<croc_id<<" "<<j<<endl;
#endif
#if THREAD_ME
#if TIME_ME
					struct timeval dummy;
					gettimeofday(&dummy,NULL);
					thread_launch_log<<thread_count<<"\t"<<gate<<"\t"
						<<(dummy.tv_sec*1000000+dummy.tv_usec)<<"\t"
						<<(gate_start_time.tv_sec*1000000+gate_start_time.tv_usec)<<endl;
#endif
#if DEBUG_THREAD
					cout<<thread_count<<endl;
#endif
					data_threads[thread_count] = 
						new boost::thread((boost::bind(&TakeData,boost::ref(daq),boost::ref(evt),croc_id,j,
						thread_count, attach, sys_id)));
#if DEBUG_THREAD
					cout<<"Success."<<endl;
#endif 
#if TIME_ME
					gettimeofday(&dummy,NULL);
					thread_return_log<<thread_count<<"\t"<<gate<<"\t"
						<<(dummy.tv_sec*1000000+dummy.tv_usec)<<"\t"
						<<(gate_start_time.tv_sec*1000000+gate_start_time.tv_usec)<<endl;
#endif
					thread_count++;

					/**********************************************************************************/
					/*  Unthreaded option                                                             */
					/**********************************************************************************/
#elif NO_THREAD
#if DEBUG_ME
					cout<<"CROC: "<<croc_id<<" channel: "<<j<<std::endl;
#endif
					TakeData(daq,evt,croc_id,j,0,attach,sys_id);
#endif
				} //channel has febs
			} //channel
		} //croc

		/**********************************************************************************/
		/*   wait for trigger thread to join in threaded operation                        */
		/**********************************************************************************/
#if THREAD_ME
		trigger_thread.join();

		/**********************************************************************************/
		/*   And the data taking threads                                                  */
		/**********************************************************************************/
#if DEBUG_THREAD
		cout<<"Getting ready to join threads"<<endl;
#endif
		for (int i=0;i<thread_count;i++) {
#if DEBUG_THREAD
			std::cout<<i<<endl;
#endif
			data_threads[i]->join();
#if DEBUG_THREAD
			cout<<"thread joined"<<endl;
#endif
		}
#endif
// endif THREAD_ME

		/**********************************************************************************/
		/*  re-enable the IRQ for the next trigger                                        */
		/**********************************************************************************/
		daq->ResetGlobalIRQEnable(); //re-enable the IRQ for the next gate

#if SINGLE_PC||MASTER
		/**********************************************************************************/
		/*   Write the End-of-Event Record to the event_handler and then to the           */
		/*   event builder.                                                               */
		/**********************************************************************************/

		//Build DAQ event bank--we should have collected up all of the signals by now
		//Get Trigger Time, Timing Violation Error (obsolete), MINOS SGATE
		int bank = 3; //DAQ Data Bank
		int error, minos, trig_time; error=minos=trig_time=0; //hold that thought...
		int detector, configuration, trigger; detector = configuration = trigger = 0;

		event_data.run_info[0]=detector; event_data.run_info[1]=configuration; event_data.run_info[4]=trigger;
		event_data.feb_info[4]=bank; event_data.feb_info[1]=daq->GetController()->GetID();
		event_data.gate_info[3]=trig_time; event_data.gate_info[3]=error; event_data.gate_info[4]=minos;

#if DEBUG_ME
		cout<<"Contacting the EventBuilder from Main"<<std::endl;
#endif

#if MASTER
		std::cout<<"gate_done: "<<gate_done[0]<<std::endl;
		while (!gate_done[0]) {
			std::cout<<"waiting..."<<std::endl;
			struct sockaddr_in remote_address;
			socklen_t address_length;
			int connection;
			address_length = sizeof (remote_address);
			std::cout<<"ready to connect: "<<socket_handle<<std::endl;
			connection = accept(socket_handle, (sockaddr*)&remote_address, &address_length);
			std::cout<<"still waiting..."<<std::endl;
			if (connection == -1) {
				/* The call to accept failed. */
				if (errno == EINTR)
				/* The call was interrupted by a signal. Try again. */
					continue;
				else
				/* Something else went wrong. */
					perror("accept");
					exit(EXIT_FAILURE);
			}
			if ((read(connection, gate_done, sizeof (gate_done)))!=sizeof(gate_done)) { //read "done" from the master
				perror("server read error: done"); //read in the number of gates to process
				exit(EXIT_FAILURE);
			}
			std::cout<<"gate_done: "<<gate_done[0]<<std::endl;
		}
#endif
		/* contact event builder service */
#if KEEP_DATA
		daq->ContactEventBuilder(&event_data,-1,attach, sys_id);
#endif

#if RECORD_EVENT
		if (!(gate%100)) {
			cout<<"********************************************************************************"<<endl;
			cout<<"Completed Gate: "<<gate<<endl;
		}

#if TIME_ME
		gettimeofday(&gate_stop_time,NULL);
		double duration = (gate_stop_time.tv_sec*1e6+gate_stop_time.tv_usec) - 
			(gate_start_time.tv_sec*1e6+gate_start_time.tv_usec);
		if (!(gate%100)) {
			cout<<"Start Time: "<<(gate_start_time.tv_sec*1000000+gate_start_time.tv_usec)<<" Stop Time: "
				<<(gate_stop_time.tv_sec*1e6+gate_start_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<endl;
		}
		gate_time_log<<gate<<"\t"<<duration<<endl;
#endif
		if (!(gate%100)) {
			cout<<"********************************************************************************"<<endl;
		}
#endif
#endif
// endif SINGLE_PC||MASTER
#if (!MASTER)&&(!SINGLE_PC)
		std::cout<<"writing true to master"<<std::endl;
		gate_done[0]=true;
		if (write(socket_handle,gate_done,1)==-1) { //we're done!
			perror("server read error: done"); //read in the number of gates to process
			exit(EXIT_FAILURE);
		}
#endif

	} //end of gates loop
#if !SINGLE_PC
	close(socket_handle);
#endif
#endif 
//TAKE_DATA

	/**********************************************************************************/
	/*   return the success status of the run                                         */
	/**********************************************************************************/
	success = true;

	/**********************************************************************************/
	/*       delete the acquire functions                                             */
	/**********************************************************************************/
	delete daq;

#if TIME_ME
	gettimeofday(&stop_time,NULL);
	double duration =(double) (stop_time.tv_sec*1e6+stop_time.tv_usec)-(start_time.tv_sec*1e6+start_time.tv_usec);
	cout<<"Start Time: "<<(start_time.tv_sec*1e6+start_time.tv_usec)<<" Stop Time: "
		<<(stop_time.tv_sec*1e6+stop_time.tv_usec)<<" Run Time: "<<(duration/1e6)<<endl;
#endif

	/**********************************************************************************/
	/*              End of execution                                                  */
	/**********************************************************************************/
	return success;
}


void TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id, int thread, 
	et_att_id  attach, et_sys_id  sys_id) 
{
/*!
*  \fn void TakeData(acquire_data *daq, event_handler *evt, int croc_id, int channel_id, int thread,
*                et_att_id  attach, et_sys_id  sys_id)
*
*  This function executes the necessary commands to complete an acquisition sequence.
*
*  Code is available for threaded and unthreaded operating modes.
*  
*  \param *daq, a pointer to the acquire_data object governing this DAQ acquisition
*  \param *evt, a pointer to the event_handler structure containing information
*               about the data being handled.
*  \param croc_id, an integer with the CROC being serviced in this call
*  \param channel_id, an integer with the channel number being serviced in this cal
*  \param thread, the thread number of this call
*  \param attach, the ET attachemnt to which data will be stored
*  \param sys_id, the ET system handle
*/

	/**********************************************************************************/
	/*  the function which interfaces with the data acquire functions to              */
	/*  execute the data acquisition loop                                             */
	/**********************************************************************************/
#if TIME_ME
	struct timeval start_time, stop_time;
	gettimeofday(&start_time, NULL);
#endif

	/**********************************************************************************/
	/*      Files for monitoring acquisition                                          */
	/**********************************************************************************/
	ofstream data_monitor;
	stringstream threadno;
	threadno<<thread;
	string filename;
	filename = "data_monitor_"+threadno.str();
	data_monitor.open(filename.c_str());
	time_t currentTime; time(&currentTime);
	data_monitor<<"Thread Start Time:  "<<ctime(&currentTime)<<endl;

	/**********************************************************************************/
	/*  Local croc & crim variables for eas of computational manipulation             */
	/**********************************************************************************/
	croc *crocTrial = daq->GetController()->GetCroc(croc_id);
	channels *channelTrial=daq->GetController()->GetCroc(croc_id)->GetChannel(channel_id);

	/**********************************************************************************/
	/*   a flag for data acquisition status                                           */
	/**********************************************************************************/
	bool data_taken = true; //a flag to let us know that we have successfully
							//serviced this channel (the functions return "0" if they are successful...)

	/**********************************************************************************/
	/*   get the FEB list which belongs to this channel                               */
	/*   and an iterator for the FEB loop                                             */
	/**********************************************************************************/
	list<feb*> *feb_list = channelTrial->GetFebList(); //the feb's on this channel
	list<feb*>::iterator feb; //we want to loop over them when we get the chance...

#if DEBUG_ME
	data_monitor<<"is data ready? "<<data_ready<<std::endl;
	data_monitor<<"bank? "<<evt->feb_info[4]<<std::endl;
#endif

	/**********************************************************************************/
	/*   the loops which govern the acquiring of data from the FEB's.                 */
	/*   The first waits until data is ready.                                         */
	/*   The second executes when data is ready to be acquired from the electronics   */
	/**********************************************************************************/
	while (!data_ready) { continue; } //wait for data to be ready

	while ((data_ready)&&(evt_record_available)) { //wait for data to become available
		//loop over all febs
		for (feb=feb_list->begin();feb!=feb_list->end();feb++) { //here it is, the feb loop
			/**********************************************************************************/
			/*          Take all data on the feb                                              */
			/**********************************************************************************/
			data_taken = daq->TakeAllData((*feb),channelTrial,crocTrial,evt,thread,attach,sys_id); 
#if DEBUG_ME
			data_monitor<<"TakeAllData Returned"<<std::endl;
#endif
			if (data_taken) { //and if you didn't succeed...(the functions return 0 if successful) 
				cout<<"Problems taking data on FEB: "<<(*feb)->GetBoardNumber()<<endl;
				cout<<"Leaving thread servicing CROC: "<<croc_id<<" channel: "<<channel_id<<endl;
				exit(-2000); //stop the presses!
			}
		} //feb loop
#if DEBUG_ME
		data_monitor<<"Completed processing FEB's in this list."<<std::endl;
#endif
#if TIME_ME
		boost::mutex::scoped_lock lock(main_mutex); 
		gettimeofday(&stop_time,NULL);
		double duration = (double) (stop_time.tv_sec*1e6+stop_time.tv_usec)-(start_time.tv_sec*1e6+start_time.tv_usec);
		take_data_extime_log<<evt->gate_info[1]<<"\t"<<thread<<"\t"<<(start_time.tv_sec*1000000+start_time.tv_usec)
			<<"\t"<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<endl;
#endif

		if (!data_taken) return; //we're done processing this channel
	} //data ready loop
} // end void TakeData


void TriggerMe(acquire_data *daq) 
{
/*! \fn void TriggerMe(acquire_data *data)
*
*  The function which arms and sets the trigger for each gate.  
*
*  This version currently is only has "One-Shot" set up for the 
*  trigger type. 
*
*  \param *daq a pointer to the acquire_data object which governs this DAQ Execution.
*
*/
	/**********************************************************************************/
	/*   The function which governs the triggering of the DAQ                         */
	/**********************************************************************************/
#if TIME_ME
	struct timeval start_time, stop_time;
	gettimeofday(&start_time, NULL);
	if (!trigger_log.is_open()) {
		trigger_log.open("trigger_thread_log.csv");
	}
#endif

#if DEBUG_ME
	time_t currentTime; time(&currentTime);
	std::cout<<"Trigger Time: "<<ctime(&currentTime);
	std::cout<<"Setting Trigger"<<std::endl;
#endif

	/**********************************************************************************/
	/* let the hardware tell us when the trigger has completed                        */
	/**********************************************************************************/
    /*! \note The trigger can be set up to use either the CRIM's interrupt 
     * or just to set the software gate via the fast-command register on the CRIM  
     */

	daq->TriggerDAQ(0); //send the one-shot trigger
	daq->WaitOnIRQ(); //wait for the trigger to be set (only returns if successful)

	/**********************************************************************************/
	/*  Let the interrupt handler deal with an asserted interrupt                     */
	/**********************************************************************************/
    /*! \note  This uses the interrupt handler to handle an asserted interrupt 
     *
     */
#if ASSERT_INTERRUPT
	daq->AcknowledgeIRQ(); //acknowledge the IRQ (only returns if successful)
#endif

#if DEBUG_ME
	std::cout<<"Data Ready"<<std::endl;
#endif

	/**********************************************************************************/
	/*  Set Data Ready                                                                */
	/**********************************************************************************/
	data_ready = true; //tell the data acquiring threads that data is available for processing.

#if TIME_ME
	gettimeofday(&stop_time,NULL);
	double duration =(double) (stop_time.tv_sec*1000000+stop_time.tv_usec)-
		(start_time.tv_sec*1000000+start_time.tv_usec);
	trigger_log<<(start_time.tv_sec*1000000+start_time.tv_usec)<<"\t"
		<<(stop_time.tv_sec*1000000+stop_time.tv_usec)<<"\t"<<(duration/1000000)<<endl;
#endif
} // end void TriggerMe


void SetHV(acquire_data *daq, int i, int j) 
{
/*! \fn void SetHV(acquire_data *daq, int i, int j)
* Sets and monitors the HV on an FEB until the HV comes to the set-point.
* 
* This function loops over each FEB in the list belonging to channel j and 
* sets the high voltage via an FPGA frame.  
*
* It then monitors that voltage via MonitorHV, belonging to *daq, until
* the return value is within 15 counts of the set point.
*
* Code is available for both threaded and unthreaded execution.
*
* \param *daq a pointer to the acquire_data object which governs this DAQ execution
* \param i an integer, the CROC ID being set
* \param j an integer, the Channel ID on croc i  */

	/**********************************************************************************/
	/*   A function which sets the HV on FEB's                                        */
	/**********************************************************************************/
#if THREAD_ME
	stringstream thread_number;
	thread_number<<j;
	string filename="HV_thread_"+thread_number.str();
	ofstream monitor_thread;
	monitor_thread.open(filename.c_str());
	monitor_thread<<"Preparing to set HV"<<endl;
#else
	cout<<"Preparing to set HV"<<endl;
#endif
	bool hv_set = false;
	int hvdiff = -1;
	std::list<feb*> *feblist = daq->GetController()->GetCroc(i)->GetChannel(j)->GetFebList();
	std::list<feb*>::iterator p,q;
	for (p=feblist->begin();p!=feblist->end();p++) {
#if THREAD_ME
		monitor_thread<<"Setting the HV on FEB: "<<(*p)->GetFEBNumber()<<std::endl;
#else
		cout<<"Setting the HV on FEB: "<<(*p)->GetFEBNumber()<<std::endl;
#endif
		daq->SetHV((*p),daq->GetController()->GetCroc(i), 
			daq->GetController()->GetCroc(i)->GetChannel(j), 44000, 30, 1);
		hvdiff = abs(44000-(daq->MonitorHV((*p),daq->GetController()->GetCroc(i), 
			daq->GetController()->GetCroc(i)->GetChannel(j))));
	}

	for (p=feblist->begin();p!=feblist->end();p++) {
#if THREAD_ME
		monitor_thread<<"Current HV for Tube "<<(*p)->GetFEBNumber()<<" on Channel "<<j
			<<": "<<(daq->MonitorHV((*p),daq->GetController()->GetCroc(i),
			daq->GetController()->GetCroc(i)->GetChannel(j)))<<endl;
		(*p)->ShowValues();
#else
		cout<<"Current HV for Tube "<<(*p)->GetFEBNumber()<<" on Channel "<<j<<": "
			<<(daq->MonitorHV((*p),daq->GetController()->GetCroc(i),
			daq->GetController()->GetCroc(i)->GetChannel(j)))<<endl;
#endif

		while (hvdiff>15) { 
			for (q=feblist->begin();q!=feblist->end();q++) {
				system("sleep 10s");
				hvdiff = abs(44000-(daq->MonitorHV((*q),daq->GetController()->GetCroc(i), 
					daq->GetController()->GetCroc(i)->GetChannel(j))));
#if DEBUG_THREAD
				(*q)->ShowValues();
#endif
#if THREAD_ME
				monitor_thread<<"Current HV: "<<(daq->MonitorHV((*q),daq->GetController()->GetCroc(i),
					daq->GetController()->GetCroc(i)->GetChannel(j)))<<" hvdiff: "<<hvdiff<<endl;
#else
				cout<<"Current HV: "<<(daq->MonitorHV((*q),daq->GetController()->GetCroc(i),
					daq->GetController()->GetCroc(i)->GetChannel(j)))<<" hvdiff: "<<hvdiff<<endl;
#endif
				if (hvdiff<=15)  break;
			}
		}
	}
} // end void SetHV
