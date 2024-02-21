"""
  DAQConfiguration.py:
   Encapsulates and stores configuration parameters
   for the DAQ (sent to the appropriate nodes during
   preparation for data taking).  Also used to
   communicate configuration between the master node
   and front-end clients.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    July-August 2010
                    
   Address all complaints to the management.
"""

import shelve
import dbm		# if a shelve database doesn't exist, this module contains the error raised

from mnvruncontrol.configuration import Configuration
from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData

# these keys are special because the value stored
# in the last run for them is irrelevant.  all that matters is
# what's in the Configuration.
_exceptions = { "detector" : MetaData.DetectorTypes[Configuration.params["mstr_detectorType"]],
                "hw_init"  : MetaData.HardwareInitLevels[Configuration.params["mstr_hwInitLevel"]],
                "num_crocs" : Configuration.params["hw_numCROCs"] }

class DAQConfiguration:
	""" Wraps the run-time detector configuration. """

	default_config = { "run"                      : 1,
	                   "subrun"                   : 1,
	                   
	                   "et_port"                  : Configuration.params["sock_etPortBase"],
	                   "et_filename"              : "etsysfile",

	                   "hw_init"                  : MetaData.HardwareInitLevels.FULL_HW_INIT,
	                   "detector"                 : MetaData.DetectorTypes.MINERVA,
	                   "is_single_run"            : True,
	                   "num_gates"                : 25,
	                   "num_crocs"                : Defaults.NUM_CROCS,
	                   "run_mode"                 : MetaData.RunningModes.ONE_SHOT,
	                   "hw_config"                : MetaData.HardwareConfigurations.NOFILE,
	                   "force_hw_reload"          : False,
	                   "led_groups"               : MetaData.LEDGroups.ABCD,
	                   "li_level"                 : MetaData.LILevels.ZERO_PE,
	                   "run_series"               : MetaData.RunSeriesTypes.PEDESTAL,

	                   "mtest_use_beam_DAQ"       : True,
	                   "mtest_branch"             : Defaults.MTEST_BRANCH,
	                   "mtest_crate"              : Defaults.MTEST_CRATE,
	                   "mtest_type"               : Defaults.MTEST_TYPE,
	                   "mtest_mem_slot"           : Defaults.MTEST_MEM_SLOT,
	                   "mtest_gate_slot"          : Defaults.MTEST_GATE_SLOT,
	                   "mtest_adc_slot"           : Defaults.MTEST_ADC_SLOT,
	                   "mtest_tdc_slot"           : Defaults.MTEST_TDC_SLOT,
	                   "mtest_tof_rst_gate_slot"  : Defaults.MTEST_TOF_RST_GATE_SLOT,
	                   "mtest_pcos_rst_gate_slot" : Defaults.MTEST_PCOS_RST_GATE_SLOT,	

	                   "auto_close"               : True,
	                   "auto_start_series"        : True }
	

	def __init__(self):
          self.Load()
          
	def Validate(self):
		# notice that the user can't freely specify hw_init or detector:
		# they must match what's in the configuration DB
#		print     (isinstance(self.run, int) and self.run > 0) 
#		print (isinstance(self.subrun, int) and self.subrun > 0) 
#		print (isinstance(self.et_port, int) and self.et_port - Configuration.params["sock_etPortBase"] in range(Configuration.params["sock_numETports"])) 
#		print self.hw_init == Configuration.params["mstr_hwInitLevel"] 
#		print self.detector == Configuration.params["mstr_detectorType"] 
#		print isinstance(self.is_single_run, bool) 
#		print (isinstance(self.num_gates, int) and self.num_gates > 0) 
#		print self.run_mode in MetaData.RunningModes 
#		print self.hw_config in MetaData.HardwareConfigurations 
#		print self.led_groups in MetaData.LEDGroups 
#		print self.li_level in MetaData.LILevels 
#		print self.run_series in MetaData.RunSeriesTypes 
#		print isinstance(self.mtest_use_beam_DAQ, bool) 
#		print isinstance(self.mtest_branch, int) 
#		print isinstance(self.mtest_crate, int) 
#		print isinstance(self.mtest_type, int) 
#		print isinstance(self.mtest_mem_slot, int) 
#		print isinstance(self.mtest_gate_slot, int) 
#		print isinstance(self.mtest_adc_slot, int) 
#		print isinstance(self.mtest_tdc_slot, int) 
#		print isinstance(self.mtest_tof_rst_gate_slot, int) 
#		print isinstance(self.mtest_pcos_rst_gate_slot, int) 
#		print isinstance(self.auto_close, bool) 
#		print isinstance(self.auto_start_series, bool)

		exceptions_pass = True
		for key in _exceptions:
			if not self.__dict__[key] == _exceptions[key]:
				exceptions_pass = False
				break

		return exceptions_pass \
		       and (isinstance(self.run, int) and self.run > 0) \
		       and (isinstance(self.subrun, int) and self.subrun > 0) \
		       and (isinstance(self.et_port, int) and self.et_port - Configuration.params["sock_etPortBase"] in range(Configuration.params["sock_numETports"])) \
		       and isinstance(self.is_single_run, bool) \
		       and (isinstance(self.num_gates, int) and self.num_gates > 0) \
		       and self.run_mode in MetaData.RunningModes \
		       and self.hw_config in MetaData.HardwareConfigurations \
		       and isinstance(self.force_hw_reload, bool) \
		       and self.led_groups in MetaData.LEDGroups \
		       and self.li_level in MetaData.LILevels \
		       and self.run_series in MetaData.RunSeriesTypes \
		       and isinstance(self.mtest_use_beam_DAQ, bool) \
		       and isinstance(self.mtest_branch, int) \
		       and isinstance(self.mtest_crate, int) \
		       and isinstance(self.mtest_type, int) \
		       and isinstance(self.mtest_mem_slot, int) \
		       and isinstance(self.mtest_gate_slot, int) \
		       and isinstance(self.mtest_adc_slot, int) \
		       and isinstance(self.mtest_tdc_slot, int) \
		       and isinstance(self.mtest_tof_rst_gate_slot, int) \
		       and isinstance(self.mtest_pcos_rst_gate_slot, int) \
		       and isinstance(self.auto_close, bool) \
		       and isinstance(self.auto_start_series, bool)

	def Load(self, filepath=None):
		""" Loads the config. from the default location
		    or (if filepath is not None) the specified file. """
		
		run_info_file = Configuration.params["mstr_runinfoFile"] if filepath is None else filepath
		db = None
	
		try:
			db = shelve.open(run_info_file, 'r')
		except dbm.error:
			pass
			
		has_all_keys = True
		for key in list(DAQConfiguration.default_config.keys()):
	
			if key in _exceptions:
				self.__dict__[key] = _exceptions[key]
			else:
				try:
					#if db is not None and db.has_key(key) and type(db[key]) == type(DAQConfiguration.default_config[key]):
					if db is None: raise KeyError()
					if key not in db: raise KeyError()
					if type(db[key]) != type(DAQConfiguration.default_config[key]): raise KeyError()
					self.__dict__[key] = db[key]
				except (KeyError, Exception) as e:
					if type(e) != KeyError:
						import pprint
						print("Got exception,")
						pprint.pprint(e)
						print("For key,")
						pprint.pprint(key)
					self.__dict__[key] = DAQConfiguration.default_config[key]
					has_all_keys = False
		
		if not has_all_keys:
			print("The database storing the last run configuration data appears to be missing or corrupted.  Default configuration will be used for any unreadable values...")
		#	print 'load: key=',key
		#	print 'run_info_file =', run_info_file
		if db is not None:
			db.close()
		
	def Save(self, filepath=None):
		""" Saves the config to a shelve database
		    in the default location or (if filepath
		    is not None) the specified file. """
		run_info_file = Configuration.params["mstr_runinfoFile"] if filepath is None else filepath
		   
		try:
			db = shelve.open(run_info_file)
			for key in list(DAQConfiguration.default_config.keys()):
				db[key] = self.__dict__[key]
			db.close()
		except:
			raise FileError

class FileError(Exception):
	pass	
