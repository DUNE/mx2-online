"""
   Defaults.py:
   Default values for the various modules in the run control software.
   They are centralized here for easier modification of the setup.
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
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
CONNECTION_ATTEMPT_INTERVAL = 1.0	# in seconds
SOCKET_TIMEOUT = 1.0  # in seconds

# number of times in a row to log the same request
# in the dispatcher before suppressing
MAX_REPEATED_REQUEST_LOGS = 5

# number of times in a row to log the same request
# in the dispatcher before suppressing
MAX_REPEATED_REQUEST_LOGS = 5

# dispatcher process details
DISPATCHER_PIDFILE = "/work/conditions/rc_dispatcher.pid"
DISPATCHER_LOGFILE = "/work/data/logs/dispatcher.log"

# slow control
SLOWCONTROL_CONFIG_LOCATION_DEFAULT = "/work/conditions/MParamFiles/data/DAQ/hardware_config"
SLOWCONTROL_ALLOWED_HV_THRESHOLDS = {300: 0, 100: 3, 60: 15}	# that is, { threshold : num allowed over that threshold, ... }
SLOWCONTROL_ALLOWED_PERIOD_THRESHOLD = 15000
