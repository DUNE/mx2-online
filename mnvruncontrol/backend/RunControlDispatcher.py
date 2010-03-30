"""
  RunControlDispatcher.py:
  Listener service that runs on a DAQ slave ("soldier" or "worker" node
  in Gabe's terminology) to manage the DAQ process and slow control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import socket
import signal
import subprocess
import threading
import errno
import time
import sys
import os
import os.path
import re
import logging
import logging.handlers

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import SocketRequests

from mnvruncontrol.backend.Dispatcher import Dispatcher

#from mnvconfigurator.SlowControl.SC_MainMethods import SC as SlowControl


class RunControlDispatcher(Dispatcher):
	"""
	This guy is the one who listens for requests and handles them.
	There should NEVER be more than one instance running at a time!
	(They wouldn't both be able to bind to the port...)  Thus the
	start() method checks before allowing dispatching to be started.
	"""
	def __init__(self):
		Dispatcher.__init__(self)
	
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
		self.filehandler = logging.handlers.RotatingFileHandler(Defaults.READOUT_DISPATCHER_LOGFILE, maxBytes=204800, backupCount=5)
		self.filehandler.setLevel(logging.INFO)
		self.filehandler.setFormatter(self.formatter)		# self.formatter is set up in the Dispatcher superclass
		self.logger.addHandler(self.filehandler)

		# we need to specify what requests we know how to handle.
		self.valid_requests += SocketRequests.ReadoutRequests
		self.handlers.update( { "alive" : self.ping,
		                        "daq_running" : self.daq_status,
		                        "daq_last_exit" : self.daq_exitstatus,
		                        "daq_start" : self.daq_start,
		                        "daq_stop" : self.daq_stop,
		                        "sc_sethwconfig" : self.sc_sethw,
		                        "sc_readboards" : self.sc_readboards } )
		
		self.pidfilename = Defaults.READOUT_DISPATCHER_PIDFILE

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
			self.logger.info("      Run mode: " + MetaData.RunningModes[int(matches.group("runmode"))] )
			self.logger.info("      Detector: " + MetaData.DetectorTypes[int(matches.group("detector"))] )
			self.logger.info("      Number of FEBs: " + matches.group("nfebs") )
			self.logger.info("      LI level: " + MetaData.LILevels[int(matches.group("lilevel"))] )
			self.logger.info("      LED group: " + MetaData.LEDGroups[int(matches.group("ledgroup"))] )
			self.logger.info("      HW init level: " + MetaData.HardwareInitLevels[int(matches.group("hwinitlevel"))] )
			self.logger.info("      ET file: " + matches.group("etfile") )
			self.logger.info("      ET port: " + matches.group("etport") )
			self.logger.info("      my identity: " + matches.group("identity") + " node")

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
				          "-ll", matches.group("lilevel"),
				          "-lg", matches.group("ledgroup"),
				          "-hw", matches.group("hwinitlevel") ) 
			if show_details:
				self.logger.info("   minervadaq command:")
				self.logger.info("      '" + ("%s " * len(executable)) % executable + "'...")
			self.daq_thread = DAQThread(self, executable, matches.group("identity"), self.lock_address)
		except Exception, excpt:
			self.logger.error("   ==> DAQ process can't be started!")
			self.logger.error("   ==> Error message: '" + str(excpt) + "'")
			return "1"
		else:
			if show_details:
				self.logger.info("    ==> Started successfully.")
			return "0"
	
	def daq_stop(self, matches, show_details, **kwargs):
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
		    file.  Returns 0 on success, 1 on hardware error, and 2 if 
		    there is no such file. """
		if show_details:
			self.logger.info("Client wants to load slow control configuration file: '" + matches.group("filename") + "'.")
		
		fullpath = Defaults.SLOWCONTROL_CONFIG_LOCATION_DEFAULT + "/" + matches.group("filename")
		
		if not os.path.isfile(fullpath):
			self.logger.warning("Specified slow control configuration file does not exist: " + fullpath)
			return "2"

		try:
			self.sc_init()
			self.slowcontrol.HWcfgFileLoad(fullpath)
		except:		# i hate leaving 'catch-all' exception blocks, but the slow control only uses generic Exceptions...
			self.logger.exception("Error trying to load the hardware config file:")
			self.logger.warning("Hardware was not configured...")
			return "1"

		if show_details:
			self.logger.info("   ==> Loaded successfully.")

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
	def __init__(self, owner_process, daq_command, my_identity, master_address):
		threading.Thread.__init__(self)
		
		self.daq_process = None
		self.owner_process = owner_process
		self.identity = my_identity	# am I the worker, the soldier, a local node, etc.?
		self.master_address = master_address
		self.daq_command = daq_command
		
		self.start()		# inherited from threading.Thread.  starts run() in a separate thread.
		
	def run(self):
		self.daq_process = subprocess.Popen(self.daq_command, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		self.pid = self.daq_process.pid		# less typing.

		self.owner_process.logger.info("   ==>  Process id: " + str(self.pid) + ".")

		stdout, stderr = self.daq_process.communicate()
		
		filename = Defaults.LOGFILE_LOCATION_DEFAULT + "/minervadaq.log"
		self.owner_process.logger.info("DAQ subprocess finished.  Its output will be written to '" + filename + "'.")
		# dump the output of minervadaq to a file so that crashes can be investigated.
		# we only keep one copy because it will be rare that anyone is interested.
		try:
			with open(filename, "w") as logfile:
				logfile.write(stdout)
		except OSError:
			self.owner_process.logger.exception("minervadaq log file error:")
			self.owner_process.logger.error("   ==> log file information will be discarded.")
		
		# open a client socket to the master node.  need to inform it we're done!
		tries = 0
		success = False
		while tries < Defaults.MAX_CONNECTION_ATTEMPTS and not success:
			self.owner_process.logger.info("Attempting to contact master to indicate I am done.")
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.settimeout(Defaults.SOCKET_TIMEOUT)
				s.connect( (self.master_address, Defaults.MASTER_PORT) )
				s.send(self.identity)		# informs the server WHICH of the readout nodes I am (and that I'm finished).
				s.shutdown(socket.SHUT_WR)
				self.owner_process.logger.info("'Done' signal sent successfully.")
				success = True
			except:
				self.owner_process.logger.exception("Socket error:")
				self.owner_process.logger.info("  ==> 'Done' communication interrupted.")
				tries += 1
				if tries < Defaults.MAX_CONNECTION_ATTEMPTS:
					self.owner_process.logger.info("  ==> Will try again in 1s.")
				time.sleep(Defaults.CONNECTION_ATTEMPT_INTERVAL)
			finally:
				s.close()
				
		if tries == Defaults.MAX_CONNECTION_ATTEMPTS:
			self.owner_process.logger.error("  ==> Could not communicate 'done' to master.")

		self.returncode = self.daq_process.returncode
		
                        
####################################################################
####################################################################
"""
  This module should probably never be imported elsewhere.
  It's designed to run directly as a background process that handles
  incoming requests for the DAQ slave service and slow control.
  
  If it IS running as a stand-alone, it will need to daemonize
  and begin listening on the specified port.
  
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
		sys.stderr.write("Your environment is not properly configured.  You must run the 'setup_daqbuild.sh' script before launching the dispatcher.\n")
		sys.exit(1)

	import optparse
	
	parser = optparse.OptionParser(usage="usage: %prog [options] command\n  where 'command' is 'start' or 'stop'")
	parser.add_option("-r", "--replace", dest="replace", action="store_true", help="Replace a currently-running instance of the service with a new one. Default: %default.", default=False)
	parser.add_option("-i", "--interactive", dest="interactive", action="store_true", help="Run in an interactive session (don't daemonize).  Default: %default.", default=False)
	parser.add_option("-m", "--master-address", dest="masterAddress", help="The internet address of the master node.  Default: %default.", default=Defaults.MASTER)
	
	(options, commands) = parser.parse_args()
	
	if len(commands) != 1 or not(commands[0].lower() in ("start", "stop")):
		parser.print_help()
		sys.exit(0)

	command = commands[0].lower()
	
	dispatcher = RunControlDispatcher()
	
	
	if command == "start":
		dispatcher.interactive = options.interactive
		dispatcher.replace = options.replace
		dispatcher.master_address = options.masterAddress
		
		if dispatcher.interactive:
			print "Running in interactive mode."
			print "All log information will be echoed to the screen."
			print "Enter 'Ctrl-C' to exit.\n\n"
		else:
			print "Dispatcher starting in daemon mode."
			print "Run this program with the keyword 'stop' to stop it."
			print "Also see the log file at '" + Defaults.DISPATCHER_LOGFILE + "'.\n"
		dispatcher.start()
	elif command == "stop":
		dispatcher.interactive = True
		dispatcher.replace = False
		dispatcher.stop()
	
	sys.exit(0)
else:
	raise RuntimeError("This module is not designed to be imported!")
