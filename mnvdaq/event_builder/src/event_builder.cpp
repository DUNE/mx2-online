#include "event_builder.h"
#include "event_builder_templates.h"

using namespace std;

ofstream thread_log("eb_log.txt");

int main(int argc, char **argv) {
  /*! \fn the main function for running the event builder */
  /* First things first...we need to make sure that the ET is actually running and if it isn't 
 * fix it. */

  if (argc != 2) {
    printf("Usage: et_producer <et_filename>\n");
    exit(1);
  }

  string output_filename(argv[1]);
  output_filename+=".dat";
  ofstream binary_outputfile(output_filename.c_str(),ios::out|ios::app|ios::binary); //open the file for binary
                                                                                       //output
  int event_size, status;
  et_openconfig openconfig;

  et_att_id  attach;
  et_sys_id  sys_id;
  
  et_stat_id cu_station;
  et_statconfig sconfig;
  et_event   *pe;
  et_id      *id;

  /* The station which will attach event headers to the buffers in an event handler structure */
  et_station_config_init(&sconfig);
  et_station_config_setblock(sconfig,ET_STATION_BLOCKING);
  et_station_config_setselect(sconfig,ET_STATION_SELECT_ALL);
  et_station_config_setuser(sconfig,ET_STATION_USER_SINGLE);
  et_station_config_setrestore(sconfig,ET_STATION_RESTORE_OUT);
  

  /* opening the ET system is the first thing we must do */
  et_open_config_init(&openconfig);
#if MULTIPC
  et_open_config_setmode(&openconfig, ET_HOST_AS_REMOTE);
  et_open_config_setcast(openconfig, ET_DIRECT);
  et_open_config_sethost(openconfig, "minervatest01.fnal.gov");
  et_open_config_setserverport(openconfig, 1091); // multi-pc & remote mode?...
#endif

  if (et_open(&sys_id, argv[1], openconfig) != ET_OK) {
    printf("et_producer: et_open problems\n");
    exit(1);
  }
  et_open_config_destroy(openconfig);

  /*check to on whether ET is up and running */
  unsigned int oldheartbeat, newheartbeat;
  id = (et_id *) sys_id;
  oldheartbeat = id->sys->heartbeat;
  int counter = 0;
  do {
   system("sleep 10s"); //give ET a chance to start up
   if (!counter) {
     newheartbeat = id->sys->heartbeat;
   } else {
     oldheartbeat=newheartbeat;
     newheartbeat = id->sys->heartbeat;
   }
   counter++;  
  } while ((newheartbeat==oldheartbeat)&&(counter!=20));
 
  if (counter==20) {
    std::cout<<"ET System did not start properly!"<<std::endl;
    exit(-5);
  }  

  /* set the level of debug output that we want (everything) */
  et_system_setdebug(sys_id, ET_DEBUG_INFO);

  /* create & attach to a new station for making the final output file */
  et_station_create(sys_id,&cu_station,"CHICAGO_UNION",sconfig);
  if (et_station_attach(sys_id, cu_station, &attach) < 0) {
    printf("et_producer: error in station attach\n");
    system("sleep 10s");
    exit(1);
  }

  /* having dispatched with that bit of annoyance request an event from the ET service */
  int evt_counter = 0;
  while ((et_alive(sys_id))) {
    struct timespec time;
    time.tv_sec = 60;
    status = et_event_get(sys_id, attach, &pe, ET_TIMED|ET_MODIFY, &time);
    if (status==ET_ERROR_TIMEOUT) break;
    if (status == ET_ERROR_DEAD) {
      printf("et_client: ET system is dead\n");
      exit(-1);
    }
    else if (status == ET_ERROR_TIMEOUT) {
      printf("et_client: got timeout\n");
      exit(-1);
    }
    else if (status == ET_ERROR_EMPTY) {
      printf("et_client: no events\n");
      exit(-1);
    }
    else if (status == ET_ERROR_BUSY) {
      printf("et_client: station is busy\n");
      exit(-1);
    }
    else if (status == ET_ERROR_WAKEUP) {
      printf("et_client: someone told me to wake up\n");
      exit(-1);
    }
    else if ((status == ET_ERROR_WRITE) || (status == ET_ERROR_READ)) {
      printf("et_client: socket communication error\n");
      exit(-1);
    }
    else if (status != ET_OK) {
      printf("et_client: get error\n");
      exit(-1);
    }
    event_handler *evt;
    int pri;
    size_t len;
    int con[ET_STATION_SELECT_INTS];
    et_event_getdata(pe, (void **) &evt);
    et_event_getpriority(pe, &pri);
    et_event_getlength(pe, &len);
    et_event_getcontrol(pe, con);

    event_builder(evt);

	    void *pdata;
	    int length;
	    switch (evt->feb_info[4]) {
	      case 0:
		length = FEB_HITS_SIZE;
		break;
	      case 1:
		length = FEB_DISC_SIZE;
		break;
      case 2:
        length = FEB_INFO_SIZE;
        break;
      case 3:
        length = DAQ_HEADER;
        break;
    }
    et_event_getdata(pe, &pdata); //get the event ready
    unsigned char final_buffer[length];
    unsigned char *tmp_buffer; 
    if (evt->feb_info[4]!=3) {
      tmp_buffer = event->GetDataBlock();
      for (int data_index=0;data_index<length;data_index++) {
        final_buffer[data_index]=tmp_buffer[data_index];
      }
    } else { 
      for (int data_index=0;data_index<length;data_index++) {
        final_buffer[data_index]= event->GetEventBlock(data_index);
      }
    }

    memcpy (pdata, (void *) final_buffer, length);
    et_event_setlength(pe,length);

    /* put event back into the ET system */
    status = et_event_put(sys_id, attach, pe); //put the event away
    evt_counter++;
    /* now write the event out to a binary file */
    binary_outputfile.write((char *) final_buffer, length);  //write out to binary file
    binary_outputfile.flush();
    if (!(evt_counter%1)) {
      cout<<"********************************************************************************"<<endl; 
      cout<<"Event Processed: "<<evt_counter<<endl;
      cout<<"********************************************************************************"<<endl; 
    }
    delete event;
  }

  cout<<"********************************************************************************"<<endl;
  cout<<"  Quitting Event Builder."<<endl;
  cout<<"********************************************************************************"<<endl;

  //detach from the station
  if (et_station_detach(sys_id, attach) < 0) {
    printf("et_producer: error in station detach\n");
    system("sleep 10s");
    exit(1);
  }

  //close ET
  if (et_close(sys_id) < 0) {
    printf("et_producer: error in ET close\n");
    system("sleep 10s");
    exit(1);
  }
  binary_outputfile.close(); //close the binary file
  return 0; //success!
}

int event_builder(event_handler *evt) {

  #if REPORT_EVENT
     thread_log<<"********************************************************************************"<<std::endl; 
     thread_log<<"Finished Processing Event Data:"<<std::endl;
     thread_log<<"GATE: "<<evt->gate_info[1]<<std::endl;
     thread_log<<"CROC: "<<evt->feb_info[2]<<std::endl;
     thread_log<<"CHAN: "<<evt->feb_info[3]<<std::endl;
     thread_log<<"BANK: "<<evt->feb_info[4]<<std::endl;
     thread_log<<"DETECT: "<<evt->run_info[0]<<std::endl; 
     thread_log<<"CONFIG: "<<evt->run_info[1]<<std::endl; 
     thread_log<<"RUN: "<<evt->run_info[2]<<std::endl;
     thread_log<<"SUB-RUN: "<<evt->run_info[3]<<std::endl;
     thread_log<<"TRIGGER: "<< evt->run_info[4]<<std::endl;
     thread_log<<"GLOBAL GATE: "<<evt->gate_info[0]<<std::endl;
     thread_log<<"TRIG TIME: "<<evt->gate_info[2]<<std::endl;
     thread_log<<"ERROR: "<<evt->gate_info[3]<<std::endl;
     thread_log<<"MINOS: "<<evt->gate_info[4]<<std::endl;
     thread_log<<"BUFFER_LENGTH: "<<evt->feb_info[5]<<std::endl;
     thread_log<<"FIRMWARE: "<<evt->feb_info[7]<<std::endl;
     thread_log<<"FRAME DATA: "<<std::endl;
     for (unsigned int index=0;index<evt->feb_info[5];index++) {
       thread_log<<"byte: "<<index<<" "<<(int)evt->event_data[index]<<std::endl;
     }
  #endif

/*  std::ofstream feb_log;
  std::string filename;
  std::stringstream bank_id;
  bank_id<<evt->run_info[2]<<"_"<<evt->run_info[3]<<"_"<<evt->gate_info[1] 
         <<"_"<<evt->feb_info[1]<<"_"<<evt->feb_info[2]<<"_"<<evt->feb_info[3]<<"_"<<evt->feb_info[4];
  filename = "dummy_feb_log_"+bank_id.str();
  if (!feb_log.is_open()) {
    feb_log.open(filename.c_str());
  }
*/
  
  #if DEBUG_ME
    thread_log<<"Processing event data"<<std::endl;
  #endif

  MinervaHeader *tmp_header;
  // 56?  54 registers in modern feb firmware, should replace with variable argument anyway...
  feb *dummy_feb = new feb(6,1,(febAddresses)0,56,thread_log); //make up a dummy feb to have access to the header decoding functions 
  if (evt->feb_info[4]==3) {
    //build the "DAQ" header
    tmp_header = new MinervaHeader(evt->feb_info[1]); //the special constructor for the DAQ bank
    //make the new event block
    event = new MinervaEvent(evt->run_info[0], evt->run_info[1], evt->run_info[2], 
                             evt->run_info[3], evt->run_info[4], evt->gate_info[0], 
                             evt->gate_info[1], evt->gate_info[2], evt->gate_info[3], 
                             evt->gate_info[4], tmp_header); //make up a new event
    //the call to MinervaEvent constructor automatically inserts the DAQ block into the event buffer
  } else {
    event = new MinervaEvent();

    #if DEBUG_ME
      thread_log<<"Current Event?"<<std::endl;
    #endif

    //sort the event data
    int info_length; //the number of bytes in each "read" of the bank being processed
                     //each of the "SIZE"'s include the 8 bytes of header we pack with the bank info
    switch (evt->feb_info[4]) {
      case 0: //ADC Data

        #if DEBUG_ME
          thread_log<<"ADC Values"<<std::endl;
        #endif
        info_length = FEB_HITS_SIZE-8;
        CheckBufferLength(evt->feb_info[5], info_length);
        for (unsigned int i=0;i<evt->feb_info[5];i+=info_length) {
          #if DEBUG_ME
             thread_log<<"Decoding Buffer"<<std::endl;
             for (int ii=0;ii<info_length;ii++) {
               cout<<"data: "<<(int)evt->event_data[ii]<<endl;
             } 
          #endif
          DecodeBuffer(evt, dummy_feb->GetADC(0), i, info_length,thread_log);
          //build the data block header
          #if DEBUG_ME
             thread_log<<"Building Bank Header"<<std::endl;
          #endif
          tmp_header = BuildBankHeader(evt,dummy_feb->GetADC(0),thread_log);
          //build event  
          #if DEBUG_ME
             thread_log<<"Making Data Block"<<std::endl;
          #endif
          event->MakeDataBlock(dummy_feb->GetADC(0), tmp_header);
        }
        break;
      case 1: //discriminator data
        #if DEBUG_ME
          thread_log<<"DISC Values"<<std::endl;
           /*for (int ii=0;ii<info_length;ii++) {
             cout<<"data: "<<(int)evt->event_data[ii]<<endl;
           } */
        #endif
        info_length = FEB_DISC_SIZE-8;
        CheckBufferLength(evt->feb_info[5], info_length);
        for (unsigned int i=0;i<evt->feb_info[5];i+=info_length) {
          DecodeBuffer(evt,dummy_feb->GetDisc(), i, info_length,thread_log);
          //build the data block header
          tmp_header = BuildBankHeader(evt,dummy_feb->GetDisc(),thread_log);
          //build event  
          event->MakeDataBlock(dummy_feb->GetDisc(), tmp_header);
        }
        break;
      case 2: //FEB info
        #if DEBUG_ME
          thread_log<<"FEB Values"<<std::endl;
           /*for (int ii=0;ii<info_length;ii++) {
             cout<<"data: "<<(int)evt->event_data[ii]<<endl;
           } */
        #endif
        info_length = FEB_INFO_SIZE-8;
        CheckBufferLength(evt->feb_info[5], info_length);
        try {
          if (info_length != dummy_feb->GetExpectedIncomingMessageLength()) throw info_length;
        } catch (int e) {
           cout<<"Message Length Mismatch: "<<info_length<<" should be: "<<dummy_feb->GetIncomingMessageLength()<<endl;
	   dummy_feb->DecodeRegisterValues(dummy_feb->GetIncomingMessageLength());
           exit(-3);
        }
        for (unsigned int i=0;i<evt->feb_info[5];i+=info_length) {
          #if DEBUG_ME
             thread_log<<"Decoding Buffer"<<std::endl;
          /*   for (int j=0;j<info_length;j++) {
               std::cout<<evt->event_data[j]<<std::endl;
             } */
          #endif
          DecodeBuffer(evt,dummy_feb, i, info_length,thread_log);
          dummy_feb->ShowValues();
          //build the data block header
          #if DEBUG_ME
             thread_log<<"Building Bank Header"<<std::endl;
          #endif
          tmp_header = BuildBankHeader(evt,dummy_feb,thread_log);
          //build event  
          #if DEBUG_ME
             thread_log<<"Making Data Block"<<std::endl;
          #endif
          event->MakeDataBlock(dummy_feb, tmp_header);
         }
         break;
      case 3: //DAQ event info
        cout<<"Received a DAQ event bank on a current event!"<<endl;
        return (-1);
        break;
      default:
        cout<<"Failed Event Bank"<<endl;
        return (-1);
    }
  }

  #if DEBUG_ME
    thread_log<<"Completed! Processed Event Data!"<<std::endl;
  #endif
  delete dummy_feb;
  delete tmp_header;
  return 0;
}  

void HandleErrors(int success) { 
  /*! \fn a little event handler
 *
 * \param success the return value for an unsuccessful
 * execution 
 *
 */
  try  {
    if (success<0) throw (success);
  } catch (int e) {
    perror("server read");
    exit(EXIT_FAILURE);
  }
} 

void CheckBufferLength(int length, int frame_length) {
  /*! \fn A function to make sure that the buffer length is correct 
 *
 * \param length the returned buffer lenght
 * \param frame_length the lenght that the frame is supposed to be
 */
  if (!(length%frame_length)) {
    cout<<"Buffer length, frame length disparity."<<endl;
    exit(-4);
  }
}

