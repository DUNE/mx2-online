"""
  Dispatcher.py:
  Base class for a listener service that listens for instructions
  from the run control across a socket.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import socket
import signal
import select
import errno
import time
import sys
import os
import os.path
import re
import logging
import logging.handlers
import threading
from Queue import Queue

from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import Configuration

# an enumeration.
MASTER = 0

class Dispatcher:
	"""
	This guy is the one who listens for requests and handles them.
	There should NEVER be more than one instance running at a time!
	(They wouldn't both be able to bind to the port...)  Thus the
	start() method checks before allowing dispatching to be started.
	"""
	def __init__(self):
		self.port = Configuration.params["Socket setup"]["dispatcherPort"]
		self.interactive = False
		self.respawn = False
		self.quit = False
		
		# so that I can receive messages from other threads without hanging.
		self.queue = Queue()
		
		# derived classes must override this.
		self.pidfilename = None

		# basic requests and methods.
		# derived classes can extend these if they want to.
		self.valid_requests = SocketRequests.GlobalRequests[:]
		self.handlers = { "alive"        : self.ping,
		                  "get_lock"     : self.get_lock,
		                  "release_lock" : self.release_lock }
		
		# keeps track of client that has a lock (and the name it's using for this node)
		self.identity = None
		self.lock_id = None
		self.lock_address = None
		
		# workhorse socket
		self.server_socket = None
		
		# we don't need to print EVERY request when a client
		# is requesting the same thing many times in a row.
		# we'll use these properties to keep track.
		self.last_request = {}
		self.request_count = {}
		
		# set up some logging facilites.
		# we leave it to derived classes to implement a file handler
		# if they want one.
		# we set up a console handler that will be used for interactive sessions.
		self.logger = logging.getLogger("dispatcher")
		self.logger.setLevel(logging.DEBUG)
		self.formatter = logging.Formatter("[%(asctime)s] %(levelname)s:  %(message)s")
		self.consolehandler = logging.StreamHandler()
		self.consolehandler.setFormatter(self.formatter)
		self.logger.addHandler(self.consolehandler)
		
		# derived classes can use this to indicate methods
		# that should be run before shutdown (for cleanup purposes).
		self.cleanup_methods = []

		# make sure that the process shuts down gracefully given the right signals.
		# these lines set up the signal HANDLERS: which functions are called
		# when each signal is received.
		signal.signal(signal.SIGINT, self.shutdown)
		signal.signal(signal.SIGTERM, self.shutdown)
		
	def setup(self):
		try:
			self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# create an IPv4 TCP socket.
			
			# accept any incoming connections to the port regardless of origin
			self.server_socket.bind(("", self.port))

			self.server_socket.setblocking(0)			# need to be able to handle messages.  don't block!
			self.server_socket.listen(3)				# allow it to keep a few backlogged connections (that way if we're trying to talk to it too fast it'll catch up)
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
		
		if self.pidfilename is None:
			raise Exception("Derived dispatcher classes must specify where the PID file is to be kept!")
		
		self.logger.info("Starting up.")
		
		other_instance_pid = self.other_instances()
		if other_instance_pid:
			if self.replace:
				self.kill_other_instance(other_instance_pid)
			else:
				self.logger.fatal("Terminating this instance.")
				sys.exit(1)

		self.setup()

		# don't daemonize or make a PID file if we're quitting anyway
		if not self.quit:
			# make sure this thing is a daemon if it needs to be
 			if not self.interactive:
				self.daemonize()
		
			self.logger.info("Creating new PID file.  My PID: " + str(os.getpid()) + "")
			
			pidfile = open(self.pidfilename, 'w')
			pidfile.write(str(os.getpid()) +"\n")
			pidfile.close()
		
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
		
	def cleanup(self):
		self.server_socket.close()
		
		for cleanup_method in self.cleanup_methods:
			cleanup_method()

		if os.path.isfile(self.pidfilename):
			self.logger.info("Removing PID file.")
			os.remove(self.pidfilename)

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

		# Iterate through and close all open file descriptors...
		for fd in range(maxfd):
			# ... except the one corresponding to our socket.
			if self.server_socket is not None and fd == self.server_socket.fileno():
				continue
				
			try:
				os.close(fd)
			except OSError:	# fd wasn't open to begin with (ignored)
				pass
		
		# Redirect stdin to /dev/null.
		# [os.open uses the first available file descriptor if none is given,
		# which will be 0 here (stdin) since we just finished closing everything.]
		os.open(os.devnull, os.O_RDWR)	# standard input (0)

		# Duplicate standard input to standard output and standard error.
		# That way they also go to /dev/null.
		os.dup2(0, 1)			# standard output (1)
		os.dup2(0, 2)			# standard error (2)


		return

	def other_instances(self):
		if self.pidfilename is None:
			raise Exception("Derived dispatcher classes must specify where the PID file is to be kept!")
	
		self.logger.info("Checking for PID file...")
		
		if os.path.isfile(self.pidfilename):
			pidfile = open(self.pidfilename)
			pid = int(pidfile.readline())
			pidfile.close()

			self.logger.info("Found PID file with PID " + str(pid) + ".")

			try:
				self.logger.info("Checking if process is alive...")
				os.kill(pid, 0)		# send it the null signal to check if it's there and alive.
			except OSError:			# you get an OSError if the PID doesn't exist.  it's safe to clean up then.
				self.logger.info("Process is dead.  Cleaning up PID file.")
				os.remove(self.pidfilename)
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
		on the port before entering dispatch mode).
		"""
		if not self.quit:		# occasionally there's an error before dispatching starts.
#			self.logger.info("Master node will be contacted at '" + self.master_address + "'.")
			self.logger.info("Dispatching starting (listening on port " + str(self.port) + ").")

		while not self.quit:
			# if we interrupt the select() or socket accept() system calls by receiving a signal,
			# they throw an exception as a warning.  we should just start over then,
			# which will cause a quit (the signal handler for the only signals
			# we're handling--SIGTERM and SIGINT--sets self.quit to True).
			try:
				# use select() to see if there's a client trying to connect
				if select.select([self.server_socket], [], [], 0)[0]:		
					try:
						client_socket, client_address = self.server_socket.accept()
						client_address = client_address[0]	# we can discard the port number.  it's not important.
					except Exception, e:
						self.logger.exception("Error trying to get socket:")

					request = ""
					datalen = -1
					while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire request
						data = client_socket.recv(1024)
						datalen = len(data)
						request += data
			
					if request == "":
						self.logger.info("Blank request from " + client_address + ".  Assuming pipe was broken and ignoring.")
						client_socket.close()
						continue
					elif client_address in self.last_request and request == self.last_request[client_address]:
						self.request_count[client_address] += 1
					else:
						if client_address in self.last_request and self.request_count[client_address] > Configuration.params["Dispatchers"]["maxRepeatedRequestLogs"]:
							self.logger.info("Note: previous request received from client " + client_address + " " + str(self.request_count[client_address] - Configuration.params["Dispatchers"]["maxRepeatedRequestLogs"]) + " more times...")
						self.last_request[client_address] = request
						self.request_count[client_address] = 1
				
					show_request_details = self.request_count[client_address] <= Configuration.params["Dispatchers"]["maxRepeatedRequestLogs"]
					if show_request_details:
						self.logger.info("Received request from client " + client_address + ": '" + request + "'")
			
					if self.request_count[client_address] == Configuration.params["Dispatchers"]["maxRepeatedRequestLogs"]:
						self.logger.info("Note: request repeated " + str(Configuration.params["Dispatchers"]["maxRepeatedRequestLogs"]) + " times.")
						self.logger.info("      Further consecutive repeats of this request")
						self.logger.info("      from this client will not be logged.")
			
					response = self.respond(request, client_address, show_request_details)
					if response is not None:		# don't waste our time sending a response to an invalid request.
						if show_request_details:
							self.logger.info("Attempting to send response:\n" + response)
						try:
							client_socket.sendall(response)		# this will throw an exception if all the data can't be sent.
						except:
							self.logger.warning("Transmission error.")	# what to do if it can't all be sent?  hmm...
						else:
							if show_request_details:
								self.logger.info("Transmission completed.")
					else:
						self.logger.info("Request is invalid.")

					try:
						client_socket.shutdown(socket.SHUT_RDWR)
						if show_request_details:
							self.logger.info("Socket closed.")
					except socket.error:
						self.logger.exception("Socket error on socket shutdown:")
						self.logger.error("   ==> Data transmission was interrupted!")
					finally:
						client_socket.close()
			except (socket.error, select.error), (errnum, msg):
				if errnum == errno.EINTR:		# the code for an interrupted system call
					continue
				else:						# if it's not an interrupted system call, we need the error!
					self.logger.exception("Error " + str(errnum) + ": " + msg)
					
			# check for messages on the queue
			if not self.queue.empty():
				item = self.queue.get()
				
				if item.recipient == MASTER:
					if self.lock_address is not None:
						self.send_message("FOR:%s FROM:%s MSG:%s" % (self.lock_id, self.identity, item.message), self.lock_address, Configuration.params["Socket setup"]["masterPort"])
					else:
						self.logger.warning("Can't send message to master because no one has a client lock...")
				else:
					self.send_message(item.message, item.recipient)
	
		self.logger.info("Instructed to close.  Exiting dispatch mode.")
		self.cleanup()

			
	def respond(self, request, client_address, show_request_details = True):
		"""
		Decides what to do with a particular request.
		Returns None for invalid requests.
		"""
		
		# if it's an imperative request, we need to extract
		# the requester's ID to make sure they're allowed to make it.
		id = None
		if request[-1] == "!":
			imperative_request = True
			matches = re.match("^.* (?P<id>[\d\w\-]+)!$", request)
			if matches is None:
				self.logger.info("Imperative request did not contain requester ID:")
				self.logger.info(request)
				return None
			
			id = matches.group("id")
			
			# if there's a lock in place already, the only one who's allowed to do anything
			# is at the SAME IP address with the SAME id.
			if self.lock_id is not None and (id != self.lock_id or client_address != self.lock_address):
				self.logger.warning("Imperative request from requester other than the one who has the lock:")
				self.logger.warning("'%s'" % request)
				self.logger.warning("Request ignored.")
				return "NOTALLOWED"
			# this is definitely not a very secure ID check, but at least it prevents
			# basic spoofing.  we verify that the provided ID is a UUID.
			elif self.lock_id is None and re.match("^[\da-f]{8}(-[\da-f]{4}){3}-[\da-f]{12}$", id) is None:
				self.logger.warning("Imperative request received with invalid ID:")
				self.logger.warning(request)
				self.logger.warning("Request ignored.")
				return "NOTALLOWED"
			
			# now remove the ID from the request so that it matches the pattern.
			request = request.replace(" %s" % id, "")
		else:
			imperative_request = False
		
		is_valid_request = False
		is_global_request = False
		for valid_request in self.valid_requests:
			matches = re.match(valid_request, request)
			if matches is not None:
				is_valid_request = True
				if valid_request in SocketRequests.GlobalRequests:
					is_global_request = True
				break
		
		if not is_valid_request:
			self.logger.info("Request does not match pattern.")
			return None

		request = matches.group("request").lower()
		
		# if this is an imperative request and the ID is ok, but there is currently no lock,
		# and it's not a manager request, then we don't want to allow it.  otherwise we
		# will have no return address for commands that send feedback to the client,
		# and we run the risk of multiple nodes trying to issue commands simultaneously.
		# inform the client that they need a lock first.
		if imperative_request and self.lock_id is None and not is_global_request:
			self.logger.warning("Imperative request received with no lock present.  Ignoring...")
			return "NOLOCK"

		if request in self.handlers:
			if id is not None:
				return self.handlers[request](matches, show_details=show_request_details, lock_id=id, client_address=client_address)
			else:
				return self.handlers[request](matches, show_details=show_request_details)
		else:
			return None
		

	def ping(self, matches, show_details):
		""" Returns something so that a client knows the server is alive. """
		if show_details:
			self.logger.info("Responding to ping.")
		return "1"
	
	def get_lock(self, matches=None, show_details=None, lock_id=None, client_address=None, **kwargs):
		""" Tries to get a run lock for this client.
		    Returns 1 on success and 0 on failure. """
		self.logger.info("Client wants a command lock.")
		if self.lock_id is None:
			self.lock_id = lock_id
			self.lock_address = client_address
			
			if "identity" in matches.groupdict():
				self.identity = matches.group("identity")
			else:
				self.logger.warning("   No identity supplied!  Identity will be blank...")
				self.identity = ""
			self.logger.info("   ==> Lock granted to client with id '%s'.  My identity: '%s' node." % (self.lock_id, self.identity))
			return "1"
		elif self.lock_id == lock_id:
			self.logger.info("   ==> This client already has a lock!  No action taken.")
			return "1"
		else:
			self.logger.info("   ==> Another client already has a lock.  Lock denied.")
			return "0"
	
	def release_lock(self, matches, show_details, lock_id, **kwargs):
		""" Releases the run lock.
		    Returns 0 if this client doesn't own the lock,
		    1 if release was successful,
		    and -1 if there is no lock currently in place. """
		self.logger.info("Client wants to release the command lock.")
		if self.lock_id is None:
			self.logger.info("   ==> No lock to release.")
			return "-1"
		elif self.lock_id != lock_id:
			self.logger.info("   ==> Lock is owned by a different client.  Lock retained.")
			return "0"

		self.lock_id = None
		self.lock_address = None
		self.identity = None
		self.logger.info("   ==> Lock released.")
		return "1"
		
	
	def send_message(self, message, recipient_addr=None, recipient_port=None):
		""" Sends a message to the master node that currently has a lock,
		    or, if there is currently no lock, to the specified recipient. """
		
		recipient_addr = recipient_addr if recipient_addr is not None else self.lock_address
		recipient_port = recipient_port if recipient_port is not None else Configuration.params["Socket setup"]["masterPort"]
		if recipient_addr is None:
			self.logger.warning("Asked to send a mesage but no lock and recipient not specified.  Ignoring...")
			return
		
		MasterMessageSenderThread(self.logger, (recipient_addr, recipient_port), message)
		

	def bootstrap(self):
		""" Handles the processing of command-line arguments
		    and starts the dispatcher processes.
		    Derived classes should call this in a 
		    if __name__=="__main__"  block.  """
		import optparse
	
		parser = optparse.OptionParser(usage="usage: %prog [options] command\n  where 'command' is 'start' or 'stop'")
		parser.add_option("-r", "--replace", dest="replace", action="store_true", help="Replace a currently-running instance of the service with a new one. Default: %default.", default=False)
		parser.add_option("-i", "--interactive", dest="interactive", action="store_true", help="Run in an interactive session (don't daemonize).  Default: %default.", default=False)
#		parser.add_option("-m", "--master-address", dest="masterAddress", help="The internet address of the master node.  Default: %default.", default=Defaults.MASTER)
	
		(options, commands) = parser.parse_args()
	
		if len(commands) != 1 or not(commands[0].lower() in ("start", "stop")):
			parser.print_help()
			sys.exit(0)

		command = commands[0].lower()
	
		if command == "start":
			self.interactive = options.interactive
			self.replace = options.replace
#			self.master_address = options.masterAddress
		
			if self.interactive:
				print "Running in interactive mode."
				print "All log information will be echoed to the screen."
				print "Enter 'Ctrl-C' to exit.\n\n"
			else:
				print "Dispatcher starting in daemon mode."
				print "Run this program with the keyword 'stop' to stop it."
				print "Also see the log file.\n"
			self.start()
		elif command == "stop":
			self.interactive = True
			self.replace = False
			self.stop()


##################################################
# MasterMessageSenderThread                      #
##################################################
class MasterMessageSenderThread(threading.Thread):
	""" Thread to take care of the sending messages to the master node.
	    (This could block so it needs a separate thread.) """
	def __init__(self, logger, recipient, message):
		threading.Thread.__init__(self)
		
		self.logger = logger		# loggers are thread-safe, so we can just use it directly.
		
		self.recipient = recipient
		self.message = message
		
		self.start()
	
	def run(self):
		tries = 0
		success = False
		    
		while tries < Configuration.params["Socket setup"]["maxConnectionAttempts"] and not success:
			self.logger.info("Attempting to send a message to '%s':" % str(self.recipient))
			self.logger.info(self.message)
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.settimeout(Configuration.params["Socket setup"]["socketTimeout"])
				s.connect( self.recipient )
				s.send(self.message)
				s.shutdown(socket.SHUT_WR)
				self.logger.info("Message sent successfully.")
				success = True
			except:
				self.logger.info("  ==> Communication interrupted.")
				tries += 1
				if tries < Configuration.params["Socket setup"]["maxConnectionAttempts"]:
					self.logger.info("  ==> Will try again in 1s.")
				time.sleep(Configuration.params["Socket setup"]["connAttemptInterval"])
			finally:
				s.close()
	

class Message:
	""" A message (put this into the queue). """
	def __init__(self, message, recipient=None):
		self.recipient = recipient		# None is for messages sent to the log
		self.message = message
