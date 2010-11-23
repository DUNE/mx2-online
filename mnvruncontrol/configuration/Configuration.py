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

# n.b. this file is much easier to look at and/or edit on a wide-ish screen ...

import sys
import shelve
import anydbm
import os.path

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData

configuration = { "General"          : { "notify_addresses"          : ( Defaults.NOTIFY_ADDRESSES,                     "Email addresses to nofity of problems",            list  )  },

                  "Front end"        : { "ResourceLocation"          : ( Defaults.RESOURCE_LOCATION_DEFAULT,            "Resource files location",                          str   ),
                                         "frontend_listenPort"       : ( Defaults.FRONTEND_LISTEN_PORT,                 "Frontend client listener port",                    int   ),
                                         "maxTriggerInterval"        : ( Defaults.FRONTEND_MAX_TRIGGER_INTERVAL,        "Max interval between triggers before warning (m)", float ),
                                         "bellInterval"              : ( Defaults.BELL_INTERVAL,                        "Interval between alert bells (s)",                 float ),
                                         "blinkInterval"             : ( Defaults.BLINK_INTERVAL,                       "Interval between alert blinks (s)",                float ), },

                  "Hardware"         : { "eventFrames"               : ( Defaults.FRAMES,                               "Number of frames in an event",                     int   ),
                                         "frameSize"                 : ( Defaults.EVENT_SIZE,                           "Size of one frame (bytes)",                        int   ),
                                         "num_FEBs"                  : ( Defaults.NUM_FEBS,                             "Number of FEBs being read out",                    int   ),
                                         "LIBoxEnabled"              : ( True,                                          "LI box is enabled",                                bool  ),
                                         "LIBoxWaitForResponse"      : ( True,                                          "Wait for response from LI box",                    bool  )  },

                  "Socket setup"     : { "dispatcherPort"            : ( Defaults.DISPATCHER_PORT,                      "Dispatcher port number",                           int   ),
                                         "masterPort"                : ( Defaults.MASTER_PORT,                          "Master port number",                               int   ),
                                         "etPortBase"                : ( Defaults.ET_PORT_BASE,                         "ET port number base",                              int   ),
                                         "numETports"                : ( Defaults.NUM_ET_PORTS_TO_USE,                  "Number of ET ports to use",                        int   ),
                                         "maxConnectionAttempts"     : ( Defaults.MAX_CONNECTION_ATTEMPTS,              "Max number of consecutive connection attempts",    int   ),
                                         "connAttemptInterval"       : ( Defaults.CONNECTION_ATTEMPT_INTERVAL,          "Interval between connection attempts (s)",         float ),
                                         "messageTimeout"            : ( Defaults.MESSAGE_TIMEOUT,                      "Message timeout (s)",                              float )  },
                                         
                  "Logging"          : { "om_logfileName"            : ( Defaults.OM_DISPATCHER_LOGFILE,                "OM dispatcher log file name",                      str   ),
                                         "master_logfileLocation"    : ( Defaults.LOGFILE_LOCATION_DEFAULT,             "DAQ manager log file location",                    str   ),
                                         "readout_logfileName"       : ( Defaults.READOUT_DISPATCHER_LOGFILE,           "Readout log file name",                            str   ),
                                         "PO_logfileName"            : ( Defaults.PO_LOGFILE_DEFAULT,                   "Post office log file name",                        str   ),
                                         "frontend_logfileName"      : ( Defaults.FRONTEND_LOGFILE_DEFAULT,             "Where to put the frontend log file",               str   ),
                                         "master_logfileName"        : ( Defaults.RC_LOGFILE_DEFAULT,                   "Master node log file name",                        str   ),
                                         "mtest_logfileName"         : ( Defaults.MTEST_DISPATCHER_LOGFILE,             "MTest dispatcher log file name",                   str   )  },
                  
                  "Master node"      : { "master_PIDfileLocation"    : ( Defaults.MASTER_DISPATCHER_PIDFILE,            "DAQ manager dispatcher PID file location",         str   ),
                                         "runinfoFile"               : ( Defaults.RUN_SUBRUN_DB_LOCATION_DEFAULT,       "Run/subrun info database file",                    str   ),
                                         "logfileGateCount"          : ( Defaults.LOGFILE_GATE_COUNT_INTERVAL,          "Interval to write gate count to log file",         int   ),
                                         "etSystemFileLocation"      : ( Defaults.ET_SYSTEM_LOCATION_DEFAULT,           "ET system file location",                          str   ),
                                         "hwInitLevel"               : ( MetaData.HardwareInitLevels.FULL_HW_INIT.hash, "Hardware init level",                              int   ),
                                         "detectorType"              : ( MetaData.DetectorTypes.MINERVA.hash,           "Detector type",                                    int   ),
                                         "nodeAddresses"             : ( [],                                            "Nodes to notify when DAQ manager is ready",        list  ),   
                                         "runSeriesLocation"         : ( Defaults.RUN_SERIES_DB_LOCATION_DEFAULT,       "Run series file location",                         str   ),
                                         "master_rawdataLocation"    : ( Defaults.RAW_DATA_LOCATION_DEFAULT,            "Raw data location (master node)",                  str   )  },

                  "Readout nodes"    : { "readout_rawdataLocation"   : ( Defaults.RAW_DATA_LOCATION_DEFAULT,            "Raw data location (readout nodes)",                str   ),
                                         "readout_PIDfileLocation"   : ( Defaults.READOUT_DISPATCHER_PIDFILE,           "Readout dispatcher PID file location",             str   ),
                                         "readout_logfileLocation"   : ( Defaults.LOGFILE_LOCATION_DEFAULT,             "Readout log file location",                        str   ),
                                         "SAMfileLocation"           : ( Defaults.SAM_FILE_LOCATION,                    "Location of SAM files",                            str   ),
                                         "lastTriggerFile"           : ( Defaults.LAST_TRIGGER_FILE,                    "Location and filename of last trigger file",       str   ),
                                         "SCfileLocation"            : ( Defaults.SLOWCONTROL_CONFIG_LOCATION_DEFAULT,  "Slow control HW file location",                    str   ),
                                         "SCBeamFile"                : ( Defaults.SLOWCONTROL_BEAM_FILE,                "'Beam' HW configuration file",                     str   ),
                                         "SCLIFile"                  : ( Defaults.SLOWCONTROL_LI_FILE,                  "'Light injection' HW configuration file",          str   ),
                                         "SCLIDiscriminatorsFile"    : ( Defaults.SLOWCONTROL_LI_DISCRIMINATORS_FILE,   "'LI with discriminators' HW configuration file",   str   ),
                                         "SCHVthresholds"            : ( Defaults.SLOWCONTROL_ALLOWED_HV_THRESHOLDS,    "Slow control HV warning thresholds (ADC counts)",  dict  ),
                                         "SCperiodThreshold"         : ( Defaults.SLOWCONTROL_ALLOWED_PERIOD_THRESHOLD, "Slow control period warning threshold",            int   ),
                                         "SCHWwriteAttempts"         : ( Defaults.SLOWCONTROL_NUM_WRITE_ATTEMPTS,       "Max number of attempts to write HW",               int   )  },
                  
                  "Monitoring nodes" : { "om_PIDfileLocation"        : ( Defaults.OM_DISPATCHER_PIDFILE,                "OM dispatcher PID file location",                  str   ),
                                         "om_logfileLocation"        : ( Defaults.OM_LOGFILE_LOCATION_DEFAULT,          "OM dispatcher log file location",                  str   ),
                                         "om_GaudiOutputOptionsFile" : ( Defaults.OM_GAUDI_OUTPUTOPTIONSFILE,           "OM Gaudi process 'output file' options file",      str   ),
                                         "om_GaudiInputOptionsFile"  : ( Defaults.OM_GAUDI_INPUTOPTIONSFILE,            "OM Gaudi process 'input file' options file",       str   ),
                                         "om_DSTTargetPath"          : ( Defaults.OM_DST_TARGET_PATH,                   "Copy target for DSTs created by OM dispather",     str   ),
                                         "om_DSTminJobTime"          : ( Defaults.OM_DST_MIN_JOB_TIME,                  "Minimum time DST job must be alive (s)",           float ),
                                         "om_useCondor"              : ( False,                                         "Use a Condor queue?",                              bool  ),
                                         "om_condorHost"             : ( Defaults.OM_CONDOR_HOST,                       "The machine hosting the Condor queue manager",     str   ),
                                         "om_maxCondorBacklog"       : ( Defaults.OM_DST_MIN_JOB_TIME,                  "Minimum time DST job must be alive (s)",           float ),
                                         "om_rawdataLocation"        : ( Defaults.OM_DATAFILE_LOCATION_DEFAULT,         "OM raw data location",                             str   )  },

                  "MTest beam nodes" : { "mtest_PIDfileLocation"     : ( Defaults.MTEST_DISPATCHER_PIDFILE,             "MTest dispatcher PID file location",               str   ),
                                         "mtest_installLocation"     : ( Defaults.MTEST_INSTALL_LOCATION,               "MTest software installation location",             str   ),
                                         "mtest_dataLocation"        : ( Defaults.MTEST_DATA_LOCATION,                  "MTest beamline data location",                     str   ),
                                         "mtest_logfileLocation"     : ( Defaults.MTEST_LOGFILE_LOCATION,               "MTest dispatcher log file location",               str   )  }  }


def SaveToDB():
	""" Save the current parameter set to the database. """
	
	if config_file_inaccessible:
		return
	
	db = shelve.open(config_file_location, "c")
	
	for param_set in params:
		for param in params[param_set]:
			db[param] = types[param_set][param](params[param_set][param])
			
	db.close()

	print "Wrote configuration to '%s'." % config_file_location

# the basic dictionary is structured a bit deep
# (though it's nice for entering data).
# below it's reworked for easier access
# (can write Configuration.params[]... in other modules).

params = {}
names = {}
types = {}

for param_set in configuration:
	params[param_set] = {}
	names[param_set] = {}
	types[param_set] = {}
	for param_name in configuration[param_set]:
		params[param_set][param_name] = configuration[param_set][param_name][0]
		names[param_set][param_name]  = configuration[param_set][param_name][1]
		types[param_set][param_name]  = configuration[param_set][param_name][2]


# first, we check if the user passed a location for the main config DB
# in the environment or on the command line.
# (e.g. maybe there's no '/work' directory.)
# if none is supplied, we use the default from Defaults.
user_specified_db = None
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

# now update using any values that are set in the DB.
# first look in the specified location (or, if that's not
# set, the default); if nothing's there or it can't be opened,
# try the current directory.
locations_to_try = ["%s/%s" % (Defaults.CONFIG_DB_LOCATION, Defaults.CONFIG_DB_NAME),]
if user_specified_db is not None:
#	print "trying user-specified DB: ", user_specified_db
	locations_to_try = [user_specified_db,] + locations_to_try
	
config_file_inaccessible = True
config_file_empty = False
config_file_location = None
for location in locations_to_try:
	try:
		db = shelve.open(location, "r")
	except anydbm.error:
		try:
			db = shelve.open(location, "c")
		except anydbm.error as e:
			pass
		else:
			config_file_inaccessible = False
			config_file_empty = True
			break
	else:
#		print "using location: ", location
		config_file_location = location
		config_file_inaccessible = False
		break

if not (config_file_inaccessible or config_file_empty):
	for param_set in params:
		for param_name in params[param_set]:
			try:
				params[param_set][param_name] = db[param_name]
			except KeyError:
				pass		# the default is already set
	db.close()
else:
	print "Note: configuration file is inaccessible.  Defaults are in use..."
			
