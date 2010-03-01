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
# do these need to be calculated somehow?
# or are they always fixed?
EVENT_SIZE = 2048 
FRAMES = 8

# Run control properties.
CONFIG_DB_LOCATION = "/work/conditions/run_control_config.db"

RUN_SUBRUN_DB_LOCATION_DEFAULT = "/work/conditions/next_run_subrun.db"
LOGFILE_LOCATION_DEFAULT = "/work/data/logs"

ET_SYSTEM_LOCATION_DEFAULT = "/work/data/etsys"
RAW_DATA_LOCATION_DEFAULT = "/work/data/rawdata"

RESOURCE_LOCATION_DEFAULT = "/work/software/mnvruncontrol/resources"

# Socket communication defaults.
DISPATCHER_PORT = 1098

MNVONLINE0 = "mnvonline0.fnal.gov"
MNVONLINE1 = "mnvonline1.fnal.gov"
MNVONLINEMASTER = "mnvonlinemaster.fnal.gov"

# dispatcher process details
DISPATCHER_PIDFILE = "/tmp/rc_dispatcher.pid"
#DISPATCHER_LOGFILE = "/work/data/logs/dispatcher_" + time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()) + ".log"
DISPATCHER_LOGFILE = "/work/data/logs/dispatcher.log"

# environment configuration
DAQROOT_DEFAULT = "/work/software/mnvonline/mnvdaq"

