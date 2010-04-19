"""
   RemoteNode.py:
    This module is the base class for remote
    nodes that need to be contacted via a socket.
    It handles the socket connection and implements
    a simple 'ping' request.  It also contains the
    mechanism for getting a 'command' lock (i.e.,
    making this particular instance the only one
    that can issue commands to the node that will
    change its behavior).
    
    Dispatchers expect this instance's ID to be
    sent along with any 'imperative' request
    (i.e., one that will result in a change in
    state), so that is done transparently here.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Mar.-Apr. 2010
                    
   Address all complaints to the management.
"""

import re
import uuid
import time
import socket
import fcntl		# needed for file-locking operations

from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import Configuration


class RemoteNode:
	def __init__(self, name, address, id=None):
		if id is not None:
			self.id = id
		else:
			self.id = str(uuid.uuid4())		# create a random unique identifier for this instance.
	
		self.socket = None
		self.name = name
		self.address = address
		self.nodetype = "unspecified"			# derived classes should overwrite this
		self.port = Configuration.params["Socket setup"]["dispatcherPort"]
		self.ValidRequests = SocketRequests.GlobalRequests	# derived classes can add more to this if they want to
		
		self.own_lock = False
		
	def request(self, request):
		""" The workhorse method that actually contacts the remote node,
		    delivers the request, gets the response, and sends that back
		    to the method that processes it. """
		    
		is_valid_request = False	
		is_global_request = False
		for valid_request in self.ValidRequests:
			if re.match(valid_request, request) is not None:
				is_valid_request = True
				break
		
		if not is_valid_request:
			raise RemoteNodeBadRequestException("Invalid request: '" + request + "'")
		
		# if this is a "!"-type command, it asks the node to change something.
		# in that case we need to pass this instance's ID along so the node
		# can check if this one has permission to make that command.	
		if request[-1] == "!":
			request = request[0:-1] + (" %s!" % self.id)
		
		tries = 0
		success = False
		while tries < Configuration.params["Socket setup"]["maxConnectionAttempts"] and not success:
			# if this is a later attempt, we should wait a little to give the network a chance to catch up.
			if tries > 0:
				time.sleep(Configuration.params["Socket setup"]["connAttemptInterval"])
				
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.socket.settimeout(Configuration.params["Socket setup"]["socketTimeout"])
				self.socket.connect( (self.address, self.port) )
				self.socket.send(request)
				self.socket.shutdown(socket.SHUT_WR)		# notifies the server that I'm done sending stuff

				response = ""
				datalen = -1
				while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire response
					data = self.socket.recv(1024)
					datalen = len(data)
					response += data

				success = True
			except (socket.error, socket.timeout) as e:
#				print "socket error..."
#				print e
				tries += 1
				continue
#			except:
#				print "a different error..."
#				#print e
			finally:
				self.socket.close()
				
			# an empty response is the sign of a broken connection.
			# (none of the queries will return with a blank response.)
			# we'll want to try again.
			if response == "":
				success = False
				tries += 1
				continue

		if tries == Configuration.params["Socket setup"]["maxConnectionAttempts"]:
			raise RemoteNodeNoConnectionException()

		return response
	
	def ping(self):
		""" Requests confirmation from the server that it is indeed alive and well. """
		try:
			response = self.request("alive?")
		except:
			return False
		
		return len(response) > 0		# if we got ANYTHING back, then it's alive
		
	def get_lock(self):
		""" Tries to get a 'command' lock (i.e., one making this particular instance the only one
		    that can issue commands to the node that will change its behavior). 
		    Also updates the session file to reflect this.
		    
		    Returns True on success and False on failure.  """
		
		# don't need another one if I've already got one.
		if self.own_lock:
			return True
		
		try:
			response = self.request("get_lock %s!" % self.name)
		except RemoteNodeNoConnectionException:
			return False
		
		self.own_lock = response == "1"
		if self.own_lock:
			pattern = re.compile("^(?P<type>\S+) (?P<id>[a-eA-E\w\-]+) (?P<address>\S+)$")
			
			rewrite = False
			try:
				sessionfile = open(Configuration.params["Master node"]["sessionfile"], "r+")
				rewrite = True
			except IOError:		# file not found
				try:
					sessionfile = open(Configuration.params["Master node"]["sessionfile"], "w")
				except (IOError, OSError):
					msg = "Couldn't open lock file!  %s node will need to be manually unlocked..." % self.name
					print msg
					self.logger.critical(msg)
					return False
			try:
				# we need a lock on this file so that it doesn't change under our feet
				# (if another node gets a lock, for example).
				# note that this blocks until the lock can be made ...
				fcntl.flock(sessionfile.fileno(), fcntl.LOCK_EX)
				try:
					if rewrite:
						lines = sessionfile.readlines()
						out = []
						matched = False
						for line in lines:
							matches = pattern.match(line)
							# replace an old line corresponding to this id
							if matches is not None and matches.group("id") == self.id:
								line = "%s %s %s\n" % (self.nodetype, self.id, self.address)
								matched = True
							out.append(line)
						if not matched:
							out.append("%s %s %s\n" % (self.nodetype, self.id, self.address))
						sessionfile.seek(0)
					else:
						out = "%s %s %s\n" % (self.nodetype, self.id, self.address)
					sessionfile.writelines(out)
				finally:		# be sure to ALWAYS release the lock no matter what happens
					fcntl.flock(sessionfile.fileno(), fcntl.LOCK_UN)
			finally:			# this file should always be closed so that we don't hang somewhere else
				sessionfile.close()
					
		return self.own_lock

	def release_lock(self):
		""" Releases a lock gotten by get_lock().
		    Also updates the session file to reflect this.

		    Returns True on success and False on failure.  """
		
		# if I don't already own a lock, I don't need to do anything more.
		if not self.own_lock:
			return True
		
		try:
			response = self.request("release_lock!")
		except RemoteNodeNoConnectionException:
			return False
		
		self.own_lock = not(response == "1")

		if not self.own_lock:
			pattern = re.compile("^(?P<type>\S+) (?P<id>[a-eA-E\w\-]+) (?P<address>\S+)$")
			try:
				sessionfile = open(Configuration.params["Master node"]["sessionfile"], "w")
			except (IOError, OSError):
				msg = "Couldn't open lock file!...  Where did it go?"
				print msg
				self.logger.warning(msg)
			else:
				# first lock the file (as described in get_lock())
				fcntl.flock(sessionfile.fileno(), fcntl.LOCK_EX)
				
				# now read the file and delete any lines corresponding to this node
				try:
					lines = sessionfile.readlines()
					out = []
					for line in lines:
						matches = pattern.match(line)
						if matches is None or matches.group("id") != self.id:
							out.append(line)
					sessionfile.seek(0)
					sessionfile.writelines(out)
				finally:
					fcntl.flock(sessionfile.fileno(), fcntl.LOCK_UN)

		return not(self.own_lock)


class RemoteNodeBadRequestException(Exception):
	pass

class RemoteNodeNotConfiguredException(Exception):
	pass

class RemoteNodeNoConnectionException(Exception):
	pass
