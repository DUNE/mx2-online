"""
   Defaults.py:
    Default values for the various modules in the run control software.
    They are centralized here for easier modification of the setup.
   
    Original author: J. Wolcott (jwolcott@fnal.gov)
                     Feb.-Apr. 2010
                    
    Address all complaints to the management.
"""

# Data acquisition properties.
EVENT_SIZE = 2048 
FRAMES = 5

# LI settings
LI_ONE_PE_VOLTAGE = 5.07		# from Brandon Eberly (eberly@fnal.gov), 3/5/2010
LI_MAX_PE_VOLTAGE = 12.07	# currently the maximum the LI box can output.

# Run control properties.
CONFIG_DB_NAME = "run_control_config.db"
CONFIG_DB_LOCATION = "/work/conditions"

RUN_SERIES_DB_LOCATION_DEFAULT = "/work/conditions/run_series"
RUN_SUBRUN_DB_LOCATION_DEFAULT = "/work/conditions/next_run_subrun.db"
LOGFILE_LOCATION_DEFAULT = "/work/data/logs"
RC_LOGFILE_DEFAULT = LOGFILE_LOCATION_DEFAULT + "/runcontrol.log"

ET_SYSTEM_LOCATION_DEFAULT = "/work/data/etsys"
RAW_DATA_LOCATION_DEFAULT = "/work/data/rawdata"

RESOURCE_LOCATION_DEFAULT = "/work/software/mnvruncontrol/resources"
DAQMGR_SESSION_FILE = "/work/conditions/daqmgr_session.dat"

LOGFILE_NAME_PATTERN = "^(?P<detector>\w\w)_(?P<run>\d{8})_(?P<subrun>\d{4})_(?P<type>\w{5})_v\d+_(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})_Controller(?P<controller>[01])Log.txt$"

# Socket communication defaults.
DISPATCHER_PORT     = 1098
MASTER_PORT         = 1090
ET_PORT_BASE        = 1091
NUM_ET_PORTS_TO_USE = 4

SOLDIER = "mnvonline0.fnal.gov"
WORKER  = "mnvonline1.fnal.gov"
#MASTER  = "mnvonlinemaster.fnal.gov"
MASTER = "localhost"
MONITOR = "mnvnearline1.fnal.gov"

MAX_CONNECTION_ATTEMPTS = 3
CONNECTION_ATTEMPT_INTERVAL = 0.5	# in seconds
SOCKET_TIMEOUT = 2.5  # in seconds

# number of times in a row to log the same request
# in the dispatcher before suppressing
MAX_REPEATED_REQUEST_LOGS = 5

# dispatcher process details
READOUT_DISPATCHER_PIDFILE = "/work/conditions/readout_dispatcher.pid"
READOUT_DISPATCHER_LOGFILE = "/work/data/logs/readout_dispatcher.log"
OM_DISPATCHER_PIDFILE = "/tmp/om_dispatcher.pid"
OM_LOGFILE_LOCATION_DEFAULT = "/work/logs"
OM_DISPATCHER_LOGFILE = "%s/om_dispatcher.log" % OM_LOGFILE_LOCATION_DEFAULT
OM_GAUDI_OPTIONSFILE = "/home/nearonline/output.opts"
OM_DATAFILE_LOCATION_DEFAULT = "/home/nearonline/data"
MTEST_INSTALL_LOCATION = "/home/nuhep/daq"
MTEST_DATA_LOCATION = "/home/nuhep/daq/DATA"
MTEST_DISPATCHER_PIDFILE = "/tmp/beamline_dispatcher.pid"
MTEST_LOGFILE_LOCATION = "/work/logs"
MTEST_DISPATCHER_LOGFILE = "%s/beamline_dispatcher.log" % MTEST_LOGFILE_LOCATION

# mtest configuration
MTEST_BRANCH=1
MTEST_CRATE=0
MTEST_TYPE=1
MTEST_MEM_SLOT=8
MTEST_GATE_SLOT=18

# monitoring
OM_DST_TARGET_PATH = "/minerva/data/users/minerva/data_processing/dst"		# where DSTs are copied when they're done being created by the dispatcher

# slow control
SLOWCONTROL_CONFIG_LOCATION_DEFAULT = "/work/conditions/MParamFiles/data/DAQ/hardware_config"
SLOWCONTROL_ALLOWED_HV_THRESHOLDS = {300: 0, 100: 3, 60: 15}	# that is, { threshold : num allowed over that threshold, ... }
SLOWCONTROL_ALLOWED_PERIOD_THRESHOLD = 15000
SLOWCONTROL_NUM_WRITE_ATTEMPTS = 3
SLOWCONTROL_BEAM_FILE              = "beam.hwcfg"
SLOWCONTROL_LI_FILE                = "li.hwcfg"
SLOWCONTROL_LI_DISCRIMINATORS_FILE = "li_with_discriminators.hwcfg"
 
