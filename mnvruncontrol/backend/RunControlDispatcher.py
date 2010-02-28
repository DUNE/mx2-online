#!/usr/bin/python

"""
  RunControlDispatcher.py:
  Listener service that runs on a DAQ slave ("soldier" or "worker" node
  in Gabe's terminology) to manage the DAQ process and slow control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb. 2010
                    
   Address all complaints to the management.
"""

import socket
import signal
import subprocess
import time
import sys
import os
import re

from mnvruncontrol.configuration import Defaults

#from mnvconfigurator.SlowControl import SC_MainObjects.py as SlowControl

class RunControlDispatcher:
	"""
	This guy is the one who listens for requests and handles them.
	There should NEVER be more than one instance running at a time!
	(They wouldn't both be able to bind to the port...)  Thus the
	constructor checks before allowing itself to be started.
	"""
	def __init__(self):
		self.logfile = None
		self.daq_process = None
		self.port = Defaults.DISPATCHER_PORT
		self.interactive = False
		self.respawn = False

		# make sure that the process shuts down gracefully given the right signals.
		# these lines set up the signal HANDLERS: which functions are called
		# when each signal is received.
		signal.signal(signal.SIGINT, self.shutdown)
		signal.signal(signal.SIGTERM, self.shutdown)

	def __del__(self):
		if self.logfile:
			self.logfile.close()
	
	def setup(self):
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# create an IPv4 TCP socket.
		self.server_socket.bind(("", self.port))				# bind it to the port specified in the config., on any interface that will let it, on the local machine
		self.server_socket.listen(1)										# only allow it to keep one backlogged connection

	def start(self):
		""" Starts the listener.  If you want to run it as a background
		    service, make sure the property 'interactive' is False. """
		
		self.logwrite("Starting up.\n")
		
		other_instance_pid = self.other_instances()
		if other_instance_pid:
			if self.replace:
				self.kill_other_instance(other_instance_pid)
			else:
				self.logwrite("Terminating this instance.\n")
				sys.exit(1)

		# make sure this thing is a daemon if it needs to be
		if not self.interactive:
			self.daemonize()
		
		self.logwrite("Creating new PID file.  My PID: " + str(os.getpid()) + "\n")
			
		pidfile = open(Defaults.DISPATCHER_PIDFILE, 'w')
		pidfile.write(str(os.getpid()) +"\n")
		pidfile.close()
		
		self.setup()
		self.dispatch()
		
	def shutdown(self, signal=None, frame=None):
		""" Ends the dispatch loop. """
		self.quit = True

	def stop(self):
		""" Kills another instance of the dispatcher. """
		self.logwrite("Checking for other instances to stop...\n")
		other_pid = self.other_instances()
		
		if other_pid:
			self.kill_other_instance(other_pid)
		else:
			self.logwrite("No other instances to stop.\n")
			sys.exit(0)
		
	def daemonize(self):
		""" Starts the listener as a background service.
		    Borrowed mostly from code.activestate.com, recipe 278731. """
		    
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
		# Google for "UNIX daemonize" or some such if you want more details.

		self.logwrite("Trying to daemonize...\n")

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

		self.logwrite("Daemonization succeeded.\n")

		# find the maximum file descriptor number
		import resource
		maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
		if (maxfd == resource.RLIM_INFINITY):		# use a default if the OS doesn't want to tell us
			maxfd = 1024

		# Iterate through and close all open file descriptors.
		# Note that this will probably close our log file,
		# but that's ok because logwrite() checks to make sure
		# it's open before writing (and if it isn't, it opens it).
		for fd in range(0, maxfd):
			if self.logfile and fd == self.logfile.fileno():	# don't close our log file!
				continue
			try:
				os.close(fd)
			except OSError:	# ERROR, fd wasn't open to begin with (ignored)
				pass
				
		# Want to redirect the standard in/outputs to /dev/null because there's no controlling terminal.
		# Redirect the lowest file descriptor (which will be STDIN, 0, because everything else
		# was closed above)
		os.open(os.devnull, os.O_RDWR)	# standard input (0)

		# Duplicate standard input to standard output and standard error.
		os.dup2(0, 1)			# standard output (1)
		os.dup2(0, 2)			# standard error (2)

		return

	def other_instances(self):
		self.logwrite("Checking for PID file...\n")
		
		if os.path.isfile(Defaults.DISPATCHER_PIDFILE):
			pidfile = open(Defaults.DISPATCHER_PIDFILE)
			pid = int(pidfile.readline())
			pidfile.close()

			self.logwrite("Found PID file with PID " + str(pid) + ".\n")

			try:
				self.logwrite("Checking if process is alive...\n")
				os.kill(pid, 0)		# send it the null signal to check if it's there and alive.
			except OSError:			# you get an OSError if the PID doesn't exist.  it's safe to clean up then.
				self.logwrite("Process is dead.  Cleaning up PID file.\n")
				os.remove(Defaults.DISPATCHER_PIDFILE)
			else:
				self.logwrite("Process is still alive.\n")
				return pid
		else:
			self.logwrite("No PID file.\n")
		
		return None
	
	def kill_other_instance(self, pid):
		self.logwrite("Instructing process " + str(pid) + " to end.\n")

		os.kill(pid, signal.SIGTERM)
		
		self.logwrite("Waiting a maximum of 10 seconds for other process to end...\n")
		secs = 0
		while True:
			time.sleep(1)
			secs += 1
			if secs > 10:
				self.logwrite("Other instance (PID " + str(pid) + ") has not yet terminated.  Kill it manually.\n")
				sys.exit(1)
				
			try:
				os.kill(pid, 0)
			except OSError:
				break
		self.logwrite("Process " + str(pid) + " ended.\n")
		
		
	def logwrite(self, data):
		""" Writes to the logfile.  Includes a flush so that data is written
		    to the file even if the process doesn't shut down cleanly. 
		    If in interactive mode, also echoes to the screen. """
		if not self.logfile:
			self.logfile = open(Defaults.DISPATCHER_LOGFILE, "w")
		
		timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.gmtime())
		self.logfile.write(timestamp + data)
		self.logfile.flush()
		
		if self.interactive:
			print timestamp + data
			
	def dispatch(self):
		""" 
		Performs the actual work of handling incoming requests 
		and responding to them appropriately.
		
		Don't call this directly.  Use start() (for interactive
		sessions) or daemonize()/restart() (for service operation)
		instead (they check to make sure this process is the only
		one trying to listen on the port before entering dispatch mode.)
		"""
		self.quit = False

		self.logwrite("Dispatching starting (listening on port " + str(self.port) + ").\n")

		while not self.quit:
			# if we interrupt the socket system call, by receiving a signal,
			# it throws an exception as a warning.  we should just start over then,
			# which will cause a quit (the signal handler for the only signals
			# we're handling right now--SIGTERM and SIGINT--sets self.quit to True).
			try:
				client_socket, client_address = self.server_socket.accept()
			except socket.error:		
				continue			# will need to start doing something fancier when we start handling SIGCHLD	

			self.logwrite("Accepted connection from " + str(client_address) + ".\n")
			
			request = ""
			datalen = -1
			while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire request
				data = client_socket.recv(1024)
				datalen = len(data)
				request += data
			
			self.logwrite("Client request: '" + request + "'\n")
			
			response = self.respond(request)
			if response is not None:		# don't waste our time sending a response to an invalid request.
				self.logwrite("Attempting to send response:\n===\n" + response + "\n===\n")
				try:
					client_socket.sendall(response)		# this will throw an exception if all the data can't be sent.
				except:
					self.logwrite("Transmission error.\n")
					pass								# what to do if it can't all be sent?  hmm...
				else:
					self.logwrite("Transmission completed.\n")
			else:
				self.logwrite("Request is invalid.  ")

			self.logwrite("Closing socket.\n")
			client_socket.close()
		
		self.logwrite("Instructed to close.  Exiting dispatch mode.\n")
		self.cleanup()

			
	def respond(self, request):
		"""
		Decides what to do with a particular request.
		Returns None for invalid requests.
		"""
		matches = re.match("^(?P<request>\S+)\s?(?P<data>\S*)[?!]$", request)
		if matches is None:
			self.logwrite("Request does not match pattern.\n")
			return None
		
		request = matches.group("request").lower()
		data = matches.group("data")
		
		handlers = { "alive" : self.ping,
		             "daq_running" : self.daq_status,
		             "daq_last_exit" : self.daq_exitstatus,
		             "daq_start" : self.daq_start,
		             "daq_stop" : self.daq_stop,
		             "sc_sethwconfig" : self.sc_sethw,
		             "sc_voltages" : self.sc_readvoltages }
		
		if request in handlers:
			if len(data) > 0:
				return handlers[request](data)
			else:
				return handlers[request]()
		else:
			return None
		

	def ping(self):
		""" Returns something so that a client knows the server is alive. """
		return "0"
	
	def daq_status(self):
		""" Returns 1 if there is a DAQ subprocess running; 0 otherwise. """
		
		if self.daq_process is None or self.daq_process.returncode != None:
			return "0"
		else:
			return "1"
	
	def daq_exitstatus(self):
		""" Returns the exit code last given by a DAQ subprocess, or,
		    if no DAQ process has yet exited, returns -1. """
		if self.daq_process is None or self.daq_process.returncode is None:
			return "-1"
		else:
			return str(self.daq_process.returncode)

	def daq_start(self):
		""" Starts the DAQ slave service as a subprocess (implemented
		    via standard UNIX fork-exec, but never mind).  First checks
		    to make sure it's not already running.  Returns 0 on success,
		    1 on some DAQ or other error, and 2 if there is already
		    a DAQ process running. """
		
		if self.daq_process and self.daq_process.returncode is not None:
			return "2"
		
		try:
			self.daq_process = subprocess.Popen("/work/software/mnvdaq/bin/daq_slave_service", env={"DAQROOT": Defaults.DAQROOT_DEFAULT})
		except:
			return "1"
		else:
			return "0"
	
	def daq_stop(self):
		""" Stops a DAQ slave service.  First checks to make sure there
		    is in fact such a service running.  Returns 0 on success,
		    1 on some DAQ or other error, and 2 if there is no DAQ
		    process currently running. """
		    
		if self.daq_process and self.daq_process.returncode is not None:
			try:
				self.daq_process.kill()
			except:
				return "1"
		else:		# if there's a process but it's already finished
			return "2"
		
		return "0"
		
	def sc_sethw(self, filename):
		""" Uses the slow control library to load a hardware configuration
		    file.  Returns 0 on success, 1 on hardware error, and 2 if 
		    there is no such file. """
		    
		return "0"
		    
	def sc_readvoltages(self):
		""" Uses the slow control library to read the FEB voltages.
		    On success, returns a string of lines consisting of
		    1 voltage per line, in the following format:
		    FPGA-CROC-CHAIN-BOARD: [voltage]
		    On failure, returns the string "NOREAD". """

		return "NOREAD"
		
	def cleanup(self):
		self.server_socket.close()

		if os.path.isfile(Defaults.DISPATCHER_PIDFILE):
			self.logwrite("Removing PID file.\n")
			os.remove(Defaults.DISPATCHER_PIDFILE)
                        
# whew, that's a mouthful.
class RunControlDispatcherAlreadyStartedException(Exception):
	pass

####################################################################
####################################################################
"""
  This module should probably never be imported elsewhere.
  It's designed to run directly as a background process that handles
  incoming requests for the DAQ slave service and slow control.
  
  If it IS running as a stand-alone, it will need to daemonize
  and begin listening on the specified port.
  
  Otherwise it will bail with an error.
"""
if __name__ == "__main__":
	import optparse
	
	parser = optparse.OptionParser(usage="usage: %prog [options] command\n  where 'command' is 'start' or 'stop'")
	parser.add_option("-r", "--replace", dest="replace", action="store_true", help="Replace a currently-running instance of the service with a new one. Default: %default.", default=False)
	parser.add_option("-i", "--interactive", dest="interactive", action="store_true", help="Run in an interactive session (don't daemonize).  Default: %default.", default=False)
	
	(options, commands) = parser.parse_args()
	
	if len(commands) != 1 or not(commands[0].lower() in ("start", "stop")):
		parser.print_help()
		sys.exit(0)

	command = commands[0].lower()
	
	dispatcher = RunControlDispatcher()
	
	
	if command == "start":
		dispatcher.interactive = options.interactive
		dispatcher.replace = options.replace
		
		if dispatcher.interactive:
			print "Running in interactive mode.  All log information will be echoed to the screen."
			print "Enter 'Ctrl-C' to exit.\n\n"
		else:
			print "Dispatcher starting in daemon mode.  \nRun this program with the keyword 'stop' to stop it."
		dispatcher.start()
	elif command == "stop":
		dispatcher.interactive = True
		dispatcher.replace = False
		dispatcher.stop()
	
	sys.exit(0)
else:
	raise RuntimeError("This module is not designed to be imported!")
