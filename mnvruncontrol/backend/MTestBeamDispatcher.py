"""
  MTestBeamDispatcher.py:
   Listener service that starts the beamline DAQ for
   the test beam DAQ at MTest.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Apr. 2010
                    
   Address all complaints to the management.
   
   How to use:
   The MTestDispatcher is for all the stuff you want to start that isn't on the main detector.
   There are two types of processes to start.
   1) A process at the start of a subrun that runs before a subrun starts. Call it type 1
   2) A process that runs during a subrun and ends when the subrun ends. Call it type 2
   
   Type 1 processes can run before or after starting type 2 processes. Put the relevant code in either  
   initialize_subrun or initialize_subrun_after_daq_threads to start before or after respectively. 
   You can put any python code in there or run a subprocess. The simplest code to run a subprocess is,
   	subprocess.call(shlex.split("<INSERT COMMAND HERE; DO NOT SOURCE; ONLY EXECUTE>"))
   
   Type 2 processes run continuously during a run. Type 2 processes need to be added to the 
   MTestBeamDispatcher.daq_threads and MTestBeamDispatcher.daq_starters dictionaries in
   the initalize function. As the dictionary key, you need the name of your thread.
   The daq_starters needs a function to run that accepts a message. See,
   	MTestBeamDispatcher.start_example(self, message)
   	
   The daq_starter function needs to return a DAQThread object. Use the
   MTestBeamDispatcher.startDAQThread(command, thread_name) 
   to get a DAQThread and automatically enter info into the log file.
   The command is any command you'd like to run.
   The thread name is going to be the name of a log file,
   	/work/logs/mtestdist_<name>_thread.log
   (The MTestDispatcher log file is on mnvtb03,
      /work/logs/mtest_dispatcher.log)
   The thread's log file will contain all the output of your thread
   and works with subprocess.Popen. It's configured to catch all the output,
   so if your output ends suddenly then it's because you didn't output past that point.
   	
   When a subrun finishes, the MTestDispatcher sends a SIGTERM signal to tell
   the type 2 process to finish. It should be configured to stop when it gets this signal.
   Some processes make child processes and its difficult to get the signal to 
   the child. To get around this, we've added a section in the 
   DAQThread.terminate_and_join function. Just check that the processname is
   the right one, and then run your special code (again: do not source when
   using the subprocess function).
"""

import subprocess
import threading
import signal
import shlex
import time
import sys
import os
import logging
import time
import select
import errno

import mnvruncontrol.configuration.Logging

from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend.Dispatcher import Dispatcher

from mnvruncontrol.backend.PostOffice.Routing import PostOffice, MessageTerminus
from mnvruncontrol.backend.PostOffice.Envelope import Subscription, Message

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
		                        
		#self.pidfilename = Configuration.params["mtest_PIDfileLocation"]
		self.pidfilename = Configuration.params["mtst_PIDfile"]
		                   
		self.daq_threads =  { "example" : None,
				      "mwpc" : None, 
				      "camac" : None } 
		#self.daq_threads =  { "example" : None,
		#		      "mwpc" : None} 
		#self.daq_threads =  { "example" : None,
		#		      "camac" : None} 
		#self.daq_threads =  { "example" : None,}
		self.daq_starters = { "wire chamber": self.start_wire_chamber,
		                      "tof":          self.start_tof,
		                      "example" : self.start_example,
		                      "mwpc" : self.start_mwpc,
				      "camac" : self.start_camac }
		self.logger.info('MTestBeamDispatcher started: mwpc and camac')

	def BookSubscriptions(self):
		
		# *** self.postoffice is None until after _Start so this needed moving from __init__ ***
		
		# we need to know when the DAQ manager goes up or down,
		# as well as when online monitoring is supposed to start or stop
		handlers = { Subscription(subject="mgr_status", action=Subscription.DELIVER, delivery_address=self) : self.daq_mgr_status_handler,
		             Subscription(subject="mtest_directive", action=Subscription.DELIVER, delivery_address=self) : self.mtest_directive_handler }
                #             Subscription(subject="lock_request", action=Subscription.DELIVER, delivery_address=self) : self._LockHandler} # TODO delete line
		
		for subscription in handlers:
			self.postoffice.AddSubscription(subscription)
			self.AddHandler(subscription, handlers[subscription])

	def daq_mgr_status_handler(self, message):
		""" Method to respond to changes in status of the
		    DAQ manager (books subscriptions, etc.). """
                #self.logger.info("Testing if _daq_mgr_status_update exists")
                #assert hasattr(self, "_daq_mgr_status_update")
		#self._daq_mgr_status_update(self, message, ["mtest_directive",])		    
                self.logger.info("Testing: starting daq_mgr_status_handler function")
                if not hasattr(self, "DAQMgrStatusUpdate"):
                        self.logger.warning("Whoa, I'm missing self.DAQMgrStatusUpdate for some reason")
                else: self.logger.info("I guess I'm not missing it")
                if not ( hasattr(message, "status") and hasattr(message, "mgr_id") ):
                        self.logger.warning("I'm missing attributes: \n%s" % message)
                try:
                        self.logger.info("Running self.DAQMgrStatusUpdate")
                        self.DAQMgrStatusUpdate(message, ["mtest_directive",])
                except Exception as e:
                        self.logger.warning("I got the following error: \n%s" % e)
                        raise
                self.logger.info("Testing: finished daq_mgr_status_handler function")



	def mtest_directive_handler(self, message):
		""" Deals with incoming directives for the MTest beam node. """
                self.logger.info("mtest_directive_handler got the following message \n%s" % message)
		
		if not ( hasattr(message, "directive") and hasattr(message, "mgr_id") ):
			self.logger.info("MTest directive message is improperly formatted.  Ignoring...")
			return

		response = message.ResponseMessage()
		if message.mgr_id in self.identities:
			response.sender = self.identities[message.mgr_id]
		
		status = True
		if not self.ClientAllowed(message.mgr_id):
			response.subject = "not_allowed"
		else:
			if message.directive == "start" or message.directive == "beamdaq_start" or message.directive == "daq_start":
				status = self.beamdaq_start(message)
			
			elif message.directive == "stop" or message.directive == "beamdaq_stop" or message.directive == "daq_stop" :
				status = self.beamdaq_stop()
				'''if status == False:
					status = True # returns false if it finished
				elif status == True:
					status = False'''
		
			if status is None:
				response.subject = "invalid_request"
			else:
				response.subject = "request_response"
				response.success = status
                self.logger.info("mtest_directive_handler is sending the following response \n%s" % response)
		self.postoffice.Publish(response)
			

	def beamdaq_start(self, message):
		""" Starts the test beam DAQ services as subprocesses. """
		    
		self.logger.info("Manager wants to start the beamline DAQ processes.")
		
		# the configuration that must be passed for this message to do anything.
		must_haves = ["et_filename", "num_gates", "run_mode"] # any items that must be in the message  
		
		for item in must_haves:          
			if not hasattr(message, item):
				self.logger.info("Missing %s from 'must_haves' so I'm ignoring this message\n%s" % (item, message))
				return None

		# first clear up any old processes.
		for thread in self.daq_threads:
			if self.daq_threads[thread] is not None and self.daq_threads[thread].is_alive():
				self.logger.info("Clearing up old threads first...")
				
				if not self.beamdaq_stop():
					return False
		
		# need some initialization stuff...
		self.initialize_subrun(message)
		
		
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
		'''self.logger.info(" Will release gate inhibit in 3 seconds.")
		timer = threading.Timer(3, self.gate_inhibit, (message, False) )
		timer.start()'''
		self.initialize_subrun_after_daq_threads(message)
				
		return True
		
	def initialize_subrun(self, message):
		self.logger.info("Initializing stuff for the subrun.")
		self.example_start_of_subrun(message)
		
	def initialize_subrun_after_daq_threads(self, message):
		self.logger.info("Initializing stuff for the subrun after starting daq threads.")
		
	
	def crate_initialize(self, message):
		self.logger.info("  ==> Initializing the crate...")
		#subprocess.call("%s/camac/example/cz %s %s %s" % (Configuration.params["mtst_installLocation"], message.branch, message.crate, message.type), shell=True)
		
	def gate_inhibit(self, message, inhibit_status):
		self.logger.info("  ==> Sending a gate inhibit command: inhibit " + ("on" if inhibit_status == True else "off"))
		inhibit_status = 1 if inhibit_status == True else 0
		#subprocess.call("%s/misc/gateinhibit/gate_inhibit %s %s %s %s %d" % (Configuration.params["mtst_installLocation"], message.branch, message.crate, message.type, message.gate_slot, inhibit_status), shell=True)
	
	def start_wire_chamber(self, message):
		""" Starts the wire chamber process.
		
		    Returns a DAQThread containing the subprocess it was started in. """
		    
		command = "%s/PCOS/PCOS_readout_sync %s %s %s %s %s %s %s %s %s %s" % (Configuration.params["mtst_installLocation"], message.branch, message.crate, message.mem_slot, message.type, message.wc_rst_gate_slot, message.num_events, message.filepattern, message.run, message.subrun, message.runmode)
		return self.startDAQThread(command, "wire chamber")

	def start_tof(self, message):
		""" Starts the time-of-flight process.
		
		    Returns a DAQThread containing the subprocess it was started in. """
		    
		command = "%s/tof/src/run_rik_t977_sync %s %s %s %s %s %s %s %s %s %s" % (Configuration.params["mtst_installLocation"], message.branch, message.crate, message.tdc_slot, message.adc_slot, message.tof_rst_gate_slot, message.num_events, message.filepattern, message.run, message.subrun, message.runmode)
		return self.startDAQThread(command, "tof")
		
	def example_start_of_subrun(self, message):
		''' This code only gets run at the start of a subrun and doesn't run concurrently. See below for an example of a command that keeps running. '''
		self.logger.info("Running example initialize code")
		subprocess.call("ls -al", shell=True)
		
	def start_example(self, message):
		""" Starts my example script which will run until the subrun ends.
			It keeps going until it gets a sigterm. """
	    
		command = "python /home/nfs/minerva/mnvruncontrol/backend/SimpleMTestDispatcherScript.py %s" % (Configuration.params["mtst_installLocation"])
		return self.startDAQThread(command, "example")
		
		
	def start_mwpc(self, message):
		""" Starts MwpcMinerva """
		if message.run_mode not in ("cosmc", ):
			self.logger.info("Not starting mwpc because %s is the wrong run mode." % message.run_mode)
			return None # must return a DAQThread object or none
		command = "/home/nfs/minerva/daq/runMwpcMinerva.sh %s %s" % (message.et_filename, message.num_gates)
		return self.startDAQThread(command, "mwpc")

	def start_camac(self, message):
		""" Starts CAMACMinerva """
		command = "/home/nfs/minerva/daq/runCAMACMinerva.sh %s %s" % (message.et_filename, message.num_gates)
		return self.startDAQThread(command, "camac")
		
	def startDAQThread(self, command, name):
		""" This makes sure every daq thread is started similarly with a log file entry. """
		self.logger.info("  ==> Using command: '%s'" % command)
		return DAQThread(command, name, self)
	
	def beamdaq_stop(self):
		""" Stops the beamline DAQ processes. """
		    
		self.logger.info("Manager wants to stop the beamline DAQ processes.")
		
		for thread in self.daq_threads:
			if self.daq_threads[thread] and self.daq_threads[thread].is_alive():
				self.logger.info("   ==> Attempting to stop the %s DAQ thread." % thread)
				try:
					self.daq_threads[thread].terminate_and_join()
				except Exception as excpt:
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
	def __init__(self, command, processname, parent):
		threading.Thread.__init__(self)
		
		self.process = None
		self.command = command
		self.processname = processname
		
		self.parent = parent
		
		self.daemon = True
		
		self.start()		# inherited from threading.Thread.  starts run() in a separate thread.
		
	def run(self):

		# redirect any output to a log file
		filename = "%s/mtestdisp_%s_thread.log" % (Configuration.params["mtst_logfileLocation"], self.processname)
		with open(filename, "w") as fileobj:
			try:
				fileobj.write("Will run the following command:\n%s\n" % self.command)
				# start the process
				# note that shlex.split doesn't understand Unicode...
				self.process = subprocess.Popen(shlex.split(str(self.command)),
					close_fds=True,
					shell=False,
					stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT)
				self.pid = self.process.pid		# less typing.
			
				done = False
				while not done:
					done = self.process.poll() is not None
					ready = False
					data = None
					try:
						ready = select.select([self.process.stdout], [], [], 0)
					except select.error as xxx_todo_changeme:
						(errnum, msg) = xxx_todo_changeme.args
						if errnum == errno.EINTR: continue
						else: raise
					if ready:
						try:
							data = os.read(self.process.stdout.fileno(), 1024)
						except OSError: continue
					#output, discarded = self.process.stdout.read()
					if data is not None: 
						fileobj.write(data)
						fileobj.flush()
						os.fsync(fileobj.fileno())

					if not done: time.sleep(0.1)

				# now wait until the process finishes
				# and write its output to the log file
				#output, discarded = self.process.communicate()
				#fileobj.write(output)
			except Exception as e:
				fileobj.write("\nCaught exception in MTestDispatcher.py in the '%s' thread:\n" % self.processname)
				import traceback
				tb = sys.exc_info()[2]
				textlist = traceback.format_exception(e.__class__, e, tb)
				text = "".join(textlist)
				fileobj.write(text)
				fileobj.write("\nEnd exception in MTestDispatcher.py\n")
				
				error_text = "Process '%s' quit early.\n%s" % (self.processname, text)
				message = Message(subject="beamdaq_status", state="mtst_error", sender=self.parent.identities[self.parent.lock_id], error=error_text)
				self.parent.postoffice.Publish(msg)
				fileobj.write("\nFinished publishing the message about this exception to the post office\n")
			
	def terminate_and_join(self):
		if self.processname == "mwpc":
			# could put special code here if needed.
			code = subprocess.call(shlex.split( "/home/nfs/minerva/mnvruncontrol/backend/kill_mwpc.sh"), shell=True)
			if code != 0:
				raise Exception("Return code was %s" % code)
		if self.processname == "camac":
			# could put special code here if needed.
			code = subprocess.call(shlex.split( "/home/nfs/minerva/mnvruncontrol/backend/kill_camac.sh"), shell=True)
			if code != 0:
				raise Exception("Return code was %s" % code)
		self.process.terminate()
		self.join()		# 'merges' this thread with the other one so that we wait until it's done.
		
                        
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
	dispatcher.Bootstrap()
	
	sys.exit(0)
	
else:
	raise RuntimeError("This module is not designed to be imported!")
