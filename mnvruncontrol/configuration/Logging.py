"""
  Logging.py:
   Does the set-up of the various logging facilities
   used by mnvruncontrol.  
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    June 2010
                    
   Address all complaints to the management.
"""

import os
import logging
import logging.handlers

from mnvruncontrol.configuration import Configuration

# keep 30 days' worth of logs.
ROTATING_LOG_COMMON_CONFIG = {
	"when":        "midnight",
	"backupCount": 30,
	"delay":       True,
}

try:
	alreadyImported
except NameError:
	# set up the root logger to do nothing.
	# modules can add handlers as they wish.
	logging.basicConfig(filename=os.devnull)

	# now configure the loggers for the various services
	formatter = logging.Formatter("[%(asctime)s] %(levelname)8s:  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
	thread_formatter = logging.Formatter("[%(asctime)s] %(threadName)s %(levelname)8s:  %(message)s", datefmt="%H:%M:%S")

	# first, the generic dispatcher's console logger.
	# it's console-only (we add files for specific instances below).
	dispatcher_logger = logging.getLogger("Dispatcher")
	dispatcher_logger.setLevel(logging.DEBUG)
	consolehandler = logging.StreamHandler()
	consolehandler.setFormatter(formatter)
	consolehandler.setLevel(logging.DEBUG)
	dispatcher_logger.addHandler(consolehandler)

	# the online monitoring node
	om_logger = logging.getLogger("Dispatcher.OM")
	om_logger.setLevel(logging.INFO)
	om_filehandler = logging.handlers.TimedRotatingFileHandler(Configuration.params["log_OM"], **ROTATING_LOG_COMMON_CONFIG)
	om_filehandler.setFormatter(formatter)
	om_logger.addHandler(om_filehandler)

	# readout node
	readout_logger = logging.getLogger("Dispatcher.Readout")
	readout_logger.setLevel(logging.DEBUG)
	readout_filehandler = logging.handlers.TimedRotatingFileHandler(Configuration.params["log_readout"], **ROTATING_LOG_COMMON_CONFIG)
	readout_filehandler.setFormatter(formatter)
	readout_logger.addHandler(readout_filehandler)

	# MTest beamline DAQ node
	mtest_logger = logging.getLogger("Dispatcher.MTest")
	mtest_logger.setLevel(logging.INFO)
	mtest_filehandler = logging.handlers.TimedRotatingFileHandler(Configuration.params["log_mtest"], **ROTATING_LOG_COMMON_CONFIG)
	mtest_filehandler.setFormatter(formatter)
	mtest_logger.addHandler(mtest_filehandler)

	# DAQMgr
	daqmgr_logger = logging.getLogger("Dispatcher.DAQManager")
	daqmgr_logger.setLevel(logging.DEBUG)
	daqmgr_filehandler = logging.handlers.TimedRotatingFileHandler(Configuration.params["log_master"], **ROTATING_LOG_COMMON_CONFIG)
	daqmgr_filehandler.setFormatter(formatter)
	daqmgr_logger.addHandler(daqmgr_filehandler)


	# the post office
	PO_logger = logging.getLogger("PostOffice")

	PO_filehandler = logging.handlers.TimedRotatingFileHandler(Configuration.params["log_PO"], **ROTATING_LOG_COMMON_CONFIG)
	PO_logger.setLevel(logging.INFO)
	PO_filehandler.setLevel(logging.INFO)
	PO_filehandler.setFormatter(formatter)

# when you need to see all the gory details, these settings are helpful
# (use them instead of the corresponding lines in the block just above)
#	PO_filehandler = logging.FileHandler(Configuration.params["log_PO"], 'w')
#	PO_logger.setLevel(5)
#	PO_filehandler.setLevel(5)
#	PO_filehandler.setFormatter(thread_formatter)
	
	PO_logger.addHandler(PO_filehandler)
	
	# the frontend
	frontend_logger = logging.getLogger("Frontend")
	frontend_logger.setLevel(logging.DEBUG)
	frontend_filehandler = logging.handlers.TimedRotatingFileHandler(Configuration.params["log_frontend"], **ROTATING_LOG_COMMON_CONFIG)
	frontend_filehandler.setLevel(logging.DEBUG)
	frontend_filehandler.setFormatter(formatter)
	frontend_logger.addHandler(frontend_filehandler)
	
	
	alreadyImported = True

