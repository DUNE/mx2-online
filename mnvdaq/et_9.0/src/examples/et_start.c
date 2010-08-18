/*----------------------------------------------------------------------------*
 *  Copyright (c) 1998        Southeastern Universities Research Association, *
 *                            Thomas Jefferson National Accelerator Facility  *
 *                                                                            *
 *    This software was developed under a United States Government license    *
 *    described in the NOTICE file included as part of this distribution.     *
 *                                                                            *
 *    Author:  Carl Timmer                                                    *
 *             timmer@jlab.org                   Jefferson Lab, MS-12H        *
 *             Phone: (757) 269-5130             12000 Jefferson Ave.         *
 *             Fax:   (757) 269-5800             Newport News, VA 23606       *
 *                                                                            *
 *----------------------------------------------------------------------------*
 *
 * Description:
 *      An example program to show how to start up an Event Transfer system.
 *
 *----------------------------------------------------------------------------*/

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include "et.h"

/* used by the signal handler */
sig_atomic_t time_to_quit = 0;

void quit_signal_handler(int signum);

void flush_and_exit(int code);

int main(int argc, char **argv)
{  
  int           c;
  extern char  *optarg;
  extern int    optind;
  int           errflg = 0;
  int           i_tmp;
  
  int           status;
  int           et_verbose = ET_DEBUG_NONE;
  int           deleteFile = 0;
  int           had_attachments = 0;
  sigset_t      sigblockset, sighandleset;

  et_sysconfig  config;
  et_sys_id     id;
  
  struct timespec sleeptime;
  /*
  et_statconfig sconfig;
  et_stat_id    statid;
  */
  
  /************************************/
  /* default configuration parameters */
  /************************************/
  int nevents = 2000;               /* total number of events */
  int event_size = 3000;            /* size of event in bytes */
  char *et_filename = NULL;
  char  et_name[ET_FILENAME_LENGTH];
  int networkPort = 1091;
  int callback_pid = 0;            /* PID of process that will be contacted when the ET system has been set up. */
  
  while ((c = getopt(argc, argv, "vdn:s:f:p:c:")) != EOF) {
    switch (c) {
    case 'p':
      i_tmp = atoi(optarg);
      if  ( (i_tmp > 1090) && (i_tmp < 1097) ) {
	networkPort = i_tmp;
      } else {
	printf("Invalid argument to -p. Valid ports are 1091-1096.\n");
	flush_and_exit(-1);
      }
      break;
    
    case 'c':
      callback_pid = atoi(optarg);
      if (callback_pid <= 1)
      {
         printf("Invalid argument to -c.  Process must have id >= 2.\n");
         flush_and_exit(-1);
      }
      if (kill(callback_pid, 0) == ESRCH)
      {
         printf("Invalid argument to -c: process does not exist.\n");
         flush_and_exit(-1);
      }
      break;

    case 'n':
      i_tmp = atoi(optarg);
      if (i_tmp > 0) {
	nevents = i_tmp;
      } else {
	printf("Invalid argument to -n. Must be a positive integer.\n");
	flush_and_exit(-1);
      }
      break;
      
    case 's':
      i_tmp = atoi(optarg);
      if (i_tmp > 0) {
	event_size = i_tmp;
      } else {
	printf("Invalid argument to -s. Must be a positive integer.\n");
	flush_and_exit(-1);
      }
      break;
      
    case 'f':
      if (strlen(optarg) >= ET_FILENAME_LENGTH) {
        fprintf(stderr, "ET file name is too long\n");
        flush_and_exit(-1);
      }
      strcpy(et_name, optarg);
      et_filename = et_name;
      break;

    /* Remove an existing memory-mapped file first, then recreate it. */
    case 'd':
      deleteFile = 1;
      break;

    case 'v':
      et_verbose = ET_DEBUG_INFO;
      break;
      
    case ':':
    case 'h':
    case '?':
    default:
      errflg++;
    }
  }
    
  if (optind < argc || errflg){
    fprintf(stderr, "usage: %s -v -r [-n events] [-s event_size] [-f file] [-p port]\n", argv[0]);
    fprintf(stderr, "          -v for verbose output\n");
    fprintf(stderr, "          -d deletes an existing file first\n");
    fprintf(stderr, "          -n sets number of events\n");
    fprintf(stderr, "          -s sets event size in bytes\n");
    fprintf(stderr, "          -f sets memory-mapped file name\n");
    fprintf(stderr, "          -p sets the network port (default is 1091; 1092-1094 also valid)\n");
    flush_and_exit(2);
  }

  /* Check et_filename */
  if (et_filename == NULL) {
    /* see if env variable SESSION is defined */
    if ( (et_filename = getenv("SESSION")) == NULL ) {
      fprintf(stderr, "No ET file name given and SESSION env variable not defined\n");
      flush_and_exit(-1);
    }
    /* check length of name */
    if ( (strlen(et_filename) + 12) >=  ET_FILENAME_LENGTH) {
      fprintf(stderr, "ET file name is too long\n");
      flush_and_exit(-1);
    }
    sprintf(et_name, "%s%s", "/tmp/et_sys_", et_filename);
  }
  
  for ( ; optind < argc; optind++) {
    printf("%s\n", argv[optind]);
  }
  
  printf("Starting an ET system.  This may take a couple of minutes...\n");
  fflush(stdout);

  struct tm *local;
  time_t starttime;
  starttime = time(NULL);
  local = localtime(&starttime);
  printf("Starting to open the systeam at time (local): %s\n", asctime(local));
  fflush(stdout);

  if (et_verbose) {
    printf("et_start: asking for %d byte frames.\n", event_size);
    printf("et_start: asking for %d frames.\n", nevents);
    printf("et_start: using port %d.\n", networkPort);
    fflush(stdout);
  }

  if (deleteFile) {
    remove(et_filename);
  }
  
  /********************************/
  /* set configuration parameters */
  /********************************/
  
  if (et_system_config_init(&config) == ET_ERROR) {
    printf("et_start: no more memory\n");
    flush_and_exit(1);
  }
  /* total number of events */
  et_system_config_setevents(config, nevents);

  /* size of event in bytes */
  et_system_config_setsize(config, event_size);

  /* max number of temporary (specially allocated mem) events */
  /* This cannot exceed total # of events                     */
  et_system_config_settemps(config, nevents);

  /* limit on # of stations */
  et_system_config_setstations(config, 10);
  
  /* soft limit on # of attachments (hard limit = ET_ATTACHMENTS_MAX) */
  et_system_config_setattachments(config, 20);
  
  /* soft limit on # of processes (hard limit = ET_PROCESSES_MAX) */
  et_system_config_setprocs(config, 20);
    
  /* set TCP server port */
  et_system_config_setserverport(config, networkPort); 
  
  /* add multicast address to listen to  */
  /* et_system_config_addmulticast(config, ET_MULTICAST_ADDR); */
  
  /* Make sure filename is null-terminated string */
  if (et_system_config_setfile(config, et_name) == ET_ERROR) {
    printf("et_start: bad filename argument\n");
    flush_and_exit(1);
  }
  
  /*************************/
  /* setup signal handling */
  /*************************/
  
  /* block all signals to prevent interruptions */
  sigfillset(&sigblockset);
  status = pthread_sigmask(SIG_BLOCK, &sigblockset, NULL);
  if (status != 0) {
    printf("et_start: couldn't block all signals (pthread_sigmask failure)\n");
    flush_and_exit(1);
  }
  /* now unblock SIGINT and SIGTERM so we can handle them */
  sigemptyset(&sighandleset);
  sigaddset(&sighandleset, SIGINT);
  sigaddset(&sighandleset, SIGTERM);
  status = pthread_sigmask(SIG_UNBLOCK, &sighandleset, NULL);
  if (status != 0) {
    printf("et_start: couldn't unblock SIGINT and SIGTERM (pthread_sigmask failure)\n");
    flush_and_exit(1);
  }
  /* set the signal handler */
  signal(SIGINT,  quit_signal_handler);
  signal(SIGTERM, quit_signal_handler);
  
  /*************************/
  /*    start ET system    */
  /*************************/
  if (et_verbose) {
    printf("et_start: starting ET system %s\n", et_name);
  }
  if (et_system_start(&id, config) != ET_OK) {
    printf("et_start: error in starting ET system\n");
    flush_and_exit(1);
  }
  starttime = time(NULL);
  local = localtime(&starttime);
  printf("System opened at time (local): %s\n", asctime(local));
  fflush(stdout);
  
  et_system_setdebug(id, et_verbose);
 
  /* any listers to the STDOUT pipe will get all the data pushed to them now */
  fflush(stdout);
  
  /* send the SIGUSR1 signal to the specified process signalling that ET is ready */
  if (callback_pid)
     kill(callback_pid, SIGUSR1);
  

  /*************************/
  /*    main loop          */
  /*************************/
  /* monitor the number of attachments to stations.
     once the station count has gone above 0,
     we exit as soon as all stations have detached. */
  sleeptime.tv_sec = 0;
  sleeptime.tv_nsec = 1000000;	/* 10 ms */
  int nattachments;
  while ( ! time_to_quit )
  {
     /* don't busy-wait. */
     nanosleep(&sleeptime, (struct timespec *)NULL);
     
     /* note that we use getattachments() here and not getstations().
        this is because stations are not necessarily deleted if the
        process that created them crashes.  on the other hand, in that case
        Grand Central _does_ notice that the attachment has disappeared,
        so we can count on the attachment number correctly reflecting
        the number of processes that are currently using the station. */
     status = et_system_getattachments(id, &nattachments);
     if (status != ET_OK)
     {
       printf("et_start: error monitoring attachment count (errno: %d)!  quitting.\n", status);
       time_to_quit = 1;
     }
     
     if ( !had_attachments && nattachments > 0 )
       had_attachments = 1;
     
     /* if we had attachments at one point and don't any longer,
        then it's time to close down the system. */
     if ( had_attachments && nattachments == 0 )
     {
       time_to_quit = 1;
       printf("All stations detached.  System will close.\n");
     }
  }
  

  printf("ET is exiting.\n");
  et_system_close(id);

  flush_and_exit(0);  
}

/* this function is intended to be the signal handler
   for SIGINT and SIGTERM.  all it does is set time_to_quit
   to 1, which will cause the main program to shut down
   gracefully. */
   
void quit_signal_handler(int signum)
{
	printf("Received SIGTERM or SIGINT.\n");
	time_to_quit = 1;
	
	/* don't bother resetting the signal handler.
	   we don't need to call this function more than once. */
}

/* this function flushes all buffers before exiting
   so that any parent process is guaranteed to get
   its output. */
   
void flush_and_exit(int code)
{
	fflush(stdout);
	fflush(stderr);
	
	exit(code);
}
