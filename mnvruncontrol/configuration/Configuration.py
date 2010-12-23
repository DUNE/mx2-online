"""
   Configuration.py:
    A module that handles the configuration of the run control.

    It's basically just a mapping from the constants in the
    Defaults module to some nice names that are overridden
    by the values stored in the config database.  This loading
    is done transparently to the user.

    The module also specifies succinct text descriptions of each of the elements
    (used, for example, in the RunControlConfiguration script).
   
    Original author: J. Wolcott (jwolcott@fnal.gov)
                     Apr. 2010
                    
    Address all complaints to the management.
"""

# n.b. this file is much easier to look at and/or edit on a wide-ish screen (>150 character width) ...

import sys
import shelve
import anydbm
import os.path

from mnvruncontrol.configuration import Defaults

# convention for variable names is as follows:
#
# pfx_variableName
#
# where 'pfx' is the prefix corresponding to the category
# the variable belongs to (see the 'categories' dictionary, below)
# and the variableName contains no underscores.
# (The prefix is included in the variable name so that someone
#  examining the database they're stored in can tell at a glance
#  which category the variable belongs to, without having to open
#  up this file.)
#
# entries are as follows:
#    "pfx_variableName" : ( Defaults.DEFAULT_VALUE, "Short text description",  type )

configuration = {
	# generalities
	"gen_notifyAddresses"         : ( Defaults.NOTIFY_ADDRESSES,                     "Email addresses to notify of problems",               list  ),

	# front-end stuff
	"frnt_resourceLocation"       : ( Defaults.RESOURCE_LOCATION_DEFAULT,            "Resource files location",                             str   ),
	"frnt_listenPort"             : ( Defaults.FRONTEND_LISTEN_PORT,                 "Frontend client listener port",                       int   ),
	"frnt_PIDfile"                : ( Defaults.FRONTEND_PID_FILE,                    "Frontend client PID file location",                   str   ),
	"frnt_maxTriggerInterval"     : ( Defaults.FRONTEND_MAX_TRIGGER_INTERVAL,        "Max interval between triggers before warning (m)",    float ),
	"frnt_bellInterval"           : ( Defaults.BELL_INTERVAL,                        "Interval between alert bells (s)",                    float ),
	"frnt_blinkInterval"          : ( Defaults.BLINK_INTERVAL,                       "Interval between alert blinks (s)",                   float ),

	# hardware
	"hw_eventFrames"              : ( Defaults.FRAMES,                               "Number of frames in an event",                        int   ),
	"hw_frameSize"                : ( Defaults.EVENT_SIZE,                           "Size of one frame (bytes)",                           int   ),
	"hw_numFEBs"                  : ( Defaults.NUM_FEBS,                             "Number of FEBs being read out",                       int   ),
	"hw_LIBoxEnabled"             : ( Defaults.ENABLE_LI,                            "LI box is enabled",                                   bool  ),
	"hw_LIBoxWaitForResponse"     : ( Defaults.LI_WAIT_FOR_RESPONSE,                 "Wait for response from LI box",                       bool  ),

	# socket config
	"sock_dispatcherPort"         : ( Defaults.DISPATCHER_PORT,                      "Dispatcher port number",                              int   ),
	"sock_masterPort"             : ( Defaults.MASTER_PORT,                          "Master port number",                                  int   ),
	"sock_etPortBase"             : ( Defaults.ET_PORT_BASE,                         "ET port number base",                                 int   ),
	"sock_numETports"             : ( Defaults.NUM_ET_PORTS_TO_USE,                  "Number of ET ports to use",                           int   ),
	"sock_maxConnectionAttempts"  : ( Defaults.MAX_CONNECTION_ATTEMPTS,              "Max number of consecutive connection attempts",       int   ),
	"sock_connAttemptInterval"    : ( Defaults.CONNECTION_ATTEMPT_INTERVAL,          "Interval between connection attempts (s)",            float ),
	"sock_messageTimeout"         : ( Defaults.MESSAGE_TIMEOUT,                      "Message timeout (s)",                                 float ),
		                
	# log files
	"log_OM"                      : ( Defaults.OM_DISPATCHER_LOGFILE,                "OM dispatcher log file name",                         str   ),
	"log_readout"                 : ( Defaults.READOUT_DISPATCHER_LOGFILE,           "Readout log file name",                               str   ),
	"log_PO"                      : ( Defaults.PO_LOGFILE_DEFAULT,                   "Post office log file name",                           str   ),
	"log_frontend"                : ( Defaults.FRONTEND_LOGFILE_DEFAULT,             "Where to put the frontend log file",                  str   ),
	"log_master"                  : ( Defaults.RC_LOGFILE_DEFAULT,                   "Master node log file name",                           str   ),
	"log_mtest"                   : ( Defaults.MTEST_DISPATCHER_LOGFILE,             "MTest dispatcher log file name",                      str   ),

	# master node stuff
	"mstr_PIDfile"                : ( Defaults.MASTER_DISPATCHER_PIDFILE,            "DAQ manager dispatcher PID file",                     str   ),
	"mstr_runinfoFile"            : ( Defaults.RUN_SUBRUN_DB_LOCATION_DEFAULT,       "Run/subrun info database file",                       str   ),
	"mstr_logfileGateCount"       : ( Defaults.LOGFILE_GATE_COUNT_INTERVAL,          "Interval to write gate count to log file",            int   ),
	"mstr_etSystemFileLocation"   : ( Defaults.ET_SYSTEM_LOCATION_DEFAULT,           "ET system file location",                             str   ),
	"mstr_hwInitLevel"            : ( Defaults.HW_INIT_LEVEL,                        "Hardware init level",                                 int   ),
	"mstr_detectorType"           : ( Defaults.DETECTOR_TYPE,                        "Detector type",                                       int   ),
	"mstr_nodeAddresses"          : ( Defaults.REMOTE_NODE_ADDRESSES,                "Nodes to notify when DAQ manager is ready",           list  ),   
	"mstr_HVignoreFEBs"           : ( Defaults.HV_IGNORE_FEBS,                       "FEBs whose HV thresholds shouldn't be checked",       list  ),   
	"mstr_runSeriesLocation"      : ( Defaults.RUN_SERIES_DB_LOCATION_DEFAULT,       "Run series file location",                            str   ),
	"mstr_HVthresholds"           : ( Defaults.ALLOWED_HV_THRESHOLDS,                "Slow control HV warning thresholds (ADC counts)",     dict  ),
	"mstr_HVperiodThreshold"      : ( Defaults.ALLOWED_PERIOD_THRESHOLD,             "Slow control period warning threshold",               int   ),
	"mstr_rawdataLocation"        : ( Defaults.RAW_DATA_LOCATION_DEFAULT,            "Raw data location (master node)",                     str   ),

	# readout nodes
	"read_rawdataLocation"        : ( Defaults.RAW_DATA_LOCATION_DEFAULT,            "Raw data location (readout nodes)",                   str   ),
	"read_PIDfile"                : ( Defaults.READOUT_DISPATCHER_PIDFILE,           "Readout dispatcher PID file",                         str   ),
	"read_logfileLocation"        : ( Defaults.LOGFILE_LOCATION_DEFAULT,             "Readout log file location",                           str   ),
	"read_SAMfileLocation"        : ( Defaults.SAM_FILE_LOCATION,                    "Location of SAM files",                               str   ),
	"read_lastTriggerFile"        : ( Defaults.LAST_TRIGGER_FILE,                    "Location and filename of last trigger file",          str   ),
	"read_SCfileLocation"         : ( Defaults.SLOWCONTROL_CONFIG_LOCATION_DEFAULT,  "Slow control HW file location",                       str   ),
	"read_SCBeamFile"             : ( Defaults.SLOWCONTROL_BEAM_FILE,                "'Beam' HW configuration file name",                   str   ),
	"read_SCLIFile"               : ( Defaults.SLOWCONTROL_LI_FILE,                  "'Light injection' HW configuration file name",        str   ),
	"read_SCLIDiscriminatorsFile" : ( Defaults.SLOWCONTROL_LI_DISCRIMINATORS_FILE,   "'LI with discriminators' HW configuration file name", str   ),
	"read_HWwriteAttempts"        : ( Defaults.SLOWCONTROL_NUM_WRITE_ATTEMPTS,       "Max number of attempts to write HW",                  int   ),

	# monitoring nodes
	"mon_PIDfile"                 : ( Defaults.OM_DISPATCHER_PIDFILE,                "OM dispatcher PID file",                              str   ),
	"mon_logfileLocation"         : ( Defaults.OM_LOGFILE_LOCATION_DEFAULT,          "Monitoring job log file location",                    str   ),
	"mon_runCurrentJob"           : ( Defaults.OM_GAUDI_RUNCURRENTJOB,               "Run the 'current' monitoring job?",                   bool  ),
	"mon_runDSTjobs"              : ( Defaults.OM_GAUDI_RUNDSTJOBS,                  "Run the DST jobs?",                                   bool  ),
	"mon_GaudiOutputOptionsFile"  : ( Defaults.OM_GAUDI_OUTPUTOPTIONSFILE,           "OM Gaudi process 'output file' options file",         str   ),
	"mon_GaudiInputOptionsFile"   : ( Defaults.OM_GAUDI_INPUTOPTIONSFILE,            "OM Gaudi process 'input file' options file",          str   ),
	"mon_DSTTargetPath"           : ( Defaults.OM_DST_TARGET_PATH,                   "Copy target for DSTs created by OM dispather",        str   ),
	"mon_DSTminJobTime"           : ( Defaults.OM_DST_MIN_JOB_TIME,                  "Minimum time DST job must be alive (s)",              float ),
	"mon_useCondor"               : ( Defaults.OM_USE_CONDOR,                        "Use a Condor queue?",                                 bool  ),
	"mon_condorHost"              : ( Defaults.OM_CONDOR_HOST,                       "The machine hosting the Condor queue manager",        str   ),
	"mon_maxCondorBacklog"        : ( Defaults.OM_MAX_CONDOR_BACKLOG,                "Max number of jobs backlogged in Condor queue",       int   ),
	"mon_rawdataLocation"         : ( Defaults.OM_DATAFILE_LOCATION_DEFAULT,         "OM raw data location",                                str   ),

	# mtest beam nodes
	"mtst_PIDfile"                : ( Defaults.MTEST_DISPATCHER_PIDFILE,             "MTest dispatcher PID file location",                  str   ),
	"mtst_installLocation"        : ( Defaults.MTEST_INSTALL_LOCATION,               "MTest software installation location",                str   ),
	"mtst_dataLocation"           : ( Defaults.MTEST_DATA_LOCATION,                  "MTest beamline data location",                        str   ),
	"mtst_logfileLocation"        : ( Defaults.MTEST_LOGFILE_LOCATION,               "MTest dispatcher log file location",                  str   )  }


# mapping from the variable prefixes to the categories they belong in
prefixes = { "frnt": "Front end",
             "gen" : "General",
             "hw"  : "Hardware",
             "log" : "Log file locations",
             "mstr": "Master node",
             "mon" : "Monitoring nodes",
             "read": "Readout nodes",
             "sock": "Socket setup",
             "mtst": "MTest beam nodes"  }

categories = {}
for prefix in prefixes:
	categories[prefixes[prefix]] = []

##################################################################################################

def SaveToDB():
	""" Save the current parameter set to the database. """
	
	if config_file_inaccessible:
		return
	
	db = shelve.open(config_file_location, "c")
	
	for param in params:
		db[param] = types[param](params[param])
			
	db.close()

	print "Wrote configuration to '%s'." % config_file_location

def LoadFromDB():
	""" Load the configuration from the specified DB.
	
	    This is used when the module is first loaded,
	    but also can be called to reload the configuration
	    later on.  Helpful if you don't want to restart
	    your program but want to take advantage of new
	    configuration options in the config file. """
	
	# need to specify that 'params' is global,
	# otherwise we'll be setting a local version of it
	# in this function that will disappear when the
	# function ends
	global params

	if not (config_file_inaccessible or config_file_empty):
		db = shelve.open(config_file_location, "r")
		for param in params:
			try:
				params[param] = db[param]
			except KeyError:
				pass		# the default is already set
		db.close()
	else:
		print "Note: configuration file is empty or inaccessible.  Defaults are in use..."

##################################################################################################

# module globals
user_specified_db = None
config_file_inaccessible = True
config_file_empty = False
config_file_location = None

params = {}
names = {}
types = {}

# which file to use?
# first, we check if the user passed a location for the main config DB
# in the environment or on the command line.
# (e.g. maybe there's no '/work' directory.)
# if none is supplied, we use the default from Defaults.
if os.getenv("RC_CONFIG_PATH") is not None:
	user_specified_db = os.getenv("RC_CONFIG_PATH")

if "-c" in sys.argv:
	index = sys.argv.index("-c")
	if index >= len(sys.argv) - 1:
		sys.stderr.write(" Error: '-c' must be followed by path to config db (e.g., '-c ~/config/rc_config.db')\n\n")
		sys.exit(1)
	try:
		user_specified_db = os.path.abspath(sys.argv[index + 1])
	except:
		pass
	# remove "-c" and its argument from the argument list
	# so that optparse doesn't barf on it in other modules
	del sys.argv[index + 1]
	del sys.argv[index]

# now look in the specified location (or, if that's not
# set, the default); if nothing's there or it can't be opened,
# try the current directory.
locations_to_try = ["%s/%s" % (Defaults.CONFIG_DB_LOCATION, Defaults.CONFIG_DB_NAME),]
if user_specified_db is not None:
#	print "trying user-specified DB: ", user_specified_db
	locations_to_try = [user_specified_db,] + locations_to_try

for location in locations_to_try:
	try:
		db = shelve.open(location, "r")
		db.close()
	except anydbm.error:
		try:
			db = shelve.open(location, "c")
			db.close()
		except anydbm.error as e:
			pass
		else:
			config_file_location = location
			config_file_inaccessible = False
			config_file_empty = True
			break
	else:
#		print "using location: ", location
		config_file_location = location
		config_file_inaccessible = False
		break


# the basic list is structured a bit deep
# (though it's nice for entering data).
# below it's reworked for easier access
# (can write Configuration.params[]...
#  in other modules that import this one).

for param in configuration:
	params[param] = configuration[param][0]
	names[param]  = configuration[param][1]
	types[param]  = configuration[param][2]

# mostly for the benefit of the run control configuration script:
# a mapping from the category names to the variables in that category
for param in configuration:
	prefix = param.split("_")[0]
	categories[prefixes[prefix]].append(param)

# load 'em up!
LoadFromDB()

