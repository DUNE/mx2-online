
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
import re
import logging
import logging.handlers

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import SocketRequests

#from mnvconfigurator.SlowControl import SC_MainObjects.py as SlowControl

class RunControlDispatcher:
	"""
	This guy is the one who listens for requests and handles them.
	There should NEVER be more than one instance running at a time!
	(They wouldn't both be able to bind to the port...)  Thus the
	start() method checks before allowing dispatching to be started.
	"""
	def __init__(self):
		self.logfile = None
		self.daq_thread = None
		self.port = Defaults.DISPATCHER_PORT
		self.interactive = False
		self.respawn = False
		self.quit = False

		# set up some logging facilites.
		# we set up a rotating file handler here;
		# if the session is interactive, the start() method
		# will set up a console handler as well (which will
		# duplicate the log contents to the screen).
		self.logger = logging.getLogger("rc_dispatcher")
		self.logger.setLevel(logging.DEBUG)
		self.filehandler = logging.handlers.RotatingFileHandler(Defaults.DISPATCHER_LOGFILE, maxBytes=204800, backupCount=5)
		self.filehandler.setLevel(logging.INFO)
		self.formatter = logging.Formatter("[%(asctime)s] %(levelname)s:  %(message)s")
		self.filehandler.setFormatter(self.formatter)
		self.logger.addHandler(self.filehandler)

		self.consolehandler = logging.StreamHandler()
		self.consolehandler.setFormatter(self.formatter)
		self.logger.addHandler(self.consolehandler)

		# make sure that the process shuts down gracefully given the right signals.
		# these lines set up the signal HANDLERS: which functions are called
		# when each signal is received.
		signal.signal(signal.SIGINT, self.shutdown)
		signal.signal(signal.SIGTERM, self.shutdown)

	def __del__(self):
		if self.logfile:
			self.logfile.close()
	
	def setup(self):
		try:
			self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# create an IPv4 TCP socket.
			
			# only bind a local socket if that's all we need.  otherwise, make sure we handle connections from far-off lands
			if self.master_address.lower() in ("localhost", "127.0.0.1"):
				bindaddr = "localhost"
			else:
				bindaddr = socket.gethostname()
			self.server_socket.bind((bindaddr, self.port))

			self.server_socket.listen(3)										# allow it to keep a few backlogged connections (that way if we're trying to talk to it too fast it'll catch up)
		except socket.error, e:
			self.logger.exception("Error trying to bind my listening socket:")
			self.logger.fatal("Can't get a socket.")
			self.shutdown()
		except Exception, e:
			self.logger.exception("An error occurred while trying to bind the socket:")
			self.logger.fatal("Quitting.")		
			self.shutdown()

	def start(self):
		""" Starts the listener.  If you want to run it as a background
		    service, make sure the property 'interactive' is False. 
		    This is normally accomplished by not setting the "-i" flag
		    on the command line (i.e., it's the default behavior).  """
		
		self.logger.info("Starting up.")
		
		other_instance_pid = self.other_instances()
		if other_instance_pid:
			if self.replace:
				self.kill_other_instance(other_instance_pid)
			else:
				self.logger.fatal("Terminating this instance.")
				sys.exit(1)

		
		# make sure this thing is a daemon if it needs to be
		if not self.interactive:
			self.daemonize()
		
		self.logger.info("Creating new PID file.  My PID: " + str(os.getpid()) + "")
			
		pidfile = open(Defaults.DISPATCHER_PIDFILE, 'w')
		pidfile.write(str(os.getpid()) +"\n")
		pidfile.close()
		
		self.setup()
		self.dispatch()
		
	def shutdown(self, sig=None, frame=None):
		""" Ends the dispatch loop. """
		self.quit = True

	def stop(self):
		""" Kills another instance of the dispatcher. """
		# we want to be sure everything gets duplicated to the screen.
		self.logger.info("Checking for other instances to stop...")
		other_pid = self.other_instances()
		
		if other_pid:
			self.logger.info("Stopping instance with pid " + str(other_pid) + "...")
			self.kill_other_instance(other_pid)
		else:
			self.logger.info("No other instances to stop.")
			sys.exit(0)
			
		self.logger.info("Shutdown completed.")
		
	def daemonize(self):
		""" Starts the listener as a background service.
		    Modified mostly from code.activestate.com, recipe 278731. """
		    
		# The standard procedure in UNIX to create a daemon is to use the fork()
		# system call twice in succession.  After the first fork(), the first
		# child process uses the setsid() system call to create a new session and
		# become its leader (this means that the terminal from which the
		# parent process was started is no longer the parent terminal of the child).
		# A session leader can later request a controlling terminal, though, which
		# is the reason for the second fork(): the resulting process is a child process 
		# (not a session leader) in this process group, and non-session leaders can't request
		# a terminal.  Both of the parent processes are exited sequentially, which leaves
		# the remaining process 'orphaned' -- which means that init (the master
		# process of the system) is the only one that will give it SIGTERM when closed.
		#
		# There are a couple of other housekeeping details that this method takes care of:
		#  (1) Closing file descriptors inherited from the parent process.
		#      We don't want open file descriptors that somehow slipped through from the
		#      parent process's controlling terminal.  So we explicitly close any
		#      open file descriptors.
		#  (2) Redirecting the standard input/output/error file descriptors to /dev/null.
		#      After daemonization, the process no longer has a terminal.  That means
		#      that where standard in/out/error point is undefined.  To make sure that
		#      we don't get any weird side effects from programming mistakes,
		#      we explicitly set them to the NULL device (in case I accidentally
		#      put a 'print' statement somewhere, for example).
		#
		# Google for "UNIX daemonize" or some such if you want more details.

		self.logger.info("Trying to daemonize... (check the log for further output)")

		try:
			pid = os.fork()	# returns 0 in the child process
		except OSError, e:
			raise Exception, "%s [%d]" % (e.strerror, e.errno)

		if (pid == 0):			# i.e., if this is the first child process
			os.setsid()

			try:
				pid = os.fork()
			except OSError, e:
				raise Exception, "%s [%d]" % (e.strerror, e.errno)

			if (pid == 0):	# The second child.
				os.chdir("/")		# don't want to be stuck in a mounted file system
				os.umask(0)		# don't inherit default file permissions from parent process
			else:
				os._exit(0)		# Exit parent of the second child (the first child).
		else:
			os._exit(0)	# NOT a typo -- that underscore is supposed to be there.

		# need to turn off the console handler.  it's not doing anything useful now.
		self.logger.removeHandler(self.consolehandler)

		self.logger.info("Daemonization succeeded.")

		# find the maximum file descriptor number
		import resource
		maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
		if (maxfd == resource.RLIM_INFINITY):		# use a default if the OS doesn't want to tell us
			maxfd = 1024

		# we're about to close any open file descriptors.  this will break the pipe
		# to our log file, as well -- so we should just close it intentionally.
		# that way we can ensure its buffer gets flushed properly.
		# the next time the logger is called it will reopen it with a new file descriptor.
		self.filehandler.close()

		# Iterate through and close all open file descriptors.
		for fd in range(maxfd):
			try:
				os.close(fd)
			except OSError:	# fd wasn't open to begin with (ignored)
				pass
		
		# Redirect stdin to /dev/null.
		# [os.open uses the first available file descriptor if none is given,
		# which will be 0 here (stdin) since we just finished closing everything.]
		os.open(os.devnull, os.O_RDWR)	# standard input (0)

		# Duplicate standard input to standard output and standard error.
		os.dup2(0, 1)			# standard output (1)
		os.dup2(0, 2)			# standard error (2)


		return

	def other_instances(self):
		self.logger.info("Checking for PID file...")
		
		if os.path.isfile(Defaults.DISPATCHER_PIDFILE):
			pidfile = open(Defaults.DISPATCHER_PIDFILE)
			pid = int(pidfile.readline())
			pidfile.close()

			self.logger.info("Found PID file with PID " + str(pid) + ".")

			try:
				self.logger.info("Checking if process is alive...")
				os.kill(pid, 0)		# send it the null signal to check if it's there and alive.
			except OSError:			# you get an OSError if the PID doesn't exist.  it's safe to clean up then.
				self.logger.info("Process is dead.  Cleaning up PID file.")
				os.remove(Defaults.DISPATCHER_PIDFILE)
			else:
				self.logger.info("Process is still alive.")
				return pid
		else:
			self.logger.info("No PID file.")
		
		return None
	
	def kill_other_instance(self, pid):
		self.logger.info("Instructing process " + str(pid) + " to end.")

		os.kill(pid, signal.SIGTERM)
		
		self.logger.info("Waiting a maximum of 10 seconds for process " + str(pid) + " to end...")
		secs = 0
		while True:
			time.sleep(1)
			secs += 1
			if secs > 10:
				self.logger.info("Process " + str(pid) + " has not yet terminated.  Kill it manually.")
				sys.exit(1)
				
			try:
				os.kill(pid, 0)
			except OSError:
				break
		self.logger.info("Process " + str(pid) + " ended.")
		
		
	def dispatch(self):
		""" 
		Performs the actual work of handling incoming requests 
		and responding to them appropriately.
		
		Don't call this directly.  Use start() instead (it checks
		to make sure this process is the only one trying to listen
		on the port before entering dispatch mode.)
		"""
		if not self.quit:		# occasionally there's an error before dispatching starts.
			self.logger.info("Master node will be contacted at '" + self.master_address + "'.")
			self.logger.info("Dispatching starting (listening on port " + str(self.port) + ").")

		while not self.quit:
			# if we interrupt the socket system call by receiving a signal,
			# the socket throws an exception as a warning.  we should just start over then,
			# which will cause a quit (the signal handler for the only signals
			# we're handling--SIGTERM and SIGINT--sets self.quit to True).
			try:
				client_socket, client_address = self.server_socket.accept()
			except socket.error, (errnum, msg):
				if errnum == errno.EINTR:		# the code for an interrupted system call
					continue
				else:						# if it's not an interrupted system call, we need the error!
					self.logger.exception("Error " + str(errnum) + ": " + msg)
			except Exception, e:
				self.logger.exception("Error trying to get socket:")

			self.logger.info("Accepted connection from " + str(client_address) + ".")
			
			request = ""
			datalen = -1
			while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire request
				data = client_socket.recv(1024)
				datalen = len(data)
				request += data
			
			self.logger.info("Client request: '" + request + "'")
			
			response = self.respond(request)
			if response is not None:		# don't waste our time sending a response to an invalid request.
				self.logger.info("Attempting to send response:\n" + response)
				try:
					client_socket.sendall(response)		# this will throw an exception if all the data can't be sent.
				except:
					self.logger.warning("Transmission error.")	# what to do if it can't all be sent?  hmm...
				else:
					self.logger.info("Transmission completed.")
			else:
				self.logger.info("Request is invalid.")

			try:
				client_socket.shutdown(socket.SHUT_RDWR)
				self.logger.info("Socket closed.")
			except socket.error:
				self.logger.exception("Socket error on socket shutdown:")
				self.logger.error("   ==> Data transmission was interrupted!")
			finally:
				client_socket.close()
	
		self.logger.info("Instructed to close.  Exiting dispatch mode.")
		self.cleanup()

			
	def respond(self, request):
		"""
		Decides what to do with a particular request.
		Returns None for invalid requests.
		"""
		is_valid_request = False
		for valid_request in SocketRequests.ValidRequests:
			matches = re.match(valid_request, request)
			if matches is not None:
				is_valid_request = True
				break
		
		if not is_valid_request:
			self.logger.info("Request does not match pattern.")
			return None

		request = matches.group("request").lower()
		handlers = { "alive" : self.ping,
		             "daq_running" : self.daq_status,
		             "daq_last_exit" : self.daq_exitstatus,
		             "daq_start" : self.daq_start,
		             "daq_stop" : self.daq_stop,
		             "sc_sethwconfig" : self.sc_sethw,
		             "sc_voltages" : self.sc_readvoltages }
		
		if request in handlers:
			return handlers[request](matches)
		else:
			return None
		

	def ping(self, matches):
		""" Returns something so that a client knows the server is alive. """
		self.logger.info("Responding to ping.")
		return "1"
	
	def daq_status(self, matches):
		""" Returns 1 if there is a DAQ subprocess running; 0 otherwise. """
		self.logger.info("Client wants to know if DAQ process is running.")
		
		if self.daq_thread and self.daq_thread.is_alive():
			self.logger.info("   ==> It IS.")
			return "1"
		else:
			self.logger.info("   ==> It ISN'T.")
			return "0"
	
	def daq_exitstatus(self, matches):
		""" Returns the exit code last given by a DAQ subprocess, or,
		    if no DAQ process has yet exited, returns 'NONE'. """
		self.logger.info("Client wants to know last DAQ process exit code.")

		if self.daq_thread is None:
			self.logger.info("   ==> DAQ has not yet been run.")
			return "NONE"
		elif self.daq_thread.is_alive():
			self.logger.info("   ==> Process is currently running.  Will need to wait for it to finish.")
			return "NONE"
		else:
			self.logger.info("   ==> Exit code: " + str(self.daq_process.returncode) + " (for codes < 0, this indicates the signal that stopped the process).")
			return str(self.daq_thread.returncode)

	def daq_start(self, matches):
		""" Starts the DAQ slave service as a subprocess.  First checks
		    to make sure it's not already running.  Returns 0 on success,
		    1 on some DAQ or other error, and 2 if there is already
		    a DAQ process running. """
		    
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

		if self.daq_thread and self.daq_thread.is_alive() is None:
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
			self.logger.info("   minervadaq command:")
			self.logger.info("      '" + ("%s " * len(executable)) % executable + "'...")
			self.daq_thread = DAQThread(self, executable, matches.group("identity"), self.master_address)
		except Exception, excpt:
			self.logger.error("   ==> DAQ process can't be started!")
			self.logger.error("   ==> Error message: '" + str(excpt) + "'")
			return "1"
		else:
			self.logger.info("    ==> Started successfully.")
			return "0"
	
	def daq_stop(self, matches):
		""" Stops a DAQ slave service.  First checks to make sure there
		    is in fact such a service running.  Returns 0 on success,
		    1 on some DAQ or other error, and 2 if there is no DAQ
		    process currently running. """
		    
		self.logger.info("Client wants to stop the DAQ process.")
		
		if self.daq_thread and self.daq_thread.is_alive():
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
			self.logger.info("   ==> No DAQ process to stop.")
			return "2"
	
		self.logger.info("   ==> Stopped successfully.  (Process " + str(self.daq_thread.pid) + " exited with code " + str(code) + ".)")
		return "0"
		
	def sc_sethw(self, matches):
		""" Uses the slow control library to load a hardware configuration
		    file.  Returns 0 on success, 1 on hardware error, and 2 if 
		    there is no such file. """
		self.logger.info("Client wants to load slow control configuration file: '" + matches.group("filename") + "'.")
		
		self.logger.info("   ==> Loaded successfully.")
		return "0"
		    
	def sc_readvoltages(self, matches):
		""" Uses the slow control library to read the FEB voltages.
		    On success, returns a string of lines consisting of
		    1 voltage per line, in the following format:
		    FPGA-CROC-CHAIN-BOARD: [voltage]
		    On failure, returns the string "NOREAD". """

		self.logger.info("Client wants to know the FEB voltages.")

		self.logger.info("No read happened.")
		return "NOREAD"
		
	def cleanup(self):
		self.server_socket.close()

		if os.path.isfile(Defaults.DISPATCHER_PIDFILE):
			self.logger.info("Removing PID file.")
			os.remove(Defaults.DISPATCHER_PIDFILE)

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
		
		self.owner_process.logger.info("Contacting master to indicate I am done.")
		# open a client socket to the master node.  need to inform it we're done!
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(2)
			s.connect( (self.master_address, Defaults.MASTER_PORT) )
			s.send(self.identity)		# informs the server WHICH of the readout nodes I am (and that I'm finished).
			s.shutdown(socket.SHUT_WR)
			self.owner_process.logger.info("'Done' signal sent successfully.")
		except:
			self.owner_process.logger.exception("Socket error:")
			self.owner_process.logger.error("  ==> 'Done' signal did not make it to master.")
		finally:
			s.close()

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
		sys.stderr("Your environment is not properly configured.  You must run the 'setup_daqbuild.sh' script before launching the dispatcher.")
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
