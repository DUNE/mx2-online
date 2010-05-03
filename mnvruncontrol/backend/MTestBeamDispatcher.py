"""
  MTestBeamDispatcher.py:
   Listener service that starts the beamline DAQ for
   the test beam DAQ at MTest.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Apr. 2010
                    
   Address all complaints to the management.
"""

import subprocess
import threading
import signal
import time
import sys
import os
import logging
import logging.handlers

from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend.Dispatcher import Dispatcher

class MTestBeamDispatcher(Dispatcher):
	"""
	MTest beam DAQ node dispatcher.  Starts and stops the beamline DAQ
	based on instructions received from the run control.
	"""
	def __init__(self):
		Dispatcher.__init__(self)
	
		# Dispatcher() maintains a central logger.
		# We want a file output, so we'll set that up here.
		self.filehandler = logging.handlers.RotatingFileHandler(Configuration.params["MTest beam nodes"]["mtest_logfileName"], maxBytes=204800, backupCount=5)
		self.filehandler.setLevel(logging.INFO)
		self.filehandler.setFormatter(self.formatter)		# self.formatter is set up in the Dispatcher superclass
		self.logger.addHandler(self.filehandler)

		# we need to specify what requests we know how to handle.
		self.valid_requests += SocketRequests.MTestBeamRequests
		self.handlers.update( { "mtestbeam_start" : self.beamdaq_start,
		                        "mtestbeam_stop"  : self.beamdaq_stop } )

		# need to shut down the subprocesses...
		self.cleanup_methods += [self.beamdaq_stop]
		                        
		self.pidfilename = Configuration.params["MTest beam nodes"]["mtest_PIDfileLocation"]
		                   
		self.daq_threads =  { "wire chamber": None, "tof": None}
		self.daq_starters = { "wire chamber": self.start_wire_chamber,
		                      "tof":          self.start_tof           }
		

	def beamdaq_start(self, matches, show_details, **kwargs):
		""" Starts the test beam DAQ services as subprocesses.
		
		    Returns 0 on success, 1 on failure. """
		    
		if show_details:
			self.logger.info("Client wants to start the beamline DAQ processes.")

		# first clear up any old processes.
		for thread in self.daq_threads:
			if self.daq_threads[thread] is not None and self.daq_threads[thread].is_alive():
				self.logger.info("Clearing up old threads first...")
				success = self.beamdaq_stop() == "0"
				
				if not success:
					return "1"
				break
		
		# need some initialization stuff...
		self.crate_initialize(matches)		# first, crate initialization
		self.gate_inhibit(matches, True)		# then a gate inhibit (don't let it trigger gates while we're configuring...)
		
		# now start the DAQ processes
		for thread in self.daq_threads:
			try:
				self.logger.info("Trying to start the %s thread..." % thread )
				self.daq_threads[thread] = self.daq_starters[thread](matches)
			except:
				self.logger.exception("  ==> failed.")
				return "1"
			else:
				self.logger.info("  ==> success.")
		
		# set a timer to cancel the gate inhibit in 3 seconds.
		self.logger.info(" Will release gate inhibit in 3 seconds.")
		timer = threading.Timer(3, self.gate_inhibit, (matches, False) )
		timer.start()
				
		return "0"
	
	def crate_initialize(self, matches, **kwargs):
		self.logger.info("  ==> Initializing the crate...")
		subprocess.call("%s/camac/example/cz %s %s %s" % (Configuration.params["MTest beam nodes"]["mtest_installLocation"], matches.group("branch"), matches.group("crate"), matches.group("type")), shell=True)
		
	def gate_inhibit(self, matches, inhibit_status, **kwargs):
		self.logger.info("  ==> Sending a gate inhibit command: inhibit " + ("on" if inhibit_status == True else "off"))
		inhibit_status = 1 if inhibit_status == True else 0
		subprocess.call("%s/misc/gateinhibit/gate_inhibit %s %s %s %s %d" % (Configuration.params["MTest beam nodes"]["mtest_installLocation"], matches.group("branch"), matches.group("crate"), matches.group("type"), matches.group("gate_slot"), inhibit_status), shell=True)
	
	def start_wire_chamber(self, matches, **kwargs):
		""" Starts the wire chamber process.
		
		    Returns a DAQThread containing the subprocess it was started in. """
		    
		command = "%s/PCOS/PCOS_readout_sync %s %s %s %s %s %s %s %s %s %s" % (Configuration.params["MTest beam nodes"]["mtest_installLocation"], matches.group("branch"), matches.group("crate"), matches.group("mem_slot"), matches.group("type"), matches.group("wc_rst_gate_slot"), matches.group("num_events"), matches.group("filepattern"), matches.group("run"), matches.group("subrun"), matches.group("runmode"))
		self.logger.info("  ==> Using command: '%s'" % command)
		return DAQThread(command, "wire chamber")

	def start_tof(self, matches, **kwargs):
		""" Starts the time-of-flight process.
		
		    Returns a DAQThread containing the subprocess it was started in. """
		    
		command = "%s/tof/src/run_rik_t977_sync %s %s %s %s %s %s %s %s %s %s" % (Configuration.params["MTest beam nodes"]["mtest_installLocation"], matches.group("branch"), matches.group("crate"), matches.group("tdc_slot"), matches.group("adc_slot"), matches.group("tof_rst_gate_slot"), matches.group("num_events"), matches.group("filepattern"), matches.group("run"), matches.group("subrun"), matches.group("runmode"))
		self.logger.info("  ==> Using command: '%s'" % command)
		return DAQThread(command, "tof")
	
	def beamdaq_stop(self, matches=None, show_details=True, **kwargs):
		""" Stops the beamline DAQ processes. 
				    
		    Returns 0 on success and 1 on failure. """
		    
		if show_details:
			self.logger.info("Client wants to stop the beamline DAQ processes.")
		
		errors = False
		for thread in self.daq_threads:
			if self.daq_threads[thread] and self.daq_threads[thread].is_alive():
				if show_details:
					self.logger.info("   ==> Attempting to stop the %s DAQ thread." % thread)
				try:
					self.daq_threads[thread].process.terminate()
					self.daq_threads[thread].join()		# 'merges' this thread with the other one so that we wait until it's done.
				except Exception, excpt:
					self.logger.error("   ==> DAQ process %s couldn't be stopped!" % thread)
					self.logger.exception("   ==> Error message:")
					errors = True

		if show_details and not errors:
			self.logger.info("   ==> All stopped successfully.")
		
		return "0" if not errors else "1"
		

#########################
# DAQThread             #
#########################
class DAQThread(threading.Thread):
	""" Each DAQ process needs to be run in a separate thread
	    so that it doesn't hold up the dispatcher while it goes. """
	def __init__(self, command, processname):
		threading.Thread.__init__(self)
		
		self.process = None
		self.command = command
		self.processname = processname
		
		self.daemon = True
		
		self.start()		# inherited from threading.Thread.  starts run() in a separate thread.
		
	def run(self):

		# redirect any output to a log file
		filename = "%s/%s.log" % (Configuration.params["MTest beam nodes"]["mtest_logfileLocation"], self.processname)
		with open(filename, "w") as fileobj:
			# start the process
			self.process = subprocess.Popen(self.command.split(), shell=False, stdout=fileobj.fileno(), stderr=subprocess.STDOUT)
			self.pid = self.process.pid		# less typing.

			# now wait until the process finishes
			# (wait() returns the process's return code)
			self.returncode = self.process.wait()
		
                        
####################################################################
####################################################################
"""
  This module should probably never be imported elsewhere.
  It's designed to run directly as a background process that handles
  incoming requests for the online monitoring system.
  
  If it IS running as a stand-alone, it will need to daemonize
  and begin listening on the specified port (both of which are
  taken care of by the Dispatcher superclass's method bootstrap()).
  
  Otherwise this implementation will bail with an error.
"""
if __name__ == "__main__":
	dispatcher = MTestBeamDispatcher()
	dispatcher.bootstrap()
	
	sys.exit(0)
	
else:
	raise RuntimeError("This module is not designed to be imported!")
