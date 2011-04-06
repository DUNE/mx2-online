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
import shlex
import time
import sys
import os
import logging

import mnvruncontrol.configuration.Logging

from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend.Dispatcher import Dispatcher

class MTestBeamDispatcher(Dispatcher):
	"""
	MTest beam DAQ node dispatcher.  Starts and stops the beamline DAQ
	based on instructions received from the run control.
	"""
	def __init__(self):
		Dispatcher.__init__(self)
	
		self.logger = logging.getLogger("Dispatcher.MTest")

		# need to shut down the subprocesses...
		self.cleanup_methods += [self.beamdaq_stop]
		                        
		self.pidfilename = Configuration.params["mtest_PIDfileLocation"]
		                   
		self.daq_threads =  { "wire chamber": None, "tof": None}
		self.daq_starters = { "wire chamber": self.start_wire_chamber,
		                      "tof":          self.start_tof           }
		
		# we need to know when the DAQ manager goes up or down,
		# as well as when online monitoring is supposed to start or stop
		handlers = { PostOffice.Subscription(subject="mgr_status", action=PostOffice.Subscription.DELIVER, delivery_address=self) : self.daq_mgr_status_handler,
		             PostOffice.Subscription(subject="mtest_directive", action=PostOffice.Subscription.DELIVER, delivery_address=self) : self.mtest_directive_handler }
		
		for subscription in handlers:
			self.postoffice.AddSubscription(subscription)
			self.AddHandler(subscription, handlers[subscription])

	def daq_mgr_status_handler(self, message):
		""" Method to respond to changes in status of the
		    DAQ manager (books subscriptions, etc.). """

		self._daq_mgr_status_update(self, message, ["mtest_directive",])		    
	
	def mtest_directive_handler(self, message):
		""" Deals with incoming directives for the MTest beam node. """
		
		if not ( hasattr(message, "directive") and hasattr(message, "mgr_id") ):
			self.logger.info("MTest directive message is improperly formatted.  Ignoring...")
			return

		response = message.ResponseMessage()
		if message.mgr_id in self.identities:
			response.sender = self.identities[message.mgr_id]
		
		status = True
		if not self.client_allowed(message.mgr_id):
			response.subject = "not_allowed"
		else:
			if message.directive == "start":
				status = om_start(message)
			
			elif message.directive == "stop":
				status = om_stop()
		
			if status is None:
				response.subject = "invalid_request"
			else:
				response.subject = "request_response"
				response.success = status
		self.postoffice.Send(response)
			

	def beamdaq_start(self, message):
		""" Starts the test beam DAQ services as subprocesses. """
		    
		self.logger.info("Manager wants to start the beamline DAQ processes.")
		
		# the configuration that must be passed for this message to do anything.
		must_haves = [ "branch", "crate", "type", "mem_slot", "wc_rst_gate_slot", \
		               "num_events", "filepattern", "run", "subrun", "runmode", \
		               "tdc_slot", "adc_slot", "tof_rst_gate_slot" ]
		
		for item in must_haves:          
			if not hasattr(message, item):
				return None

		# first clear up any old processes.
		for thread in self.daq_threads:
			if self.daq_threads[thread] is not None and self.daq_threads[thread].is_alive():
				self.logger.info("Clearing up old threads first...")
				
				if not self.beamdaq_stop():
					return False
		
		# need some initialization stuff...
		self.crate_initialize(message)		# first, crate initialization
		self.gate_inhibit(message, True)		# then a gate inhibit (don't let it trigger gates while we're configuring...)
		
		# now start the DAQ processes
		for thread in self.daq_threads:
			try:
				self.logger.info("Trying to start the %s thread..." % thread )
				self.daq_threads[thread] = self.daq_starters[thread](message)
			except:
				self.logger.exception("  ==> failed.")
				return False
			else:
				self.logger.info("  ==> success.")
		
		# set a timer to cancel the gate inhibit in 3 seconds.
		self.logger.info(" Will release gate inhibit in 3 seconds.")
		timer = threading.Timer(3, self.gate_inhibit, (message, False) )
		timer.start()
				
		return True
	
	def crate_initialize(self, message):
		self.logger.info("  ==> Initializing the crate...")
		subprocess.call("%s/camac/example/cz %s %s %s" % (Configuration.params["mtest_installLocation"], message.branch, message.crate, message.type), shell=True)
		
	def gate_inhibit(self, message, inhibit_status):
		self.logger.info("  ==> Sending a gate inhibit command: inhibit " + ("on" if inhibit_status == True else "off"))
		inhibit_status = 1 if inhibit_status == True else 0
		subprocess.call("%s/misc/gateinhibit/gate_inhibit %s %s %s %s %d" % (Configuration.params["mtest_installLocation"], message.branch, message.crate, message.type, message.gate_slot, inhibit_status), shell=True)
	
	def start_wire_chamber(self, message):
		""" Starts the wire chamber process.
		
		    Returns a DAQThread containing the subprocess it was started in. """
		    
		command = "%s/PCOS/PCOS_readout_sync %s %s %s %s %s %s %s %s %s %s" % (Configuration.params["mtest_installLocation"], message.branch, message.crate, message.mem_slot, message.type, message.wc_rst_gate_slot, message.num_events, message.filepattern, message.run, message.subrun, message.runmode)
		self.logger.info("  ==> Using command: '%s'" % command)
		return DAQThread(command, "wire chamber")

	def start_tof(self, message):
		""" Starts the time-of-flight process.
		
		    Returns a DAQThread containing the subprocess it was started in. """
		    
		command = "%s/tof/src/run_rik_t977_sync %s %s %s %s %s %s %s %s %s %s" % (Configuration.params["mtest_installLocation"], message.branch, message.crate, message.tdc_slot, message.adc_slot, message.tof_rst_gate_slot, message.num_events, message.filepattern, message.run, message.subrun, message.runmode)
		self.logger.info("  ==> Using command: '%s'" % command)
		return DAQThread(command, "tof")
	
	def beamdaq_stop(self):
		""" Stops the beamline DAQ processes. """
		    
		self.logger.info("Manager wants to stop the beamline DAQ processes.")
		
		for thread in self.daq_threads:
			if self.daq_threads[thread] and self.daq_threads[thread].is_alive():
				self.logger.info("   ==> Attempting to stop the %s DAQ thread." % thread)
				try:
					self.daq_threads[thread].process.terminate()
					self.daq_threads[thread].join()		# 'merges' this thread with the other one so that we wait until it's done.
				except Exception, excpt:
					self.logger.error("   ==> DAQ process %s couldn't be stopped!" % thread)
					self.logger.exception("   ==> Error message:")
					return excpt

		self.logger.info("   ==> All stopped successfully.")
		
		return not True
		

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
		filename = "%s/%s.log" % (Configuration.params["mtest_logfileLocation"], self.processname)
		with open(filename, "w") as fileobj:
			# start the process
			# note that shlex.split doesn't understand Unicode...
			self.process = subprocess.Popen(shlex.split(str(self.command)),
				close_fds=True,
				shell=False,
				stdout=fileobj.fileno(),
				stderr=subprocess.STDOUT)
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
