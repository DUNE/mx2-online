"""
   Defaults.py:
    Default values for the various modules in the run control software.
    They are centralized here for easier modification of the setup.
   
    Original author: J. Wolcott (jwolcott@fnal.gov)
                     Feb.-Apr. 2010
                    
    Address all complaints to the management.
"""

from mnvruncontrol.configuration import MetaData

# general stuff
NOTIFY_ADDRESSES = ["jwolcott@fnal.gov",]

CONFIG_DB_NAME = "run_control_config.db"
CONFIG_DB_LOCATION = "/work/conditions"

LOGFILE_GATE_COUNT_INTERVAL = 50	# the master log file will get a notice every this many gates

# Data acquisition properties.
EVENT_SIZE                = 2048 
FRAMES                    = 4
NUM_FEBS                  = 509				# full detector
DAQ_HEADER_VERSION_STRING = "v09"

# LI settings
LI_ONE_PE_VOLTAGE    = 5.07   # from Brandon Eberly (eberly@fnal.gov), 3/5/2010
LI_MAX_PE_VOLTAGE    = 12.07  # currently the maximum the LI box can output.
ENABLE_LI            = False
LI_WAIT_FOR_RESPONSE = True

# Front-end properties
BLINK_INTERVAL                = 2		# in seconds
BELL_INTERVAL                 = 10	# in seconds
FRONTEND_MAX_TRIGGER_INTERVAL = 5  # in minutes
FRONTEND_LISTEN_PORT          = 3000
RESOURCE_LOCATION_DEFAULT     = "/work/software/mnvruncontrol/resources"
FRONTEND_PID_FILE             = "/tmp/runcontrol.pid"

# logging!
FRONTEND_LOGFILE_DEFAULT    = "/tmp/runcontrol.log"
LOGFILE_LOCATION_DEFAULT    = "/work/data/logs"
OM_LOGFILE_LOCATION_DEFAULT = "/work/logs"
OM_DISPATCHER_LOGFILE       = "%s/om_dispatcher.log" % OM_LOGFILE_LOCATION_DEFAULT
PO_LOGFILE_DEFAULT          = "/work/data/logs/postoffice.log"
RC_LOGFILE_DEFAULT          = "%s/runcontrol.log" % LOGFILE_LOCATION_DEFAULT

# Socket communication defaults.
DISPATCHER_PORT     = 1098
ET_PORT_BASE        = 1201
MASTER_PORT         = 1090
NUM_ET_PORTS_TO_USE = 50

CONNECTION_ATTEMPT_INTERVAL = 0.5	# in seconds
MAX_CONNECTION_ATTEMPTS     = 3
MESSAGE_TIMEOUT             = 5  # in seconds

# various dispatcher file locations
ET_SYSTEM_LOCATION_DEFAULT           = "/work/data/etsys"
LAST_TRIGGER_FILE                    = "/work/conditions/last_trigger.dat"
MASTER_DISPATCHER_PIDFILE            = "/work/conditions/daqmgr_dispatcher.pid"
MTEST_INSTALL_LOCATION               = "/home/nuhep/daq"
MTEST_DATA_LOCATION                  = "/home/nuhep/daq/DATA"
MTEST_DISPATCHER_PIDFILE             = "/tmp/beamline_dispatcher.pid"
MTEST_LOGFILE_LOCATION               = "/work/logs"
MTEST_DISPATCHER_LOGFILE             = "%s/beamline_dispatcher.log" % MTEST_LOGFILE_LOCATION
OM_DISPATCHER_PIDFILE                = "/tmp/om_dispatcher.pid"
OM_GAUDI_OUTPUTOPTIONSFILE           = "/work/conditions/outputfilenames.opts" # use "/minerva/data/online_processing/swap_area/outputfilenames.opts" on mnvnearline1
OM_GAUDI_INPUTOPTIONSFILE            = "/work/conditions/inputfilenames.opts"  #     "/minerva/data/online_processing/swap_area/inputfilenames.opts"
OM_DATAFILE_LOCATION_DEFAULT         = "/work/data/rawdata"                    #     "/minerva/data/online_processing/swap_area"
RAW_DATA_LOCATION_DEFAULT            = "/work/data/rawdata"
READOUT_DISPATCHER_PIDFILE           = "/work/conditions/readout_dispatcher.pid"
READOUT_DISPATCHER_LOGFILE           = "/work/data/logs/readout_dispatcher.log"
RUN_SERIES_DB_LOCATION_DEFAULT       = "/work/conditions/run_series"
RUN_SUBRUN_DB_LOCATION_DEFAULT       = "/work/conditions/next_run_subrun.db"
SAM_FILE_LOCATION                    = "/work/data/sam"
SLOWCONTROL_CONFIG_LOCATION_DEFAULT  = "/work/conditions/MParamFiles/data/DAQ/hardware_config"

# master node
MASTER_ADMIN_PWD           = "rcadmin"
MASTER_CONTROL_XFER_WAIT   = 15			# in seconds
MASTER_MAX_DAQ_ERROR_COUNT = 3
HW_INIT_LEVEL              = MetaData.HardwareInitLevels.FULL_HW_INIT.hash
DETECTOR_TYPE              = MetaData.DetectorTypes.MINERVA.hash
REMOTE_NODE_ADDRESSES      = []
ALLOWED_HV_THRESHOLDS      = {200: 0}	# that is, { threshold : num allowed over that threshold, ... }
ALLOWED_PERIOD_THRESHOLD   = 15000
HV_IGNORE_FEBS             = []

# mtest configuration
MTEST_BRANCH             = 1
MTEST_CRATE              = 0
MTEST_TYPE               = 1
MTEST_MEM_SLOT           = 8
MTEST_GATE_SLOT          = 18
MTEST_ADC_SLOT           = 3
MTEST_TDC_SLOT           = 2
MTEST_TOF_RST_GATE_SLOT  = 18
MTEST_PCOS_RST_GATE_SLOT = 20

# monitoring
OM_GAUDI_RUNCURRENTJOB = True
OM_GAUDI_RUNDSTJOBS    = True
OM_DST_TARGET_PATH     = "/minerva/data/users/minerva/data_processing/dst"		# where DSTs are copied when they're done being created by the dispatcher
OM_DST_MIN_JOB_TIME    = 10		# the minimum amount of time a DSTMaker job can take (anything shorter and mail is sent to NOTIFY_ADDRESSES)
OM_CONDOR_HOST         = "mnvnearline1.fnal.gov"
OM_MAX_CONDOR_BACKLOG  = 2		# max number of jobs that can be backlogged in the Condor queue
OM_USE_CONDOR          = False

# readout nodes
SLOWCONTROL_NUM_WRITE_ATTEMPTS       = 3
SLOWCONTROL_BEAM_FILE                = "beam.hwcfg"
SLOWCONTROL_LI_FILE                  = "li.hwcfg"
SLOWCONTROL_LI_DISCRIMINATORS_FILE   = "li_with_discriminators.hwcfg"
