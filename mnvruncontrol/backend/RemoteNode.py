"""
   RemoteNode.py:
    Encapsulates some of the tasks associated with
    the management of a remote node that has a
    dispatcher running on it.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    July-Aug. 2010
                    
   Address all complaints to the management.
"""

from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend.PostOffice.Envelope import Message
from mnvruncontrol.backend.PostOffice.Errors import TimeoutError

# first, an enumeration of "types" of remote node
ANY        = 0
READOUT    = 1
MONITORING = 2
MTEST      = 3
PERIPHERAL = 4

NODE_TYPES = (READOUT, MONITORING, MTEST, PERIPHERAL)

# enumeration of statuses
IDLE    = 0
OK      = 1
ERROR   = 2

class RemoteNode:
	""" Models a remote node. """
	
	def __init__(self, nodetype, name, address):
		self.type = nodetype	
		self.name = name
                # TODO fix it so that OM dispatcher and readout dispatcher don't occupy the same socket
		self.address = (address, 1095 if name == "om_node" else Configuration.params["sock_dispatcherPort"])
		
		self.connection_made = False
		self.status = IDLE
		self.locked = False
		
	def SetLocked(self, locked):
		""" Updates the internal 'locked' flag
		    and ensures the session table matches. """

		# NOTICE: session management has been disabled.
		# This method is therefore unnecessary.
		# To preserve the hooks and structure, the former code
		# is left here, and the method basically does nothing.

		self.locked = locked
		return
		
#		# TODO: would be nice to have some file locking (for the session file) here.
#		# unfortunately it's difficult to implement using the shelve db.
#		    

#		filename = Configuration.params["sessionfile"]
#		
#		# we need a lock on this file so that it doesn't change under our feet
#		# (if another node gets a lock, for example).
#		# note that this blocks until the lock can be made ...
#		try:
#			db = shelve.open(filename)
#		except:
#			logging.getLogger("Dispatcher.DAQManager").warning("Can't open session file ('%s')!", filename)
#			return

#		logging.getLogger("Dispatcher.DAQManager").debug("Adjusting node '%s' in session file '%s'...", self.name, filename)

#		try:
#			if "node_list" not in db:
#				db["node_list"] = []
#			
#			matched = False
#			new_list = []
#			for node in db["node_list"]:
#				if node["type"] == self.type and node["name"] == self.name and node["address"] == self.address:
#					matched = True
#					if not self.locked:
#						continue
#					
#					new_list.append(node)
#			
#			if not matched and self.locked:
#				new_list.append( {"type": self.type, "name": self.name, "address": self.address} )
#		finally:			# ALWAYS close the file
#			db.close()

	def InitialContact(self, postoffice, mgr_id):
		""" Sends the initial "daq_mgr" status="online" message
		    to this node (which performs initial configuration). """
		
		message = Message(subject="mgr_status", status="online", mgr_id=mgr_id, node_identity=self.name)
		
		from mnvruncontrol.backend.PostOffice.Logging import logger

		logger().warning("TEST - REACHED INITIAL CONTACT")
		try:
			deliveries = postoffice.SendTo(message=message, recipient_list=[self.address,], timeout=Configuration.params["sock_messageTimeout"])
		except TimeoutError:
			deliveries = []
		
		if len(deliveries) == 0:
			raise NoContactError()
		elif len(deliveries) > 1:
			raise TooManyResponsesError()
			
		self.connection_made = True

class NoContactError(Exception):
	pass

class TooManyResponsesError(Exception):
	pass
