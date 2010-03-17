"""
   Defaults.py:
   Default values for the various modules in the run control software.
   They are centralized here for easier modification of the setup.
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb. 2010
                    
   Address all complaints to the management.
"""

import time

# Data acquisition properties.
EVENT_SIZE = 2048 
FRAMES = 8

# Run control properties.
CONFIG_DB_LOCATION = "/work/conditions/run_control_config.db"

RUN_SERIES_DB_LOCATION_DEFAULT = "/work/conditions/run_series"
RUN_SUBRUN_DB_LOCATION_DEFAULT = "/work/conditions/next_run_subrun.db"
LOGFILE_LOCATION_DEFAULT = "/work/data/logs"
RC_LOGFILE_DEFAULT = LOGFILE_LOCATION_DEFAULT + "/runcontrol.log"

ET_SYSTEM_LOCATION_DEFAULT = "/work/data/etsys"
RAW_DATA_LOCATION_DEFAULT = "/work/data/rawdata"

RESOURCE_LOCATION_DEFAULT = "/work/software/mnvruncontrol/resources"


# Socket communication defaults.
DISPATCHER_PORT = 1098
MASTER_PORT     = 1090
ET_PORT_BASE    = 1091

SOLDIER = "mnvonline0.fnal.gov"
WORKER  = "mnvonline1.fnal.gov"
#MASTER  = "mnvonlinemaster.fnal.gov"
MASTER = "localhost"

MAX_CONNECTION_ATTEMPTS = 5
CONNECTION_ATTEMPT_INTERVAL = 0.2	# in seconds
SOCKET_TIMEOUT = 0.25

# dispatcher process details
DISPATCHER_PIDFILE = "/tmp/rc_dispatcher.pid"
DISPATCHER_LOGFILE = "/work/data/logs/dispatcher.log"

# environment configuration
DAQROOT_DEFAULT = "/work/software/mnvonline/mnvdaq"

