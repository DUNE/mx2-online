"""
  Dispatcher.py:
   Base class for a listener service that listens for instructions
   or requests from a remote client using the PostOffice mechanism.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    July-Aug. 2010
                    
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

import mnvruncontrol.configuration.Logging

from mnvruncontrol.configuration import Configuration
from mnvruncontrol.backend import PostOffice

class Dispatcher(PostOffice.MessageTerminus):
	"""
	This guy is the one who listens for requests and handles them.
	There should NEVER be more than one instance running at a time!
	(They wouldn't both be able to bind to the port...)  Thus the
	start() method checks before allowing dispatching to be started.
	"""
	def __init__(self):
		self.interactive = False
		self.respawn = False
		self.quit = False
		
		# we'll set up the PostOffice after we
		# daemonize (otherwise the fork only will
		# preserve the thread doing the fork...)
		self.postoffice = None
		
		# this can be overridden by a derived class if it wants
		self.socket_port = Configuration.params["Socket setup"]["dispatcherPort"]
		self.server_socket = None
		
		# where this log goes is set up in the Logging module
		self.__logger = logging.getLogger("Dispatcher")
		
		# derived classes must override this.
		self.pidfilename = None

		# keeps track of client that has a lock (and the name it's using for this node)
		self.identities = {}
		self.lock_id = None
		
		# we don't need to print EVERY request when a client
		# is requesting the same thing many times in a row.
		# we'll use these properties to keep track.
		self.last_request = {}
		self.request_count = {}
		
		# methods that should be run as part of the starting-up procedure.
		self.startup_methods = []
		
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
			server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# create an IPv4 TCP socket.
			# allowed to be rebound before a TIME_WAIT, LAST_ACK, or FIN_WAIT state expires
			server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			
			# accept any incoming connections to the port regardless of origin
			server_socket.bind(("", self.socket_port))

			server_socket.setblocking(0)			# need to be able to handle messages.  don't block!
			server_socket.listen(3)				# allow it to keep a few backlogged connections (that way if we're trying to talk to it too fast it'll catch up)
		except socket.error, e:
			self.__logger.exception("Error trying to bind my listening socket:")
			self.__logger.fatal("Can't get a socket.")
			self.shutdown()
		except Exception, e:
			self.__logger.exception("An error occurred while trying to bind the socket:")
			self.__logger.fatal("Quitting.")		
			self.shutdown()
		
		self.__logger.info("Listening on port %d.", self.socket_port)
		
		self.server_socket = server_socket
			
	def start(self):
		""" Starts the listener.  If you want to run it as a background
		    service, make sure the attribute 'interactive' is False. 
		    This is normally accomplished by not setting the "-i" flag
		    on the command line (i.e., it's the default behavior).  """
		
		if self.pidfilename is None:
			raise Exception("Derived dispatcher classes must specify where the PID file is to be kept!")
		
		self.__logger.info("Starting up.")
		
		other_instance_pid = self.other_instances()
		if other_instance_pid:
			if self.replace:
				self.kill_other_instance(other_instance_pid)
			else:
				self.__logger.fatal("Terminating this instance.")
				self.shutdown()
				sys.exit(1)

		self.setup()

		# don't daemonize or make a PID file if we're quitting anyway
		if not self.quit:
			# make sure this thing is a daemon if it needs to be
 			if not self.interactive:
				self.daemonize()
		
			self.__logger.info("Creating new PID file.  My PID: " + str(os.getpid()) + "")
			
			pidfile = open(self.pidfilename, 'w')
			pidfile.write(str(os.getpid()) +"\n")
			pidfile.close()

		# don't set this up until AFTER we have daemonized.
		# both the MessageTerminus and the PostOffice use threads,
		# and apparently os.fork() will only fork the thread
		# actually doing the calling.  doing things this way
		# ensures that the threads are created after the fork
		# and thus are not dropped.
		PostOffice.MessageTerminus.__init__(self)
		self.postoffice = PostOffice.PostOffice(use_logging=True, listen_socket=self.server_socket)
		
		for method in self.startup_methods:
			method()

		# make sure we receive correspondence regarding our lock status
		lock_subscr = PostOffice.Subscription(subject="lock_request", action=PostOffice.Subscription.DELIVER, delivery_address=self)
		self.postoffice.AddSubscription(lock_subscr)
		self.AddHandler(lock_subscr, self.lock_handler)
		
		self.__logger.info("Dispatching started.")
		while not self.quit:
			time.sleep(0.1)
		
		self.__logger.info("Shutting down.")
		self.cleanup()
		self.shutdown()
		
	def shutdown(self, sig=None, frame=None):
		""" Ends the dispatch loop. """

		# when this method is not called as a signal handler
		# we want it to do the other shutdown stuff		
		if sig is None and frame is None:
			self.Close()
			self.postoffice.Shutdown()

		self.quit = True

	def stop(self):
		""" Kills another instance of the dispatcher. """

		self.__logger.info("Checking for other instances to stop...")
		other_pid = self.other_instances()
		
		if other_pid:
			self.__logger.info("Stopping instance with pid " + str(other_pid) + "...")
			self.kill_other_instance(other_pid)
		else:
			self.__logger.info("No other instances to stop.")
			sys.exit(0)
			
		self.__logger.info("Shutdown completed.")
		
	def cleanup(self):
		for cleanup_method in self.cleanup_methods:
			cleanup_method()

		# try to make sure no child processes are left over.
		# they are all within the dispatcher's process group, hopefully.
		os.killpg(os.getpgrp(), signal.SIGTERM)

		if os.path.isfile(self.pidfilename):
			self.__logger.info("Removing PID file.")
			os.remove(self.pidfilename)
		
#		print threading.enumerate()

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
		#  (1) Closing the STD* file descriptors inherited from the parent process.
		#      We don't want open file descriptors that somehow slipped through from the
		#      parent process's controlling terminal.  So we explicitly close the
		#      STDIN, STDOUT, and STDERR file descriptors inherited from the parent.
		#  (2) Redirecting the standard input/output/error file descriptors to /dev/null.
		#      After daemonization, the process no longer has a terminal.  That means
		#      that where standard in/out/error point is undefined.  To make sure that
		#      we don't get any weird side effects from programming mistakes,
		#      we explicitly set them to the NULL device (in case I accidentally
		#      put a 'print' statement somewhere, for example).
		#
		# Google for "UNIX daemonize" or some such if you want more details.

		self.__logger.info("Trying to daemonize... (check the log for further output)")

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

		self.__logger.info("Daemonization succeeded.")

#		# find the maximum file descriptor number
#		import resource
#		maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
#		if (maxfd == resource.RLIM_INFINITY):		# use a default if the OS doesn't want to tell us
#			maxfd = 1024

#		# Iterate through and close all open file descriptors...
#		for fd in range(maxfd):
#			# ... except the one corresponding to our socket.
#			if self.server_socket is not None and fd == self.server_socket.fileno():
#				continue
#				
#			try:
#				os.close(fd)
#			except OSError:	# fd wasn't open to begin with (ignored)
#				pass

		# Close the STD* file descriptors.  We don't close ALL
		# file descriptors because we need one for our socket
		# and (probably) one for our log file.
		for i in range(3):
			os.close(i)
		
		# Redirect stdin to /dev/null.
		# [os.open uses the first available file descriptor if none is given,
		# which will be 0 here (stdin) since we just finished closing 0-2.]
		os.open(os.devnull, os.O_RDWR)	# standard input (0)

		# Duplicate standard input to standard output and standard error.
		# That way they also go to /dev/null.
		os.dup2(0, 1)			# standard output (1)
		os.dup2(0, 2)			# standard error (2)


		return

	def other_instances(self):
		if self.pidfilename is None:
			raise Exception("Derived dispatcher classes must specify where the PID file is to be kept!")
	
		self.__logger.info("Checking for PID file...")
		
		if os.path.isfile(self.pidfilename):
			pidfile = open(self.pidfilename)
			pid = int(pidfile.readline())
			pidfile.close()

			self.__logger.info("Found PID file with PID " + str(pid) + ".")

			try:
				self.__logger.info("Checking if process is alive...")
				os.kill(pid, 0)		# send it the null signal to check if it's there and alive.
			except OSError:			# you get an OSError if the PID doesn't exist.  it's safe to clean up then.
				self.__logger.info("Process is dead.  Cleaning up PID file.")
				os.remove(self.pidfilename)
			else:
				self.__logger.info("Process is still alive.")
				return pid
		else:
			self.__logger.info("No PID file.")
		
		return None
	
	def kill_other_instance(self, pid):
		self.__logger.info("Instructing process " + str(pid) + " to end.")

		os.kill(pid, signal.SIGTERM)
		
		self.__logger.info("Waiting a maximum of 10 seconds for process " + str(pid) + " to end...")
		secs = 0
		while True:
			time.sleep(1)
			secs += 1
			if secs > 10:
				self.__logger.info("Process " + str(pid) + " has not yet terminated.  Kill it manually.")
				sys.exit(1)
				
			try:
				os.kill(pid, 0)
			except OSError:
				break
		self.__logger.info("Process " + str(pid) + " ended.")
	
	def _daq_mgr_status_update(self, message, additional_notification_requests = []):
		""" Method to respond to changes in status of the
		    DAQ manager (books subscriptions, etc.). 
		    
		    Not all dispatchers will want this behavior,
		    so this function must be called explicitly
		    by derived class handlers.  """
		    
		# if it's not properly formatted, ignore it!
		if not ( hasattr(message, "status") and hasattr(message, "mgr_id") ):
			self.logger.info("DAQ manager status message is improperly formatted.  Ignoring...")
			return
		
		if message.status == "online":
			self.logger.info("DAQ manager at %s informs me it is online and that it will refer to me as '%s'.", message.return_path[0], message.node_identity)
			subscr_list = []

			# notice that we insist that messages to be forwarded
			# must come from the DAQ manager itself (max_forward_hops=0)
			for subject in ["mgr_status", "lock_request"] + additional_notification_requests:
				subscr_list.append( PostOffice.Subscription(subject=subject, delivery_address=[None, self.socket_port], max_forward_hops=0) )
			
			self.postoffice.ForwardRequest(message.return_path[0], subscr_list)
			
			# how this manager will refer to my node
			if hasattr(message, "node_identity"):
				self.identities[message.mgr_id] = message.node_identity

		elif message.status == "offline":
			self.logger.info("DAQ manager at %s informs me it is going offline.", message.return_path[0])
			if message.mgr_id in self.identities:
				del self.identities[message.mgr_id]
				
			# don't need to cancel the forward subscriptions
			# because the manager is going down.  they'll get removed anyway.
			
			# unlock this node if the manager going offline is the one
			# who last locked this node
			if self.lock_id == message.mgr_id:
				self.logger.info(" ... will drop the lock it had.")
				self.lock_id = None
	
	
	def lock_handler(self, message):
		""" Handles incoming requests for lock status changes/information.
		
		    Messages must contain at least the attributes 'request'
		    (which can be 'get', 'release', or 'info') and 
		    'requester_id' (which must be the ID of the node making
		    the request).  """

		# NOTICE: session management has been disabled.
		# This method has been modified to ALWAYS allow
		# a client to get a lock.  (That means one DAQ manager
		# can 'steal' a lock from another!)  
		# To preserve the hooks and structure, the former code
		# is left (commented) below.

		response_msg = message.ResponseMessage()

		# lock requests that have no return path are OUTGOING.
		# we don't want to lock ourselves!
		if len(message.return_path) == 0:
			response_msg.subject = "request_response"
			response_msg.success = LockError("Not issuing a lock to my own node!")

		elif not(hasattr(message, "request") and hasattr(message, "requester_id")):
			response_msg.subject = "invalid_request"
		else:
			response_msg.subject = "request_response"
			if message.requester_id in self.identities:
				response_msg.sender = self.identities[message.requester_id]
				
			if message.request == "get":
				self.__logger.info("Client wants a command lock.")
				
				if self.lock_id == message.requester_id:
					self.__logger.info("   ==> This client already has a lock!  No action taken.")
					response_msg.success = True
				else:
					self.lock_id = message.requester_id
					self.__logger.info("   ==> Lock granted to client with id '%s'.", self.lock_id)
					response_msg.success = True


#				if self.lock_id is None:
#					self.lock_id = message.requester_id
#					self.__logger.info("   ==> Lock granted to client with id '%s'.", self.lock_id)
#					response_msg.success = True
#				elif self.lock_id == message.requester_id:
#					self.__logger.info("   ==> This client already has a lock!  No action taken.")
#					response_msg.success = True
#				else:
#					self.__logger.info("   ==> Another client already has a lock.  Lock denied.")
#					response_msg.success = False

			elif message.request == "release":
				self.__logger.info("Client wants to release the command lock.")
				if self.lock_id is None:
					self.__logger.info("   ==> No lock to release.")
					response_msg.success = True
				elif self.lock_id != message.requester_id:
					self.__logger.info("   ==> Lock is owned by a different client.  Lock retained.")
					response_msg.success = False
				else:
					self.lock_id = None
					self.__logger.info("   ==> Lock released.")
					response_msg.success = True

			elif message.request == "info":
				response_msg.is_locked = (self.lock_id is not None)
				response_msg.by_whom = self.lock_id
				response_msg.success = True

		self.postoffice.Send(response_msg)
	
	def client_allowed(self, client_id):
		""" Checks if a client is allowed to issue commands
		    based on the current state of this node's lock. """

		# NOTICE: session management has been disabled.
		# This method is therefore unnecessary.
		# To preserve the hooks and structure, the former code
		# is left here, and the method simply always returns True.
		
		return True
		    
#		if self.lock_id is None:
#			return False
#		
#		return self.lock_id == client_id
		
		
	def bootstrap(self):
		""" Handles the processing of command-line arguments
		    and starts the dispatcher processes.
		    Derived classes should call this in a 
		    if __name__=="__main__"  block.  """
		import optparse
	
		parser = optparse.OptionParser(usage="usage: %prog [options] command\n  where 'command' is 'start' or 'stop'")
		parser.add_option("-r", "--replace", dest="replace", action="store_true", help="Replace a currently-running instance of the service with a new one. Default: %default.", default=False)
		parser.add_option("-i", "--interactive", dest="interactive", action="store_true", help="Run in an interactive session (don't daemonize).  Default: %default.", default=False)
	
		(options, commands) = parser.parse_args()
	
		if len(commands) != 1 or not(commands[0].lower() in ("start", "stop")):
			parser.print_help()
			self.shutdown()
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

			try:
				self.start()
			except:
				self.shutdown()
				raise
		elif command == "stop":
			self.interactive = True
			self.replace = False
			self.stop()
			
class LockError(Exception):
	pass
