"""
  RunControlDispatcher.py:
   Listener service that runs on a DAQ slave ("soldier" or "worker" node
   in Gabe's terminology) to manage the DAQ process and slow control.
   It inherits most of its functionality from Dispatcher.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import subprocess
import threading
import time
import sys
import os
import os.path
import logging
import logging.handlers

from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend import Dispatcher

from mnvconfigurator.SlowControl.SC_MainMethods import SC as SlowControl


class RunControlDispatcher(Dispatcher.Dispatcher):
	"""
	This guy is the one who listens for requests and handles them.
	There should NEVER be more than one instance running at a time!
	(They wouldn't both be able to bind to the port...)  Thus the
	start() method checks before allowing dispatching to be started.
	"""
	def __init__(self):
		Dispatcher.Dispatcher.__init__(self)
	
		# the master slow control object.  it handles
		# the interface with the hardware.
		# we can't initialize it here because it seems to
		# use file descriptors to interact with the hardware,
		# which means that during daemonization the
		# hardware link would get broken.
		# it will be initialized when used.
		self.slowcontrol = None

		# Dispatcher() maintains a central logger.
		# We want a file output, so we'll set that up here.
		self.filehandler = logging.handlers.RotatingFileHandler(Configuration.params["Readout nodes"]["readout_logfileName"], maxBytes=204800, backupCount=5)
		self.filehandler.setLevel(logging.INFO)
		self.filehandler.setFormatter(self.formatter)		# self.formatter is set up in the Dispatcher superclass
		self.logger.addHandler(self.filehandler)

		# we need to specify what requests we know how to handle.
		self.valid_requests += SocketRequests.ReadoutRequests
		self.handlers.update( { "alive"          : self.ping,
		                        "daq_running"    : self.daq_status,
		                        "daq_last_exit"  : self.daq_exitstatus,
		                        "daq_start"      : self.daq_start,
		                        "daq_stop"       : self.daq_stop,
		                        "sc_sethwconfig" : self.sc_sethw,
		                        "sc_readboards"  : self.sc_readboards } )
		                        
		self.cleanup_methods += [self.daq_stop]
		
		self.pidfilename = Configuration.params["Readout nodes"]["readout_PIDfileLocation"]
		self.current_HW_file = "NOFILE"

		self.daq_thread = None

	def daq_status(self, matches, show_details, **kwargs):
		""" Returns 1 if there is a DAQ subprocess running; 0 otherwise. """
		if show_details:
			self.logger.info("Client wants to know if DAQ process is running.")
		
		if self.daq_thread and self.daq_thread.is_alive():
			if show_details:
				self.logger.info("   ==> It IS.")
			return "1"
		else:
			if show_details:
				self.logger.info("   ==> It ISN'T.")
			return "0"
	
	def daq_exitstatus(self, matches, show_details, **kwargs):
		""" Returns the exit code last given by a DAQ subprocess, or,
		    if no DAQ process has yet exited, returns 'NONE'. """
		self.logger.info("Client wants to know last DAQ process exit code.")

		if self.daq_thread is None:
			if show_details:
				self.logger.info("   ==> DAQ has not yet been run.")
			return "NONE"
		elif self.daq_thread.is_alive():
			if show_details:
				self.logger.info("   ==> Process is currently running.  Will need to wait for it to finish.")
			return "NONE"
		else:
			if show_details:
				self.logger.info("   ==> Exit code: " + str(self.daq_process.returncode) + " (for codes < 0, this indicates the signal that stopped the process).")
			return str(self.daq_thread.returncode)

	def daq_start(self, matches, show_details, **kwargs):
		""" Starts the DAQ slave service as a subprocess.  First checks
		    to make sure it's not already running.  Returns 0 on success,
		    1 on some DAQ or other error, and 2 if there is already
		    a DAQ process running. """
		    
		if show_details:
			self.logger.info("Client wants to start the DAQ process.")
			self.logger.info("   Configuration:")
			self.logger.info("      Run number: " + matches.group("run"))
			self.logger.info("      Subrun number: " + matches.group("subrun"))
			self.logger.info("      Number of gates: " + matches.group("gates"))
			self.logger.info("      Run mode: " + MetaData.RunningModes.description(int(matches.group("runmode"))) )
			self.logger.info("      Detector: " + MetaData.DetectorTypes.description(int(matches.group("detector"))) )
			self.logger.info("      Number of FEBs: " + matches.group("nfebs") )
			self.logger.info("      LI level: " + MetaData.LILevels.description(int(matches.group("lilevel"))) )
			self.logger.info("      LED group: " + MetaData.LEDGroups.description(int(matches.group("ledgroup"))) )
			self.logger.info("      HW init level: " + MetaData.HardwareInitLevels.description(int(matches.group("hwinitlevel"))) )
			self.logger.info("      ET file: " + matches.group("etfile") )
			self.logger.info("      ET port: " + matches.group("etport") )

		if self.daq_thread and self.daq_thread.is_alive() is True:
			if show_details:
				self.logger.info("   ==> There is already a DAQ process running.")
			return "2"
		
		try:
			executable = ( environment["DAQROOT"] + "/bin/minervadaq", 
				          "-et", matches.group("etfile"),
				          "-p",  matches.group("etport"),
				          "-g",  matches.group("gates"),
				          "-m",  matches.group("runmode"),
				          "-r",  matches.group("run"),
					     "-s",  matches.group("subrun"),
				          "-d",  matches.group("detector"),
				          "-dc", matches.group("nfebs"),
				          "-ll", matches.group("lilevel"),
				          "-lg", matches.group("ledgroup"),
				          "-hw", matches.group("hwinitlevel"),
				          "-cf", self.current_HW_file ) 
			if show_details:
				self.logger.info("   minervadaq command:")
				self.logger.info("      '" + ("%s " * len(executable)) % executable + "'...")
			self.daq_thread = DAQThread(self, self.logger, executable, self.lock_address)
		except Exception, excpt:
			self.logger.error("   ==> DAQ process can't be started!")
			self.logger.error("   ==> Error message: '" + str(excpt) + "'")
			return "1"
		else:
			if show_details:
				self.logger.info("    ==> Started successfully.")
			return "0"
	
	def daq_stop(self, matches=None, show_details=True, **kwargs):
		""" Stops a DAQ slave service.  First checks to make sure there
		    is in fact such a service running.  Returns 0 on success,
		    1 on some DAQ or other error, and 2 if there is no DAQ
		    process currently running. """
		    
		if show_details:
			self.logger.info("Client wants to stop the DAQ process.")
		
		if self.daq_thread and self.daq_thread.is_alive():
			if show_details:
				self.logger.info("   ==> Attempting to stop.")
			try:
				self.daq_thread.daq_process.terminate()
				self.daq_thread.join()		# 'merges' this thread with the other one so that we wait until it's done.
				code = self.daq_thread.returncode
			except Exception, excpt:
				self.logger.error("   ==> DAQ process couldn't be stopped!")
				self.logger.exception("   ==> Error message:")
				return "1"
		else:		# if there's a process but it's already finished
			if show_details:
				self.logger.info("   ==> No DAQ process to stop.")
			return "2"

		if show_details:
			self.logger.info("   ==> Stopped successfully.  (Process " + str(self.daq_thread.pid) + " exited with code " + str(code) + ".)")
		return "0"
		
	def sc_sethw(self, matches, show_details, **kwargs):
		""" Uses the slow control library to load a hardware configuration
		    file.  Returns 0 on success, 1 on error, and 2 if 
		    there is no such file. """
		hwconfig_hash = int(matches.group("hwconfig"))
		hwfile = Configuration.params["Readout nodes"][MetaData.HardwareConfigurations.code(hwconfig_hash)] 
		if show_details:
			self.logger.info("Client wants to load slow control configuration file: '%s'." % MetaData.HardwareConfigurations.description(hwconfig_hash))
		
		fullpath = "%s/%s" % (Configuration.params["Readout nodes"]["SCfileLocation"], hwfile)
		
		if not os.path.isfile(fullpath):
			self.logger.warning("Specified slow control configuration file does not exist: " + fullpath)
			return "2"
			
		self.sc_init()
		
		SCHWSetupThread(self, self.slowcontrol, fullpath)
		
		self.current_HW_file = hwfile

		return "0"
		    
	def sc_readboards(self, matches, show_details, **kwargs):
		""" Uses the slow control library to read a few parameters
		    from the front-end boards:
		     (1) the target - actual high voltages (in ADC counts).
		     (2) the HV period (in seconds)
		    On success, returns a string of lines consisting of
		    1 voltage per line, in the following format:
		    CROC-CHANNEL-BOARD: [voltage_deviation_in_ADC_counts]
		    On failure, returns the string "NOREAD". 
                    If the slow control modules return an empty list
                    (no FEBs), this method returns "NOBOARDS". """

		if show_details:
			self.logger.info("Client wants high voltage details of front-end boards.")
		try:
			self.sc_init()
			feblist = self.slowcontrol.HVReadAll(0)		# we want ALL boards, that is, those that deviate from target HV by at least 0...
		except:
			self.logger.exception("Error trying to read the voltages:")
			self.logger.warning("No read performed.")
			return "NOREAD"

		if len(feblist) == 0:
			return "NOBOARDS"
		
		formatted_feblist = [ "%s-%s-%s: %s %s" % (febdetails['FPGA']["CROC"],
		                                           febdetails["FPGA"]["Channel"],
		                                           febdetails["FPGA"]["FEB"],
		                                           febdetails["A-T"],
		                                           (febdetails["PeriodMan"] if febdetails["Mode"] == "Manual" else febdetails["PeriodAuto"]) )
		                      for febdetails in feblist ]
		return "\n".join(formatted_feblist)
		
	def sc_init(self):
		if self.slowcontrol is None:
			self.slowcontrol = SlowControl()

		# find the appropriate VME devices: CRIMs, CROCs, DIGitizers....
		self.slowcontrol.FindCRIMs()
		self.slowcontrol.FindCROCs()
		self.slowcontrol.FindDIGs()
		
		# then load the FEBs into their various CROCs
		self.slowcontrol.FindFEBs(self.slowcontrol.vmeCROCs)

#########################
# DAQThread             #
#########################
class DAQThread(threading.Thread):
	""" DAQ processes need to be run in a separate thread
	    so that they can be monitored continuously.  When
	    they terminate, a socket is opened to the master
	    node to emit a "done" signal."""
	def __init__(self, owner_process, logger, daq_command, master_address):
		threading.Thread.__init__(self)
		
		self.daq_process = None
		self.logger = logger		# since loggers are thread-safe, we'll just use it directly.
		self.owner_process = owner_process
		self.master_address = master_address
		self.daq_command = daq_command
		
		self.daemon = True
		
		self.start()		# inherited from threading.Thread.  starts run() in a separate thread.
		
	def run(self):
		try:
			filename = "%s/minervadaq.log" % Configuration.params["Readout nodes"]["readout_logfileLocation"]
			with open(filename, "w") as logfile:
				self.daq_process = subprocess.Popen(self.daq_command, env=environment, stdout=logfile.fileno(), stderr=subprocess.STDOUT)
				self.pid = self.daq_process.pid		# less typing.

				self.owner_process.logger.info("   ==>  Process id: " + str(self.pid) + ".")

				self.returncode = self.daq_process.wait()
		
				self.owner_process.logger.info("DAQ subprocess finished.  Its output will be written to '" + filename + "'.")
				# dump the output of minervadaq to a file so that crashes can be investigated.
				# we only keep one copy because it will be rare that anyone is interested.
		except (OSError, IOError) as e:
			self.logger.exception("minervadaq log file error: %s" % e.message)
			self.logger.warning("   ==> log file information will be discarded.")
		
		self.owner_process.queue.put(Dispatcher.Message(message="daq_finished", recipient=Dispatcher.MASTER))
				

#########################
# SCHWSetupThread       #
#########################
class SCHWSetupThread(threading.Thread):
	""" Thread to take care of the initialization of the slow control.
	    Sends a message to the master node when it's done. """
	def __init__(self, dispatcher, slowcontrol, filename):
		threading.Thread.__init__(self)
		
		self.dispatcher = dispatcher
		self.slowcontrol = slowcontrol
		self.filename = filename
		
		self.start()
	
	def run(self):
		try:
			self.slowcontrol.HWcfgFileLoad(self.filename)
		except:		# i hate leaving 'catch-all' exception blocks, but the slow control only uses generic Exceptions...
			self.dispatcher.logger.exception("Error trying to load the hardware config file")
			self.dispatcher.logger.warning("Hardware was not configured...")
			self.dispatcher.queue.put(Dispatcher.Message("hw_error", Dispatcher.MASTER))
		else:
			self.dispatcher.logger.info("HW file %s was loaded." % self.filename)
			self.dispatcher.queue.put(Dispatcher.Message("hw_ready", Dispatcher.MASTER))
		



                       
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

	dispatcher = RunControlDispatcher()
	dispatcher.bootstrap()
	
	sys.exit(0)
else:
	raise RuntimeError("This module is not designed to be imported!")
