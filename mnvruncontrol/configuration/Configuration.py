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

configuration = { "Front end"        : { "runinfoFile"             : ( Defaults.RUN_SUBRUN_DB_LOCATION_DEFAULT,       "Run/subrun info database file",                   str   ),
                                         "ResourceLocation"        : ( Defaults.RESOURCE_LOCATION_DEFAULT,            "Resource files location",                         str   ),
                                         "runSeriesLocation"       : ( Defaults.RUN_SERIES_DB_LOCATION_DEFAULT,       "Run series file location",                        str   ),
                                         "logFileLocations"        : ( [],                                            "Where to look for log files",                     list  ),
                                         "notificationInterval"    : ( Defaults.NOTIFICATION_INTERVAL,                "Interval between alert notifications (s)",        float ),
                                         "readoutNodes"            : ( [],                                            "Readout nodes",                                   list  ),
                                         "monitorNodes"            : ( [],                                            "Online monitoring nodes",                         list  ),
                                         "mtestbeamNodes"          : ( [],                                            "MTest beam DAQ nodes",                            list  )  },

                  "Hardware"         : { "eventFrames"             : ( Defaults.FRAMES,                               "Number of frames in an event",                    int   ),
                                         "frameSize"               : ( Defaults.EVENT_SIZE,                           "Size of one frame (bytes)",                       int   ),
                                         "LIBoxEnabled"            : ( True,                                          "LI box is enabled",                               bool  ),
                                         "LIBoxWaitForResponse"    : ( True,                                          "Wait for response from LI box",                   bool  )  },

                  "Socket setup"     : { "dispatcherPort"          : ( Defaults.DISPATCHER_PORT,                      "Dispatcher port number",                          int   ),
                                         "masterPort"              : ( Defaults.MASTER_PORT,                          "Master port number",                              int   ),
                                         "etPortBase"              : ( Defaults.ET_PORT_BASE,                         "ET port number base",                             int   ),
                                         "numETports"              : ( Defaults.NUM_ET_PORTS_TO_USE,                  "Number of ET ports to use",                       int   ),
                                         "maxConnectionAttempts"   : ( Defaults.MAX_CONNECTION_ATTEMPTS,              "Max number of consecutive connection attempts",   int   ),
                                         "connAttemptInterval"     : ( Defaults.CONNECTION_ATTEMPT_INTERVAL,          "Interval between connection attempts (s)",        float ),
                                         "socketTimeout"           : ( Defaults.SOCKET_TIMEOUT,                       "Socket timeout (s)",                              float )  },
                                         
                  "Dispatchers"      : { "maxRepeatedRequestLogs"  : ( Defaults.MAX_REPEATED_REQUEST_LOGS,            "Max number of consecutive same requests logged",  int   )  },
                  
                  "Master node"      : { "master_logfileLocation"  : ( Defaults.LOGFILE_LOCATION_DEFAULT,             "Run control (frontend) log file location",        str   ),
                                         "master_logfileName"      : ( Defaults.RC_LOGFILE_DEFAULT,                   "Run control (frontend) log file name",            str   ),
                                         "etSystemFileLocation"    : ( Defaults.ET_SYSTEM_LOCATION_DEFAULT,           "ET system file location",                         str   ),
                                         "sessionfile"             : ( Defaults.DAQMGR_SESSION_FILE,                  "Where to store the DAQ manager session file",     str   ),
                                         "master_rawdataLocation"  : ( Defaults.RAW_DATA_LOCATION_DEFAULT,            "Raw data location (master node)",                 str   )  },

                  "Readout nodes"    : { "readout_rawdataLocation" : ( Defaults.RAW_DATA_LOCATION_DEFAULT,            "Raw data location (readout nodes)",               str   ),
                                         "readout_PIDfileLocation" : ( Defaults.READOUT_DISPATCHER_PIDFILE,           "Readout dispatcher PID file location",            str   ),
                                         "readout_logfileLocation" : ( Defaults.LOGFILE_LOCATION_DEFAULT,             "Readout log file location",                       str   ),
                                         "readout_logfileName"     : ( Defaults.READOUT_DISPATCHER_LOGFILE,           "Readout log file name",                           str   ),
                                         "SCfileLocation"          : ( Defaults.SLOWCONTROL_CONFIG_LOCATION_DEFAULT,  "Slow control HW file location",                   str   ),
                                         "SCBeamFile"              : ( Defaults.SLOWCONTROL_BEAM_FILE,                "'Beam' HW configuration file",                    str   ),
                                         "SCLIFile"                : ( Defaults.SLOWCONTROL_LI_FILE,                  "'Light injection' HW configuration file",         str   ),
                                         "SCLIDiscriminatorsFile"  : ( Defaults.SLOWCONTROL_LI_DISCRIMINATORS_FILE,   "'LI with discriminators' HW configuration file",  str   ),
                                         "SCHVthresholds"          : ( Defaults.SLOWCONTROL_ALLOWED_HV_THRESHOLDS,    "Slow control HV warning thresholds (ADC counts)", list  ),
                                         "SCperiodThreshold"       : ( Defaults.SLOWCONTROL_ALLOWED_PERIOD_THRESHOLD, "Slow control period warning threshold",           int   ),
                                         "SCHWwriteAttempts"       : ( Defaults.SLOWCONTROL_NUM_WRITE_ATTEMPTS,       "Max number of attempts to write HW",              int   )  },
                  
                  "Monitoring nodes" : { "om_PIDfileLocation"      : ( Defaults.OM_DISPATCHER_PIDFILE,                "OM dispatcher PID file location",                 str   ),
                                         "om_logfileLocation"      : ( Defaults.OM_LOGFILE_LOCATION_DEFAULT,          "OM dispatcher log file location",                 str   ),
                                         "om_logfileName"          : ( Defaults.OM_DISPATCHER_LOGFILE,                "OM dispatcher log file name",                     str   ),
                                         "om_GaudiOptionsFile"     : ( Defaults.OM_GAUDI_OPTIONSFILE,                 "OM Gaudi process options file",                   str   ),
                                         "om_DSTTargetPath"        : ( Defaults.OM_DST_TARGET_PATH,                   "Copy target for DSTs created by OM dispather",    str   ),
                                         "om_rawdataLocation"      : ( Defaults.OM_DATAFILE_LOCATION_DEFAULT,         "OM raw data location",                            str   )  },

                  "MTest beam nodes" : { "mtest_PIDfileLocation"   : ( Defaults.MTEST_DISPATCHER_PIDFILE,             "MTest dispatcher PID file location",              str   ),
                                         "mtest_installLocation"   : ( Defaults.MTEST_INSTALL_LOCATION,               "MTest software installation location",            str   ),
                                         "mtest_dataLocation"      : ( Defaults.MTEST_DATA_LOCATION,                  "MTest beamline data location",                    str   ),
                                         "mtest_logfileLocation"   : ( Defaults.MTEST_LOGFILE_LOCATION,               "MTest dispatcher log file location",              str   ),
                                         "mtest_logfileName"       : ( Defaults.MTEST_DISPATCHER_LOGFILE,             "MTest dispatcher log file name",                  str   )  }  }


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
# on the command line.  (e.g. maybe there's no '/work' directory.)
# if none is supplied, we use the default from Defaults.
user_specified_db = None
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
locations_to_try = [os.path.abspath(Defaults.CONFIG_DB_NAME), "%s/%s" % (Defaults.CONFIG_DB_LOCATION, Defaults.CONFIG_DB_NAME)]
if user_specified_db is not None:
	locations_to_try = [user_specified_db] + locations_to_try
	
config_file_inaccessible = True
for location in locations_to_try:
	try:
		db = shelve.open(location, "r")
	except anydbm.error:
		pass
	else:
		config_file_inaccessible = False
		break

if not config_file_inaccessible:
	for param_set in params:
		for param_name in params[param_set]:
			try:
				params[param_set][param_name] = db[param_name]
			except KeyError:
				pass		# the default is already set
else:
	print "Note: configuration file is inaccessible.  Defaults are in use."

