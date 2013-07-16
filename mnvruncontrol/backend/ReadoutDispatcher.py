"""
  Package: mnvruncontrol
   The MINERvA run control
  
  File: RunControlDispatcher.py
  
  Notes:
   Listener service that runs on a DAQ slave ("soldier"
   or "worker" node in DAQ terminology) to manage
   the DAQ process and slow control.
   It inherits most of its functionality from Dispatcher.

  
  Original author: J. Wolcott (jwolcott@fnal.gov)
                   first version,  Feb.-Mar. 2010
                   second version, Aug. 2010
                    
  Address all complaints to the management.
"""
import subprocess
import threading
import shlex
import time
import copy
import sys
import re
import os
import os.path
import itertools
import logging
import logging.handlers

import mnvruncontrol.configuration.Logging

from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import Configuration
from mnvruncontrol.configuration import Defaults

from mnvruncontrol.backend import Dispatcher
from mnvruncontrol.backend import PostOffice
from mnvruncontrol.backend import LIBox

from mnvconfigurator.SlowControlE2cr2.SC_MainMethods import SC as SlowControl

#################################################
#  these are the return codes used by the DAQ
#  subprocess.  they're enumerated here so that
#  they are centralized and easy to change if
#  necessary.

class DAQ_EXIT_CODES:
	SENTINEL = 2
	NO_SENTINEL = 3
#################################################

class ReadoutDispatcher(Dispatcher.Dispatcher):
	"""
	This guy is the one who listens for requests and handles them.
	There should NEVER be more than one instance running at a time!
	(They wouldn't both be able to bind to the port...)  Thus the
	start() method checks before allowing dispatching to be started.
	"""
	def __init__(self):
		Dispatcher.Dispatcher.__init__(self)
		# the master slow control object.
		# it handles the interface with the hardware.
		# we can't initialize it here because it seems to
		# use file descriptors to interact with the hardware,
		# which means that during daemonization the
		# hardware link would get broken.
		# it will be initialized when used.
		self.slow_controls = []
		
		# the LI box object.
		# this one does all communication with the LI box
		# via an RS-232 (serial) interface provided by the
		# PySerial module.
		# again we wait to initialize it until it's needed.
		self.li_box = None

		self.logger = logging.getLogger("Dispatcher.Readout")

		self.cleanup_methods += [self.daq_stop]
		
		self.pidfilename = Configuration.params["read_PIDfile"]
		self.current_HW_file = "NOFILE"

		self.daq_thread = None

	def BookSubscriptions(self):
		""" Overrides Dispatcher's BookSubscriptions()
		    to do something useful here. """
		
		# we need to know when the DAQ manager goes up or down,
		# as well as when the DAQ on this node is supposed to start or stop
		handlers = { PostOffice.Subscription(subject="mgr_status", action=PostOffice.Subscription.DELIVER, delivery_address=self) : self.DAQMgrStatusHandler,
			        PostOffice.Subscription(subject="readout_directive", action=PostOffice.Subscription.DELIVER, delivery_address=self) : self.ReadoutDirectiveHandler }
	
		for subscription in handlers:
			self.postoffice.AddSubscription(subscription)
			self.AddHandler(subscription, handlers[subscription])


	def DAQMgrStatusHandler(self, message):
		""" Method to respond to changes in status of the
		    DAQ manager (books subscriptions, etc.). """

		self.DAQMgrStatusUpdate(message, ["readout_directive", ])		    
	
	def ReadoutDirectiveHandler(self, message):
		""" Handles incoming directives for a readout node. """
		
		self.logger.log(5, "Manager directive message:\n%s", message)
		
		if not ( hasattr(message, "directive") ):
			self.logger.info("Readout directive message is improperly formatted.  Ignoring...")
			return
		
		response = message.ResponseMessage()
		if hasattr(message, "mgr_id") and message.mgr_id in self.identities:
			response.sender = self.identities[message.mgr_id]
		else:
			response.sender = self.id
		
		# there are a few directives for which identification
		# and a lock are unnecessary, so we consider them first.
		if message.directive == "daq_running":
			response.daq_running = self.daq_status()
		elif message.directive == "daq_exit_status":
			response.daq_exit_status = self.daq_exitstatus()
		elif message.directive == "sc_read_boards":
			response.sc_board_list = self.sc_readboards()
		
		# the rest are commands, so we first need to verify
		# that this manager is allowed to issue them.
		else:
			if not hasattr(message, "mgr_id"):
				self.logger.info("Readout directive message is improperly formatted.  Ignoring...")
				return
				
			if not self.ClientAllowed(message.mgr_id):
				response.subject = "not_allowed"
			else:
				if message.directive == "daq_start":
					status = self.daq_start(message.configuration, identity=self.identities[message.mgr_id])
			
				elif message.directive == "daq_stop":
					status = self.daq_stop()
					
				elif message.directive == "hw_config":
					status = self.sc_sethw(message.hw_config, identity_to_report=response.sender)
		
				elif message.directive == "li_configure":
					status = self.li_configure(message.li_level, message.led_groups)
		
				if status is None:
					response.subject = "invalid_request"
				else:
					response.subject = "request_response"
					response.success = status
					
#		self.logger.debug("response message:\n%s", response)
		self.postoffice.Send(response)

	def daq_status(self):
		""" Returns 1 if there is a DAQ subprocess running; 0 otherwise. """
		self.logger.info("Manager wants to know if DAQ process is running.")
		
		if self.daq_thread and self.daq_thread.is_alive():
			self.logger.info("   ==> It IS.")
			return True
		else:
			self.logger.info("   ==> It ISN'T.")
			return False
	
	def daq_exitstatus(self):
		""" Returns the exit code last given by a DAQ subprocess, or,
		    if no DAQ process has yet exited, returns None. """
		self.logger.info("Manager wants to know last DAQ process exit code.")

		if self.daq_thread is None:
			self.logger.info("   ==> DAQ has not yet been run.")
			return None
		elif self.daq_thread.is_alive():
			self.logger.info("   ==> Process is currently running.  Will need to wait for it to finish.")
			return None
		else:
			self.logger.info("   ==> Exit code: %d (for codes < 0, this indicates the signal that stopped the process).", self.daq_process.returncode)
			return self.daq_thread.returncode

	def daq_start(self, configuration, identity):
		""" Starts the DAQ slave service as a subprocess.  First checks
		    to make sure it's not already running.  Returns True on success,
		    False if there is already a DAQ process running, and if an
		    exception is raised, the exception is returned. """
		    
		logmsg = "Manager wants to start the DAQ process.\n" \
			  + "   Configuration:\n" \
		       + "      Run number: %d\n" \
		       + "      Subrun number: %d\n" \
		       + "      Number of gates: %d\n" \
		       + "      Run mode: %s\n" \
		       + "      Detector: %s\n" \
		       + "      Number of CROCs: %d\n" \
		       + "      LI level: %s\n" \
		       + "      LED group: %s\n" \
		       + "      HW init level: %s\n" \
		       + "      ET file: %s\n" \
		       + "      ET port: %d\n" 
		self.logger.info(logmsg, configuration.run, configuration.subrun, \
		                 configuration.num_gates, configuration.run_mode.description, \
		                 configuration.detector.description, configuration.num_crocs, \
		                 configuration.li_level.description, configuration.led_groups.description, \
		                 configuration.hw_init.description, configuration.et_filename, configuration.et_port)

		if Configuration.params["hw_disabled"]:
			self.logger.info("  ... but the hardware is disabled, so just sending the 'subrun end' message.")
			self.postoffice.Send(PostOffice.Message(subject="daq_status", state="finished", sentinel=False, sender=identity,
			                                        run=configuration.run, subrun=configuration.subrun))
			return True
	
		if self.daq_thread and self.daq_thread.is_alive() is True:
			self.logger.info("   ==> There is already a DAQ process running.")
			return False
			
		# clean up the 'last trigger' file
		try:
			os.remove(Configuration.params["read_lastTriggerFile"])
		except OSError:
			pass
		
		try:
			executable = ( 
			environment["DAQROOT"] + "/bin/minervadaq", 
				          "-et", str(configuration.et_filename),
				          "-p",  str(configuration.et_port),
				          "-g",  str(configuration.num_gates),
				          "-m",  str(configuration.run_mode.hash),
				          "-r",  str(configuration.run),
					     "-s",  str(configuration.subrun),
				          "-d",  str(configuration.detector.hash),
				          "-dc", str(configuration.num_crocs),
				          "-ll", str(configuration.li_level.hash),
				          "-lg", str(configuration.led_groups.hash),
				          "-hw", str(configuration.hw_init.hash),
				          "-cf", self.current_HW_file ) 
			self.logger.info("   minervadaq command:")
			self.logger.info("      '" + ("%s " * len(executable)) % executable + "'...")
			self.daq_thread = DAQThread(owner_process=self, daq_command=executable,
			                            etfile=configuration.et_filename, identity=identity, 
			                            runinfo={"run": configuration.run, "subrun": configuration.subrun})
		except Exception, e:
			self.logger.exception("   ==> DAQ process can't be started! Error message: ")
			return e
		else:
			self.logger.info("    ==> Started successfully.")
			return True
	
	def daq_stop(self):
		""" Stops a DAQ slave service.  First checks to make sure there
		    is in fact such a service running.  Returns True on success,
		    returns the exception if one is raised during the DAQ startup,
		    and False if there is no DAQ process currently running. """
		    
		self.logger.info("Manager wants to stop the DAQ process.")
		
		if self.daq_thread and self.daq_thread.is_alive():
			self.logger.info("   ==> Attempting to stop.")
			try:
				self.daq_thread.daq_process.terminate()
				self.daq_thread.join()		# 'merges' this thread with the other one so that we wait until it's done.
				code = self.daq_thread.returncode
			except Exception, excpt:
				self.logger.exception("   ==> DAQ process couldn't be stopped! Error message:")
				return excpt
		else:		# if there's a process but it's already finished
			self.logger.info("   ==> No DAQ process to stop.")
			return False

		self.logger.info("   ==> Stopped successfully.  (Process %d exited with code %d.)", self.daq_thread.pid, code)
		return True
		
	def li_configure(self, li_level, led_groups):
		""" Uses the LI box interface to configure it.
		
		    Returns True on success, False if for some
		    reason the configuration could not be written,
		    and an exception if one occurred. """
		
		self.logger.debug("Configuring LI using parameters: %s, %s", li_level, led_groups)
		
		if self.li_box is None:
			self.li_box = LIBox.LIBox(disable_LI=not(Configuration.params["hw_LIBoxEnabled"]), wait_response=Configuration.params["hw_LIBoxWaitForResponse"], echocmds=True)
		
		need_LI = True
		if li_level == MetaData.LILevels.ONE_PE:
			self.li_box.pulse_height = Defaults.LI_ONE_PE_VOLTAGE                                        
		elif li_level == MetaData.LILevels.MAX_PE:
			self.li_box.pulse_height = Defaults.LI_MAX_PE_VOLTAGE
		else:
			need_LI = False

		self.logger.info("Resetting the light injection box...")
		try:
			self.li_box.reset()
			self.logger.info( " ... used LI commands:\n%s", "\n".join(self.li_box.get_command_history()) )
		except Exception as e:
			self.logger.exception("An error occurred while trying to reset the LI box:")
			return e
		self.logger.debug(" ... done.")

		# if the LEDs are supposed to be off anyway, just reset the box and be done
		if not need_LI:
			return True

		self.logger.info("Client wants the light injection system configured as follows:\n  LI level: %s\n  LED groups enabled: %s", li_level, led_groups)
		if self.li_box.disable:
		    self.logger.warning("The LI box is currently disabled!  No configuration will actually be done...")

		self.li_box.LED_groups = led_groups.description

		try:
			self.li_box.write_configuration()
		except LIBox.Error as e:
			self.logger.error("The LI box is not responding!  Check the cable and serial port settings.")
			return e
		except Exception as e:
			self.logger.exception("An error occurred while trying to communicate with the LI box:")
			return e
		else:
			self.logger.debug("     ... done.")
			self.logger.info( "     Commands issued to the LI box:\n%s", "\n".join(self.li_box.get_command_history()) )
			return True
		
	def sc_sethw(self, hw_config, identity_to_report=None):
		""" Uses the slow control library to load a hardware configuration
		    file.  Returns True on success, False if there is no such file,
		    and the exception itself if one is raised during loading. """

		# if the hardware is not being used,
		# we need to forge the slow control
		# response before returning...
		if Configuration.params["hw_disabled"]:
			self.postoffice.Send(PostOffice.Message(subject="daq_status", sender=identity_to_report, error=None, state="hw_ready"))
			return True
		    
		hwfile = Configuration.params[hw_config.code] 
		fullpath = "%s/%s" % (Configuration.params["read_SCfileLocation"], hwfile)
	
		self.logger.info("Manager wants to load slow control configuration file: '%s' at location '%s'", hw_config.description, fullpath)
		
		if not os.path.isfile(fullpath):
			self.logger.warning("Specified slow control configuration file does not exist: %s", fullpath)
			return False

		try:			
			self.sc_init()
		except Exception, e:
			self.logger.exception("Hardware error while initializing:")
			return e
		
		SCHWSetupThread(self, self.slow_controls, fullpath, identity_to_report=identity_to_report)
		
		self.current_HW_file = hwfile

		return True
		    
	def sc_readboards(self):
		""" Uses the slow control library to read a few parameters
		    from the front-end boards:
		     (1) the (target - actual) high voltages (in ADC counts).
		     (2) the HV period (in seconds)

		    On success, returns a list of dictionaries with the following
		    keys: "croc", "channel", "board", "hv_deviation", "period"
		    
		    If an exception occurs during the read, that exception is returned."""

		self.logger.info("Manager wants high voltage details of front-end boards.")

		if Configuration.params["hw_disabled"]:
			self.logger.info("  This node's hardware is disabled, so returning an empty status report.")
			return None

		try:
			self.sc_init()

			formatted_feblist = []
			for sc in self.slow_controls:
				croc_feblist, croce_feblist = sc.HVReadAll(0)		# we want ALL boards, that is, those that deviate from target HV by at least 0...
		
				reformat = [
					{
						"crate"       : sc.boardNum,
						"croc"        : (febdetails["FPGA"]["CROCE"] if "CROCE" in febdetails['FPGA'] else febdetails["FPGA"]["CROC"]),
						"chain"       : febdetails["FPGA"]["Channel"],		# NOT a typo.  these are CHAINS -- they go from 0!
						"board"       : febdetails["FPGA"]["FEB"],
						"hv_deviation": febdetails["A-T"],
						"period"      : (febdetails["PeriodMan"] if febdetails["Mode"] == "Manual" else febdetails["PeriodAuto"]),
					} for febdetails in itertools.chain(croc_feblist, croce_feblist)
				]
				formatted_feblist += reformat

		except Exception, e:
			self.logger.exception("Error trying to read the voltages:")
			self.logger.warning("No read performed.")
			return e

		return formatted_feblist
		
	def sc_init(self):
		if len(self.slow_controls) == 0:
			for i in range(Configuration.params["read_SCNumCrates"]):
				sc = SlowControl(linkNum=0, boardNum=i)
				if not sc or not sc.controller:
					continue

				# find the appropriate VME devices: CRIMs, CROCs, DIGitizers....
				sc.FindCRIMs()
				sc.FindCROCs()
				sc.FindCROCEs()
				sc.FindDIGs()
		
				# then load the FEBs into their various CROCs
				sc.FindFEBs(sc.vmeCROCs)
				sc.FindCROCEFEBs(sc.vmeCROCEs)				

				self.slow_controls.append(sc)


#########################
# DAQThread             #
#########################
class DAQThread(threading.Thread):
	""" DAQ processes need to be run in a separate thread
	    so that they can be monitored continuously.  When
	    they terminate, a socket is opened to the master
	    node to emit a "done" signal."""
	def __init__(self, owner_process, daq_command, etfile, identity, runinfo):
		threading.Thread.__init__(self)
		
		self.daq_process = None
		self.logger = logging.getLogger("Dispatcher.Readout")
		self.owner_process = owner_process
		self.daq_command = daq_command
		self.identity = identity
		self.runinfo = runinfo
#		self.sam_file = "%s/%s_SAM.py" % (Configuration.params["read_SAMfileLocation"], etfile)
		
		self.daemon = True
		
		self.start()		# inherited from threading.Thread.  starts run() in a separate thread.
		
	def run(self):
		# note that shlex.split doesn't understand Unicode...
		self.daq_process = subprocess.Popen(self.daq_command,
			close_fds=True,
			env=environment)
		self.pid = self.daq_process.pid		# less typing.

		self.logger.info("   ==>  Process id: " + str(self.pid) + ".")
		
		# how often to check, and how many times to check at that frequency
		# (we do some throttling to keep the disk wear down)
		# { frequency (in seconds): count, frequency: count, ... }
		check_count_max = {0.1: 20, 1: 5, 5: 25, 15: None}
		check_frequencies = sorted(check_count_max.keys())
		check_counts = {0.1: 0, 1: 0, 5: 0}
		check_frequency = 0.1

		self.trigger_file_last_look = 0
		
		# check the 'last trigger' file every so often
		while self.daq_process.poll() is None:
			# don't busy-wait
			time.sleep(0.1)

			if time.time() - self.trigger_file_last_look < check_frequency:
				continue
			
			stats = None
			try:
				stats = os.stat(Configuration.params["read_lastTriggerFile"])
			except OSError:
				pass
			finally:
				# if the file has been modified since the last look, report a new gate.
				# but we want to make sure we throttle the updates a bit so that we don't
				# overwhelm the receiving end, so we make sure we leave at least 0.5s
				# between updates.
				if stats is not None and stats.st_mtime - self.trigger_file_last_look > 0.5:
					# reset the counter to the fastest check frequency
					# since we know some activity has been happening
					check_frequency = check_frequencies[0]
					check_counts[check_frequency] = 0

					self.ReportNewGate(stats.st_mtime)
				elif check_frequencies.index(check_frequency) < len(check_frequencies) - 1:
					if check_counts[check_frequency] <= check_count_max[check_frequency]:
						check_counts[check_frequency] += 1
					# if it hasn't been modified, and we've looked the maximum number of times
					# at this frequency, move to the next one.  
					else:
						check_frequency = check_frequencies[check_frequencies.index(check_frequency) + 1]
						check_counts[check_frequency] = 0
		
		# last 'cleanup' read
		self.ReportNewGate(time.time())
		
		self.returncode = self.daq_process.returncode

		self.logger.info("DAQ subprocess finished.  Check its logfile for more details.")
		
		# "sentinel-indicating" return codes are 2 & 3.
		# anything else indicates an error
		# (minervadaq doesn't use code 0.)
		if self.returncode in (DAQ_EXIT_CODES.SENTINEL, DAQ_EXIT_CODES.NO_SENTINEL):
			sentinel = self.returncode == DAQ_EXIT_CODES.SENTINEL
		
			self.owner_process.postoffice.Send(PostOffice.Message(subject="daq_status", state="finished", sentinel=sentinel, sender=self.identity,
			                                                      run=self.runinfo["run"], subrun=self.runinfo["subrun"]))
		else:
			self.owner_process.postoffice.Send(PostOffice.Message(subject="daq_status", state="exit_error", sender=self.identity,
			                                                      run=self.runinfo["run"], subrun=self.runinfo["subrun"], code=self.returncode ))
		
	def ReportNewGate(self, file_mod_time):
		""" Opens up the last trigger file and parses it to find the gate count,
		    then sends this information to the master node. """

		# gotta beware.  the DAQ is writing to this file repeatedly,
		# so we might wind up with an unsuccessful open.
		try:
			with open(Configuration.params["read_lastTriggerFile"], "r") as trigger_file:
				# we attempt to get the whole file at once -- it's short.
				# this way it (hopefully) won't be changing under our feet.
				trigger_data = trigger_file.read()
				
				# now we look for the token "eventCount=".
				matches = re.search("run=(?P<run>\d+)\nsubrun=(?P<subrun>\d+)\nnumber=(?P<trig_num>\d+)\ntype=(?P<trig_type>\d+)\ntime=(?P<trig_time>\d+)", trigger_data)

				# if we find it, we report it, THEN record when we found it.
				# notice that this way if we get an exception, or don't find
				# the gate count in the file (maybe it's still being written),
				# we'll wind up trying again on the next time around.
				if matches is not None:
					self.owner_process.postoffice.Send( PostOffice.Message( subject="daq_status", \
					                                                        state="running", \
					                                                        gate_count=int(matches.group("trig_num")), \
					                                                        run_num=int(matches.group("run")), \
					                                                        subrun_num=int(matches.group("subrun")),
					                                                        last_trigger_time=int(matches.group("trig_time")) / 10**6, \
					                                                        last_trigger_type=MetaData.TriggerTypes[int(matches.group("trig_type"))], \
					                                                        
					                                                        sender=self.identity ) )
					self.trigger_file_last_look = file_mod_time
				
		# if we can't open the file, oh, well.  we'll be trying again soon anyway.
		except (IOError, OSError):
			pass
				

#########################
# SCHWSetupThread       #
#########################
class SCHWSetupThread(threading.Thread):
	""" Thread to take care of the initialization of the slow control.
	    Sends a message to the master node when it's done. """
	def __init__(self, dispatcher, slowcontrols, filename, identity_to_report=None):
		threading.Thread.__init__(self)
		
		self.dispatcher = dispatcher
		self.slow_controls = slowcontrols
		self.filename = filename
		self.identity = identity_to_report
		
		self.start()
	
	def run(self):
		with open(self.filename) as hwfile:
			try:
				for sc in self.slow_controls:
					sc.HWcfgFileLoad(hwfile, scsNumbers=len(self.slow_controls))
					hwfile.seek(0)  # the file will be used again for the next slow control...
				
			except Exception, e:		# i hate leaving 'catch-all' exception blocks, but the slow control only uses generic Exceptions...
				self.dispatcher.logger.exception("Error trying to load the hardware config file for the crate %d slow control" % sc.boardNum)
				self.dispatcher.logger.warning("Hardware was not configured...")
				self.dispatcher.postoffice.Send(PostOffice.Message(subject="daq_status", sender=self.identity, error=e, state="hw_error"))
			else:
				self.dispatcher.logger.info("HW file %s was loaded.  Informing manager." % self.filename)
				self.dispatcher.postoffice.Send(PostOffice.Message(subject="daq_status", sender=self.identity, error=None, state="hw_ready"))
		



                       
####################################################################
####################################################################
"""
  This module should probably never be imported elsewhere.
  It's designed to run directly as a background process that handles
  incoming requests for the DAQ slave service and slow control.
  
  Otherwise this implementation will bail with an error.
"""
if __name__ == "__main__":
	environment = {}
	try:
		environment["DAQROOT"] = os.environ["DAQROOT"]
		environment["ET_HOME"] = os.environ["ET_HOME"]
		environment["ET_LIBROOT"] = os.environ["ET_LIBROOT"]
		environment["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
	except KeyError:
		sys.stderr.write("Your environment is not properly configured.  You must run the 'setupdaqenv.sh' script before launching the dispatcher.\n")
		sys.exit(1)

	dispatcher = ReadoutDispatcher()
	dispatcher.Bootstrap()
	
	sys.exit(0)
else:
	raise RuntimeError("This module is not designed to be imported!")
