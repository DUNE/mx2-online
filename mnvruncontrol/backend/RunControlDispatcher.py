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

		# make sure that the process shuts down gracefully given the right signals.
		signal.signal(signal.SIGINT, self.shutdown)
		signal.signal(signal.SIGTERM, self.shutdown)

	def __del__(self):
		if self.logfile:
			self.logfile.close()
	
	def check_pidfile(self):
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
				self.logwrite("Process is still alive!  Terminating this instance.\n")
				print "There is already one copy of the dispatcher running.  Use the option '--replace' to close it and use a new copy instead."
				sys.exit(1)
		
		self.logwrite("Creating new PID file.  My PID: " + str(os.getpid()) + "\n")
		pidfile = open(Defaults.DISPATCHER_PIDFILE, 'w')
		pidfile.write(str(os.getpid()) +"\n")
		pidfile.close()

	def setup(self):
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# create an IPv4 TCP socket.
		self.server_socket.bind(("", self.port))				# bind it to the port specified in the config., on any interface that will let it, on the local machine
		self.server_socket.listen(1)										# only allow it to keep one backlogged connection


	def logwrite(self, data):
		""" Writes to the logfile.  Includes a flush so that data is written
		    to the file even if the process doesn't shut down cleanly. """
		if not self.logfile:
			self.logfile = open(Defaults.DISPATCHER_LOGFILE, "w")
		
		timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.gmtime())
		self.logfile.write(timestamp + data)
		self.logfile.flush()
	
	def dispatch(self):
		""" 
		Performs the actual work of handling incoming requests 
		and responding to them appropriately.
		"""
		self.quit = False

		self.logwrite("Starting up.\n")
		self.check_pidfile()		# first make sure this is the only instance -- otherwise we won't be able to bind the port
		self.setup()		

		self.logwrite("Dispatching starting (listening on port " + str(self.port) + ").\n")
		
		while not self.quit:
			# if we interrupt the socket system call, by receiving a signal,
			# it throws an exception as a warning.  we should just start over then
			# (because the only signals we're handling right now are SIGTERM and SIGINT).
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
		    
		return "0"
	
	def daq_stop(self):
		""" Stops a DAQ slave service.  First checks to make sure there
		    is in fact such a service running.  Returns 0 on success,
		    1 on some DAQ or other error, and 2 if there is no DAQ
		    process currently running. """
		
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
		
	def shutdown(self, signal=None, frame=None):
		self.quit = True

        def cleanup(self):
		self.server_socket.close()

                if os.path.isfile(Defaults.DISPATCHER_PIDFILE):
                        self.logwrite("Removing PID file.\n")
                        os.remove(Defaults.DISPATCHER_PIDFILE)

####################################################################
####################################################################
"""
  This module should probably never be imported elsewhere.
  It's designed to run directly as a background process that handles
  incoming requests for the DAQ slave service and slow control.
  
  If it IS running as a stand-alone, it will need to daemonize
  and begin listening on the specified port.
  
  Otherwise it won't do anything.
"""
if __name__ == "__main__":
	dispatcher = RunControlDispatcher()
	
	dispatcher.dispatch()
	
	sys.exit(0)
