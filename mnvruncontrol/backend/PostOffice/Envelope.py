"""
   Envelope.py:
    Classes modeling Messages or their delivery information.
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    June-October 2010
                    
   Address all complaints to the management.
"""

import pprint
import uuid

from mnvruncontrol.backend.PostOffice import Configuration
from mnvruncontrol.backend.PostOffice.NetworkTypes import IPv4Address

from mnvruncontrol.backend.PostOffice.Logging import logger

class Message:
	""" Models a message. """

	def __init__(self, subject, sender=None, in_reply_to=None, max_forward_hops=-1, **kwargs):
		""" Constructor.  
		    
		    This is a pretty simple class, so it just
		    sets up the basic attributes using the
		    information provided. """
		    
		self.id               = uuid.uuid4()		# a random, unique ID
		self.subject          = subject
		self.sender           = sender
		self.max_forward_hops = max_forward_hops
		self.in_reply_to      = in_reply_to
		
		self._direct_delivery = False				# will be delivered only by subscriptions
		                                             # that particularly specify this message's ID
		
		# add the user-specified attributes
		for kwarg in kwargs:
			self.__dict__[kwarg] = kwargs[kwarg]
		
		
		self.return_address = None			# will be set by the sending post office
		self.return_path = []				# ditto
		
	def __repr__(self):
		""" Generate a printable representation of the message. """
		
		return pprint.pformat(self.__dict__)
		
	def ResponseMessage(self, subject="response_message", sender=None, **kwargs):
		""" Creates a new message that will be interpreted as
		    a message replying to this one. """
		    
		# a response message is necessarily "in reply to" this one.
		# don't let the user specify a different one!
		if "in_reply_to" in kwargs:
			del kwargs["in_reply_to"]
		    
		return Message(subject, sender, self.id, **kwargs)
		
class Subscription:
	""" Subscriptions are used to match incoming messages.
	
	    Recipients specify which messages they're interested in
	    by using Subscriptions.  (If a PostOffice doesn't have
	    a subscription matching an incoming message, the message
	    will simply be discarded.) """

	# class constants
	FORWARD = 1
	DELIVER = 2

	def __init__(
		self,
		subject="*", 
		sender="*",
		in_reply_to="*",
		action=None,
		delivery_address=None,
		postmaster_ok=False,
		expiry=-1,
		max_forward_hops=-1,
		other_attributes={}
	):
		""" Constructor.
	    
	         Notice that by default (if no parameters are specified)
	         a subscription that matches all messages and does nothing 
	         with them is created.
	         
	         The parameters are as follows:
	           subject:          match messages with this subject. 
	           sender:             "      "       "    "  sender. 
	           in_reply_to:        "      "     replying to the specified one.
	           
	             (note that the previous three parameters can be specified
	              as '*' which means 'match everything')
	           
	           action:           what the Post Office should do with messages
	                             that match this subscription.  
	                             Can be FORWARD, DELIVER, or None. 
	           delivery_address: where the message should be sent.
	                             if action is DELIVER, this should be a
	                                MessageTerminus instance.
	                             if action is FORWARD, this should be a
	                                (IP address, port) tuple.
	                             if action is None, this should also be None.
	           postmaster_ok:    should this subscription be allowed to match
	                             messages with 'postmaster' subject line?
	           expiry:           how many times this subscription can match
	                             until it's automatically removed.  '-1' means
	                             'no limit'.
	           max_forward_hops: the maximum number of times a message can have
	                             been forwarded and still match this subscription.
	                             in this scheme, 0 means "must originate locally,"
	                             and -1 means "any number of forwards."
	                             ignored if 'action' is not FORWARD.
	           other_attributes: other attributes that a message must have,
	                             specified as {attr_name: required_value} in
	                             the dictionary.  """

		# try to forestall any problems.  if the delivery_address is
		# an iterable type, it's probably supposed to be an IP address.
		# convert it to an IPv4Address straightaway.
		# however, if that doesn't work, don't fail yet -- we don't
		# know what the action is supposed to be yet.
		if hasattr(delivery_address, "__iter__"):
			try:
				delivery_address = IPv4Address.from_iter(delivery_address)
			except Exception:
				pass			
	    
		# NOW we check against the action.
		if action in (Subscription.FORWARD, Subscription.DELIVER):
			if action != Subscription.DELIVER:
				if not isinstance(delivery_address, IPv4Address):
					try:
						delivery_address = IPv4Address.from_iter(delivery_address)
					except Exception:
						raise AttributeError("FORWARD action requires a delivery_address in (host, port) format...")
			elif action == Subscription.DELIVER and not hasattr(delivery_address, "_TakeDelivery"):
				raise AttributeError("DELIVER action requires delivery_address to be a MessageTerminus object...")
		elif action is not None:
			raise AttributeError("Invalid action.")
		
		# for hashing purposes
		self._id = uuid.uuid4()
		
		self.subject                    = subject
		self.sender                     = sender
		self.in_reply_to                = in_reply_to
		self.action                     = action
		self.delivery_address           = delivery_address
		self.postmaster_ok              = postmaster_ok
		self.expiry                     = expiry
		self.max_forward_hops           = max_forward_hops
		self.other_attributes           = other_attributes
		
		self.times_matched              = 0
		self.messages_delivered         = []
		
		# don't allow accidentally conflicting subscriptions
		if subject == "postmaster":
			self.postmaster_ok = True
	
	def __contains__(self, other):
		""" Implements the 'in' operator.
		
		    This method exists to provide the functionality
		    for checking if one subscription is a subset of
		    the other.  Note that the order DOES matter:
		    
		    a in b
		    
		    is not the same thing as
		    
		    b in a
		    
		    unless a and b are identical!  """
		    
		try:
			subjects_match   = self.subject == "*" or self.subject == other.subject
			senders_match    = self.sender == "*" or self.sender == other.sender
			reply_match      = self.in_reply_to == "*" or self.in_reply_to == other.in_reply_to
			deliver_match    = self.delivery_address is None or self.delivery_address == other.delivery_address
			postmaster_match = self.postmaster_ok or self.postmaster_ok == other.postmaster_ok
			
			# careful.  specification of other attributes
			# makes a subscription LESS general, not MORE.
			# therefore they must have the same attributes
			# or 'other' may possibly have more attributes
			# (but NOT vice versa!).
			other_match = True
			for criterion in self.other_attributes:
				if criterion not in other.other_attributes or other.other_attributes[criterion] != self.other_attributes[criterion]:
					other_match = False
					break

		except AttributeError:
			return False

		return subjects_match and senders_match and reply_match and deliver_match and postmaster_match and other_match
			
	
	def __eq__(self, other):
		""" Implements the == operator.

		    Two subscriptions are equivalent if they match
		    the same messages and are delivered to the same place. """
		
		try:
			return self.subject == other.subject \
			   and self.sender == other.sender \
			   and self.in_reply_to == other.in_reply_to \
			   and self.delivery_address == other.delivery_address \
			   and self.postmaster_ok == other.postmaster_ok \
			   and self.other_attributes == other.other_attributes

		except AttributeError:		# if other doesn't have one of these properties, it can't be equal!
			return False
			
	def __hash__(self):
		""" Returns a hash for this object.
	
		    Needed so that Subscriptions can be used as
		    dictionary keys. """
		
		return hash( self._id )
			
	def __repr__(self):
		""" Creates a string representation of this subscription.
		
		    Format is '(subject, sender, in_reply_to, action, delivery_address, postmaster_ok)'
		    (where 'delivery_address' will just be the class name of the 
		     MessageTerminus object if action is DELIVER). """
		
		if self.action == Subscription.FORWARD:
			delivery = "FORWARD"
		elif self.action == Subscription.DELIVER:
			delivery = "DELIVER"
		else:
			delivery = "NO DELIVERY"
		
		address = str(self.delivery_address) if self.action == Subscription.FORWARD else str(self.delivery_address.__class__)
		
		return "(%s, %s, %s, %s, %s, %s, %s)" % (self.subject, self.sender, self.in_reply_to, delivery, address, str(self.postmaster_ok), self.other_attributes)
	
	def MessageMatch(self, message, for_delivery=True):
		""" Does the given message match this subscription?
		
		    The optional parameter for_delivery is used to differentiate
		    between message matching operations that are performed for
		    the purpose of delivery (used in the PostOffice) and other
		    uses of subscriptions (e.g., handlers).  A message will only
		    be allowed to match once for_delivery, but it can match
		    an infinite number of times otherwise. """
		    
		logger().log(Configuration.PO_EXTRA_VERBOSE, "Entering MessageMatch() for subscription: %s", self._id)
		
		if not (hasattr(message, "subject") and hasattr(message, "sender") and hasattr(message, "in_reply_to")):
			raise TypeError("MessageMatch() can only be used on Message objects!")

		if not self.Validate():
			raise ValueError("Subscription's parameters are invalid: %s" % self)

		# if this subscription has expired but not yet been removed,
		# it still shouldn't be matching!
		if self.expiry > 0 and self.times_matched > self.expiry:
			logger().log(Configuration.PO_EXTRA_VERBOSE, "Exiting MessageMatch() for subscription: %s", self._id)
			return False
			
		# we also need to enforce the "maximum number of forwards" policies here.
		if self.action == Subscription.FORWARD:
			if hasattr(self, "max_forward_hops") and self.max_forward_hops >= 0 and len(message.return_path) > self.max_forward_hops:
				logger().log(Configuration.PO_EXTRA_VERBOSE, "Exiting MessageMatch() for subscription: %s", self._id)
				return False
			elif hasattr(message, "max_forward_hops") and message.max_forward_hops >=0 and len(message.return_path) > message.max_forward_hops:
				logger().log(Configuration.PO_EXTRA_VERBOSE, "Exiting MessageMatch() for subscription: %s", self._id)
				return False
				
		# and it also shouldn't allow the same message
		# to be delivered to the same location twice...
		if for_delivery and message.id in self.messages_delivered:
			logger().log(Configuration.PO_EXTRA_VERBOSE, "Not matching message %s to subscription %s again...", message.id, self)
			logger().log(Configuration.PO_EXTRA_VERBOSE, "Exiting MessageMatch() for subscription: %s", self._id)
			return False
			
		# finally, if this message is designated for direct delivery,
		# on the node that's sending the message,
		# only subscriptions that require a message ID match are
		# allowed to match it.
		if message._direct_delivery and len(message.return_path) == 0 and not "id" in self.other_attributes:
			logger().log(Configuration.PO_EXTRA_VERBOSE, "Not matching message %s with subscription %s because it's marked 'for direct delivery'...", message.id, self)
			logger().log(Configuration.PO_EXTRA_VERBOSE, "Exiting MessageMatch() for subscription: %s", self._id)
			return False
		
		subject_match = (self.subject == "*" and (self.postmaster_ok or message.subject != "postmaster")) or self.subject == message.subject
		sender_match = self.sender = "*" or self.sender == message.sender
		reply_match = self.in_reply_to == "*" or self.in_reply_to == message.in_reply_to

		other_match = True
		for criterion in self.other_attributes:
			if not hasattr(message, criterion) or message.__dict__[criterion] != self.other_attributes[criterion]:
				other_match = False
				break
		
		matched = subject_match and sender_match and reply_match and other_match
		
		# we definitely need to avoid forwarding loops.
		# the policy is thus: don't forward a message to a node
		# it's already been to.  we have to do this here (not
		# in the delivery thread) because subscriptions that have
		# an expiry would otherwise still "match" and could get
		# removed before the delivery thread could do anything
		# about it.

		logger().log(Configuration.PO_EXTRA_VERBOSE, "Exiting MessageMatch() for subscription: %s", self._id)

		if matched:
			if self.action == Subscription.FORWARD and self.delivery_address in message.return_path:
				logger().warning( "message %s will not be matched to subscription %s to avoid forwarding loop...", message.id, self )
				return False
			self.times_matched += 1
		
		return matched
		
	def Validate(self):
		""" Checks that the internal state of the subscription makes sense.
		
		    This is supposed to help prevent accidental reassignments of
		    subscription parameters from sneaking by (and thus causing
		    strange, inexplicable errors). """

		# this can't be done in the module header with the others
		# because there's a circular import.
		# deferring this one is the only solution I've found
		# that doesn't involve restructuring.
		from mnvruncontrol.backend.PostOffice.Routing import MessageTerminus 
		
		action_ok = self.action in (None, Subscription.FORWARD, Subscription.DELIVER)
		if not action_ok:
			logger().warning("Subscription %s has invalid 'action' parameter... (value: %d)", self, self.action)
		
		addr_ok = (self.action is None and self.delivery_address is None) \
		          or ( self.action == Subscription.DELIVER and isinstance(self.delivery_address, MessageTerminus) ) \
		          or ( self.action == Subscription.FORWARD and isinstance(self.delivery_address, IPv4Address) )
		if not addr_ok:
			logger().warning("Subscription %s has invalid 'delivery_address' parameter (value: %s)...", self, self.delivery_address)
			
		return action_ok and addr_ok

