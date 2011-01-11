"""
  PostOffice.py:
   A relatively versatile message delivery system.
   
   It is VERY important to note that this system is a BROADCAST
   system.  That is, messages are deposited at the Post Office
   and whoever wants to look at them can.  Potential recipients
   indicate their intent by booking "subscriptions," which the
   Post Office checks every time a message arrives.  A copy of
   the message is delivered to EVERY recipient with a matching
   subscription.
   
   This has fundamental consequences for the behavior of a network of
   Post Offices joined together in series.  When you send a
   message, you have no idea how many potential recipients
   you might have or where your message might finally end up:
   there might be a subscription forwarding your message to another
   node, and you have no way of knowing how many subscriptions
   matching your message exist there (and especially how many
   further nodes those subscriptions might be forwarding to!).
   
   So it's best to think of the DELIVERY portion of this system like
   a newspaper or magazine distribution service, where articles are
   "published" and whoever subscribes can read them and send them
   along to anybody else -- rather than like postal or e-mail,
   where recipients (and their physical/electronic "locations") are
   individually specified.  If you get the wrong mindset, you'll
   probably wind up frustrated that it isn't working the way you expect :)
   
   A technical comment on security is also in order.  The network
   implementation of the PostOffice system relies on the Python 'pickle'
   module to serialize and de-serialize messages so they can be sent
   over a TCP stream.  This is fantastic, because Pickle is incredibly
   flexible; but it means the PostOffice inherits one major weakness.
   From the Python manual on the pickle module:
   
   "Warning: the pickle module is not intended to be secure against
   erroneous or maliciously constructed data. Never unpickle data
   received from an untrusted or unauthenticated source."
   
   In other words, you must be ABSOLUTELY sure that you can trust
   a Message _before_ you try to read it. (!)  The PostOffice
   offers one built-in way to do this: it supports using SSL certificates
   to verify both sends and receipts of messages.  You can also
   come up with access-control-based solutions (use a firewall,
   possibly in conjunction with port forwarding via SSH, for
   example) that will work equally well.  Just be sure that you
   know for a fact EVERY SINGLE potential source that can send
   a Message to a PostOffice unless you are prepared to assume 
   responsibility for all the potential problems, including (but
   not limited to) the total takeover of your computer by a remote
   user.  Consider yourself warned.
   
   One final (unrelated) note: the system is set up to use the
   Python 'logging' module to produce logs of its activity.
   If you want to take advantage of this, all activity is
   logged to the "PostOffice" logger; you will need to configure
   the root logger and add a handler for the PostOffice logger
   (see the 'logging' module's documentation).  If you don't want
   the PostOffice components to use logging, set this module's global
   variable "use_logging" to False.
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    June-October 2010
                    
   Address all complaints to the management.
"""

import ssl
import uuid
import time
import copy
import Queue
import errno
import socket
import select
import pprint
import logging
import cPickle
import warnings
import threading

# mute the UnicodeWarning that sometimes comes up
# when a non-PostOffice client tries to send us
# whatever they want over a socket.  (port scanners,
# spambots, etc.)  those messages don't match our
# message template, so they're thrown out anyway.
warnings.filterwarnings(action="ignore", category=UnicodeWarning)

class Null(object):
	""" An object that does nothing at all.  Used here to 
	    stand in for a 'logger' instance in the event
	    that the user doesn't want to use logging. """
	def __init__(self, *args, **kwargs): pass
	def __call__(self, *args, **kwargs): return self
	def __getattr__(self, name):         return self
	def __setattr__(self, name, value):  pass
	def __delattr__(self, name):         pass

# first: a global variable.  set this to True if you want logging;
# set it to False if you don't.
use_logging = True
__logger = logging.getLogger("PostOffice")
__null = Null()

# function that returns a logger object (or a placeholder that can be used like one).
def logger():
	global __logger, __null
	return __logger if use_logging else __null
	
# we use a 'magic' set of bytes at the beginning of
# every PostOffice message sent over the socket
# to indicate that they're really from a PostOffice.
# (obviously this can be spoofed, but it will prevent
# accidental reconstruction of a socket communication
# that was sent by some other service -- e.g., a port scanner.)
MESSAGE_MAGIC = u"%POSTOFFICE%"
CHECKSUM_BYTES = 8

# other configurables
SOCKET_TIMEOUT   = 1.5  # how long a socket is given to connect, in seconds
SUBSCRIPTION_TTL = 60   # time a subscription can have delivery failures before it's deleted, in seconds

class IPv4Address:
	""" An IPv4 address wrapper that does intelligent things
	    like translate DNS-resolvable names to IP addresses. """
	def __init__(self, host, port):
		self.set_host(host)
		self.set_port(port)
		
	def __eq__(self, other):
		if hasattr(other, "__iter__"):
			try:
				other = IPv4Address.from_iter(other)
			except (TypeError, ValueError):
				return False

		if not hasattr(other, "host") or not hasattr(other, "port"):
			return False

		return other.host == self.host and other.port == self.port
		
	def __repr__(self):
		return "('%s', %d)" % (self.host, self.port)
		
	def set_host(self, host):
		# None is allowed for not-yet-fully-configured addresses
		if host is None:
			self.host = None
			return
			
		if not isinstance(host, basestring):
			raise TypeError("Host must be str or unicode, not %s", type(host))
		
		try:
		 	self.host = socket.gethostbyname(host)
		except socket.gaierror:
			self.host = host
	
	def set_port(self, port):
		# None is allowed for not-yet-fully-configured addresses
		if port is None:
			self.port = None
			return
			
		if not isinstance(port, int):
			raise TypeError("Port must be int, not %s", type(port))

		self.port = port		
	
	def to_tuple(self):
		""" Returns a list of the form ('host', port). """
		
		return (self.host, self.port)
	
	@staticmethod
	def from_iter(lst):
		""" Get an IPv4Address from an iterable."""
		
		if isinstance(lst, basestring):
			raise TypeError("lst must not be a string!")
		
		if not hasattr(lst, "__iter__"):
			raise TypeError("lst must be an iterable type!")
		
		if len(lst) != 2:
			raise ValueError("lst must be of the form ['host', port]")
		
		return IPv4Address(lst[0], lst[1])

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

	def __init__(self, subject="*", sender="*", in_reply_to="*", action=None, delivery_address=None, postmaster_ok=False, expiry=-1, max_forward_hops=-1, other_attributes={}):
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
	
	def _MessageMatch(self, message, for_delivery=True):
		""" Does the given message match this subscription?
		
		    The optional parameter for_delivery is used to differentiate
		    between message matching operations that are performed for
		    the purpose of delivery (used in the PostOffice) and other
		    uses of subscriptions (e.g., handlers).  A message will only
		    be allowed to match once for_delivery, but it can match
		    an infinite number of times otherwise. """
		
		if not (hasattr(message, "subject") and hasattr(message, "sender") and hasattr(message, "in_reply_to")):
			raise TypeError("_MessageMatch() can only be used on Message objects!")

		if not self.Validate():
			raise ValueError("Subscription's parameters are invalid: %s", self)

		# if this subscription has expired but not yet been removed,
		# it still shouldn't be matching!
		if self.expiry > 0 and self.times_matched > self.expiry:
			return False
			
		# we also need to enforce the "maximum number of forwards" policies here.
		if self.action == Subscription.FORWARD:
			if hasattr(self, "max_forward_hops") and self.max_forward_hops >= 0 and len(message.return_path) > self.max_forward_hops:
				return False
			elif hasattr(message, "max_forward_hops") and message.max_forward_hops >=0 and len(message.return_path) > message.max_forward_hops:
				return False
				
		# and it also shouldn't allow the same message
		# to be delivered to the same location twice...
		if for_delivery and message.id in self.messages_delivered:
			logger().log(5, "Not matching message %s to subscription %s again...", message.id, self)
			return False
			
		# finally, if this message is designated for direct delivery,
		# on the node that's sending the message,
		# only subscriptions that require a message ID match are
		# allowed to match it.
		if message._direct_delivery and len(message.return_path) == 0 and not "id" in self.other_attributes:
			logger().log(5, "Not matching message %s with subscription %s because it's marked 'for direct delivery'...", message.id, self)
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
		
		action_ok = self.action in (None, Subscription.FORWARD, Subscription.DELIVER)
		if not action_ok:
			logger().warning("Subscription %s has invalid 'action' parameter... (value: %d)", self, self.action)
		
		addr_ok = (self.action is None and self.delivery_address is None) \
		          or ( self.action == Subscription.DELIVER and isinstance(self.delivery_address, MessageTerminus) ) \
		          or ( self.action == Subscription.FORWARD and isinstance(self.delivery_address, IPv4Address) )
		if not addr_ok:
			logger().warning("Subscription %s has invalid 'delivery_address' parameter (value: %s)...", self, self.delivery_address)
			
		return action_ok and addr_ok
		

class MessageTerminus:
	""" MessageTerminus objects can have messages delivered to them.
	
	    A MessageTerminus maintains its own thread so that it can
	    receive and handle messages asynchronously (i.e., so that
	    the whole program won't block while it gets a message and
	    deals with it).	
	    
	    N.b.: be ABSOLUTELY sure that any methods used as message
	    handlers are thread-safe or you will experience strange
	    problems.  Also be aware that if they go off and start
	    any long-running tasks, any subsequent messages will be
	    delivered but left unhandled until the long-running task
	    finishes (a MessageTerminus can only handle one message
	    at a time).  If you need to start long-running tasks but
	    handle messages in the meantime, create another thread
	    to do the tasks. """
	
	def __init__(self, obj_id=None):
		
		# objects CAN specify their own IDs, though they usually won't.
		if obj_id is None:
			obj_id = uuid.uuid4()
		self.id = obj_id
		logger().debug("Created MessageTerminus with id %s" % self.id)
		
		self.mailbox = Queue.Queue()
		self.handlers = {}
		self.handler_lock = threading.Lock()
		
		self.time_to_quit = False
		
		self.delivery_thread = threading.Thread(target=self._MailboxMonitor)
		self.delivery_thread.daemon = True
		self.delivery_thread.start()
	
	def __hash__(self):
		""" Creates a hash for the object.
		
		    Leaves open the possibility for duplicates, though
		    (since objects can specify their own IDs)... """
		
		return hash(self.id)
		
	def Close(self):
		""" Shut down the thread belonging to this object. 
		
		    Note that if you do this, you will never be
		    able to reuse this instance (its thread has
		    been used).  Create a new MessageTerminus
		    in that case.  """
		
		self.time_to_quit = True
		
		if hasattr(self, "delivery_thread") and self.delivery_thread and self.delivery_thread.is_alive():
			self.delivery_thread.join()
	
		self.delivery_thread = None

	def _MailboxMonitor(self):
		""" Watches the mailbox and calls the appropriate handling
		    method when a message is received. 
		    
		    Runs until the object is destroyed (?) or Python is exited. """
		
		while not self.time_to_quit:
			time.sleep(0.001)	# avoid busy-waiting
			try:
				message = self.mailbox.get_nowait()
			except Queue.Empty:
				continue
			
			logger().debug("MessageTerminus %s handling message %s.", self.id, message.id)
			
			# it's up to you to be smart and make sure
			# you don't define overlapping subscriptions,
			# otherwise this might deliver the same message
			# to the same object multiple times...
			handlers = {}
			with self.handler_lock:
				logger().log(5, "MessageTerminus acquired handler lock.")
				matched = False
				for subscription in self.handlers:
					if subscription._MessageMatch(message, for_delivery=False):
						logger().log(5, " ....message %s is about to be handled using subscription: %s", message.id, subscription)
						self.handlers[subscription](message)
						logger().log(5, " ... message %s was handled successfully.", message.id)
						matched = True
				
					# need to make sure we remove expired subscriptions.
					if subscription.expiry < 0 or subscription.times_matched < subscription.expiry:
						handlers[subscription] = self.handlers[subscription]
					else:
						logger().log(debug, "MessageTerminus %s dropped subscription handler (expired): %s", self.id, subscription)
				
				logger().log(5, "MessageTerminus matched message %s to a subscription: %s", message.id, matched)
			
				self.handlers = handlers
					
	def AddHandler(self, subscription, handler):
		""" Add a handler for messages.
		
		    PLEASE use this method instead of directly
		    appending to the handler list.  This
		    method uses a lock to protect the list
		    and make access thread-safe. """
		    
		with self.handler_lock:
			if subscription in self.handlers:
				raise SubscriptionError("Not adding duplicate message handler: %s" % str(subscription))

			self.handlers[subscription] = handler
	
	def DropHandler(self, subscr_to_delete):
		""" Remove a subscription.
		
		    Note: this will remove ANY handlers whose subscriptions
		    are SUBSETS of this one, as well.  If you want
		    to leave the more general ones, make sure the
		    subscription you pass as an argument to this
		    method is specific! """

		# notice the lock.  this is very important
		# because otherwise this method is NOT thread-safe!
		with self.handler_lock:
			for subscription in self.handlers:
				if subscription in subscr_to_delete:
					del self.handlers[subscription]

	def _TakeDelivery(self, message):
		""" Receives a message from the Post Office.
		
		    This method is called by the Post Office
		    when a message is supposed to be delivered here.
		    It simply puts the message onto the queue and
		    returns (to avoid blocking up the P.O. thread).
		    The MailboxMonitor thread takes it from there. """
		
		logger().log(5, "MessageTerminus %s received message:\n%s", self.id, message)
		
		self.mailbox.put_nowait(message)
		
class PostOffice(MessageTerminus):
	""" The class that stitches together all the pieces.
	
	    You should create one of these for every node
	    that lives an independent existence.  Multiple
	    nodes on the same machine are ok so long as
	    you manually specify them to listen on
	    different ports (pass the 'listen_port' parameter
	    to the constructor). """
	
	def __init__(self, listen_port=None, listen_socket=None, tls_cert=None, tls_key=None, tls_cafile=None, use_logging=False):
		""" Constructor.
		
		    You must pass either listen_port (in which case this object
		    will create its own socket) or listen_socket (which must be
		    an initialized but unbound TCP socket).
		    
		    If you want socket security--and you are not specifying your
		    own socket with it already configured--you must pass at
		    least tls_cert (the location to the server certificate you
		    want to use) and tls_key if the private key is not stored
		    in the cert. file.  In either case you must also specify
		    tls_cafile (the path to a file containing the Certificate
		    Authority certificates you want to trust) -- see the 'ssl'
		    module documentation.
		    
		    If you specify any of the TLS parameters, the PostOffice
		    will assume you also want to verify clients by demanding
		    a certificate from them.  Be sure that all your nodes
		    agree on this, or you will not be able to connect them
		    to one another.
		    
		    A PostOffice object can also log its activity using the
		    'logging' module, though it won't by default.  If you
		    want to use it, you should make sure to set up the root
		    logger before running the PostOffice object,
		    or you'll get a huge amount of information dumped to
		    STDERR.  You will need to pass use_logging=True to
		    enable the logger.  """
		    
		MessageTerminus.__init__(self)
		
		self.listen_port = listen_port
		self.listen_socket = listen_socket
		self.tls_cert = tls_cert
		self.tls_key = tls_key
		self.tls_cafile = tls_cafile
		    
		self.id = uuid.uuid4()
		
		logger().debug("Created PostOffice with id %s", self.id)

		# now the message holders
		self.message_queue        = Queue.Queue()
		self.pending_messages     = {}
		self.unconfirmed_messages = {}
		self.unanswered_messages  = {}
		self.message_backlog      = {}
		self.pending_message_lock = threading.Lock()

		# subscriptions come with one for "postmaster" messages
		# already included (delivers to this object!).  it has
		# a special attribute so that we can differentiate it
		# from others added later
		postmaster_subscription = Subscription(subject="postmaster", action=Subscription.DELIVER, delivery_address=self, postmaster_ok=True)
		postmaster_subscription._postmaster_subscription = True
		
		self.subscriptions     = [postmaster_subscription,]
		self.subscription_lock = threading.Lock()
		
		# and we need a handler for those messages...
		# (remember handlers were introduced in the MessageTerminus superclass)
		self.AddHandler(postmaster_subscription, self._PostMasterMessages)
		
		# a dictionary of locks preventing us from trying
		# to simultaneously deliver two messages to the same recipient
		self.delivery_locks = { postmaster_subscription: threading.Lock() }
		
		# "response_requested" messages shouldn't be delivered
		# until the routes have been established.
		self.messages_awaiting_release = {}
		self.messages_awaiting_release_lock = threading.Lock()
		
		# and finally, the worker threads.
		self.scheduler_thread = threading.Thread(target=self._Schedule)
		self.scheduler_thread.daemon = True
		
		# notice we're using a thread *pool* for the delivery threads.
		# that way we can deliver multiple messages at once, even
		# if some recipient's post office is being really slow.
		# this is a self-growing pool; more threads are added as needed.
		# we start with a few so that we don't always pay the
		# thread creation overhead.  the flag is so that threads
		# know that delivery is in progress (they won't start delivery
		# on a message they just got until this thread is done with
		# delivery for that message)
		self.delivery_threads = [DeliveryThread(self) for i in range(3)]
		self.delivering = False
		
		self.time_to_quit = False
		
		# if full configuration for the listener was provided, start it.
		if (self.listen_port is None and self.listen_socket is not None) or (self.listen_port is not None and self.listen_socket is None):
			self.StartListening()
	
	def StartListening(self):
		""" Start up the various listener services.
		
		    You should only ever call this externally if
		    you didn't provide either a listen_port or
		    a listen_socket (because you want to delay
		    listening). """
		
		if (self.listen_port is None and self.listen_socket is None) or (self.listen_port is not None and self.listen_socket is not None):
			raise AttributeError("You must specify one or the other of 'listen_port' and 'listen_socket', but not both.")

		if self.listen_socket is not None:
			self.listen_port = self.listen_socket.getsockname()[1]
			logger().info("Using provided socket.  Listening at port %d.", self.listen_port)
		else:
			try:
				# create an IPv4 TCP socket.
				listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

				# allowed to be rebound before a TIME_WAIT, LAST_ACK, or FIN_WAIT state expires
				listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				listen_socket.setblocking(0)			

				# accept any incoming connections to the port regardless of origin
				listen_socket.bind( ("", self.listen_port) )

				# allow it to keep a few backlogged connections
				# so we can catch up if we're moving slowly
				listen_socket.listen(5)				

				if self.tls_cert is not None:
					self.listen_socket = ssl.wrap_socket(listen_socket, server_side=True, certfile=self.tls_cert, keyfile=self.tls_key, ca_certs=self.tls_cafile, ssl_version=ssl.TLSv1, cert_reqs=ssl.CERT_REQUIRED)
				else:
					self.listen_socket = listen_socket
			except socket.error:
				logger().exception("Error while trying to configure & bind listening socket:")
				logger().fatal("Can't get a socket.")
				raise
		
		self.scheduler_thread.start()
		
		
	def _Schedule(self):
		""" The method that handles incoming messages over the socket
		    and assigns outgoing messages to delivery threads. 
		    
		    It should be run in its own thread to ensure it doesn't
		    block things up while it waits for messages (this is
		    arranged by default by the constructor). """
		
		logger().debug("Entering scheduling loop.")
		while not self.time_to_quit:
			# dispatching current messages is first.
			# the socket connection will wait.
			
			# first, assemble a list of messages to be processed in this pass.
			# this includes the first message in each subscription's backlog
			# (if any) as well as the first message in the queue (if any).
			messages = []

			for subscription in self.message_backlog:
				if len(self.message_backlog[subscription]) > 0:
					messages += [self.message_backlog[subscription][0],]

			msg_from_queue = False
			try:
				messages += [self.message_queue.get_nowait(),]
				msg_from_queue = True
			except Queue.Empty:
				pass
			
#			logger().debug("Handling messages.  Message count: %d", len(messages))
			# now handle them.
			for message in messages:
				# "reponse_requested" messages need to wait
				# until they've been cleared for delivery.
				# put the message back and skip to the next message.
				if message.subject != "postmaster" and message.in_reply_to in self.messages_awaiting_release:
					logger().log(5, "Message %s is in-reply-to a message that hasn't been released yet (%s).  Putting back into the queue to retry...", message.id, message.in_reply_to)
					self.message_queue.put_nowait(message)
					continue 

				logger().debug("Scheduling message %s...", message.id)
			
				# messages that want delivery confirmations 
				with self.pending_message_lock:
					if hasattr(message, "status_reports") and message.status_reports == True and message.id not in self.pending_messages:
						return_address = message.return_path[-1] if len(message.return_path) > 0 else None
						self.pending_messages[message.id] = {"return_address": return_address, "recipient_status": [], "time_started": time.time()}
				
						# messages that are requesting a response
						# are supposed to also use delivery confirmation
						# (that way we know how many responses to expect).
						# thus this 'if' is nested below the delivery confirmation one.
						if hasattr(message, "response_requested") and message.response_requested == True:
							self.pending_messages[message.id]["response_requested"] = True
						
							with self.messages_awaiting_release_lock:
								if message.id not in self.messages_awaiting_release:
									self.messages_awaiting_release[message.id] = time.time()
						else:
							self.pending_messages[message.id]["response_requested"] = False
				

				matched = False
				try:
					before = time.time()
					self.subscription_lock.acquire()
					if time.time() - before > 0.1:
						logger().warning("Subscription lock acquisition took too long in _Schedule()!")
					
					self.delivering = True
					
					logger().log(5, "Acquired subscription lock.")
#						logger().log(5, "Subscriptions to check: \n%s", pprint.pformat(self.subscriptions))

					# normally this would be two of the same "for" loop
					# to prevent race conditions between the adding of items
					# to the pending_messages list and the sending of messages,
					# but the message delivery threads all wait until self.delivering
					# is False before continuing anyway.
					subscriptions = []				
					for subscription in self.subscriptions:
						# remove any subscriptions that are undeliverable
						if hasattr(subscription, "failed_deliveries") \
						   and subscription.failed_deliveries >= 3 \
						   and time.time() - subscription.first_failure_time > SUBSCRIPTION_TTL:
							logger().info("Subscription %s has exceeded the maximum number of delivery failures and will be dropped.", subscription)
							if subscription in self.message_backlog:
								del self.message_backlog[subscription]
							continue
							
						if subscription._MessageMatch(message):
							logger().debug("Message %s matched subscription: %s", message.id, subscription)
							matched = True
							
							# make sure this location is in the list of deliveries	 
							if message.id in self.pending_messages:
								if hasattr(subscription.delivery_address, "_TakeDelivery"):	 
									address = None	 
								else:	 
									address = subscription.delivery_address

								need_update = True
								for status in self.pending_messages[message.id]["recipient_status"]:
									if address == status[0]:
										need_update = False
										break
								if need_update:
									logger().log(5, "Message %s trying to get pending message lock...", message.id)
									with self.pending_message_lock:	 
										logger().log(5, "Message %s acquired pending message lock.", message.id)

										self.pending_messages[message.id]["recipient_status"].append( [address, None] )
										logger().debug("Added address %s to message %s recipient-waiting list.", address, message.id)
							
							# if the subscription is locked, or there is a queue
							# of messages waiting to be sent using this subscription,
							# this message needs to wait.
							# notice that we test for the presence of the lock by trying
							# to acquire it!
							logger().log(5, "Trying to acquire lock for subscription id %s (scheduling): %s", subscription._id, subscription)
							acquired_lock = self.delivery_locks[subscription].acquire(False)		# non-blocking acquire()
							subscription_backlog = subscription in self.message_backlog
							message_in_backlog = None if not subscription_backlog else (message in self.message_backlog[subscription])
							message_index = None if not message_in_backlog else self.message_backlog[subscription].index(message)
							
							if not acquired_lock:
								logger().log(5, "Failed to acquire lock id %s (scheduling).", subscription._id)
							else:
								logger().log(5, "Successfully acquired lock id %s (scheduling).", subscription._id)
							
							logger().log(5, "Backlog status: got lock = %s, this subscription has backlog = %s, this message in backlog = %s, message index in backlog = %s", acquired_lock, subscription_backlog, message_in_backlog, message_index)
							
							if not acquired_lock \
							   or ( subscription_backlog and ( (not message_in_backlog) or message_index > 0 ) ) :
							              
								if acquired_lock and subscription_backlog:
									position = len(self.message_backlog[subscription]) if not message_in_backlog \
									           else message_index
									logger().log(5, " ... but subscription %s has %d other messages in line for delivery first.  Putting message %s into backlog.", subscription, position, message.id)
								elif not acquired_lock:
									logger().log(5, " ... but subscription %s is currently locked.  Putting message %s into backlog.", subscription, message.id)
								
								if not subscription_backlog:
									self.message_backlog[subscription] = []
								
								# make sure that this message is delivered in the order it was received!
								if not message_in_backlog:
									logger().log(5, "Backlog before: %s", self.message_backlog[subscription])
									self.message_backlog[subscription].append(message)
									logger().log(5, "Backlog after: %s", self.message_backlog[subscription])
								
								# if we DID get the lock, but the message can't be delivered,
								# we need to release it again!
								if acquired_lock:
									self.delivery_locks[subscription].release()

								# this match shouldn't count!
								subscription.times_matched -= 1
								subscriptions.append(subscription)		# put it back in!
								continue
						
							# if we've gotten this far, we managed to acquire the lock.
							# we need to the let the subscription thread deliver...
							# so release it.
							logger().log(5, "Releasing lock for subscription id %s (scheduling): %s", subscription._id, subscription)
							self.delivery_locks[subscription].release()
						
							# we have passed the check above, so we know that:
							#  (1) the subscription is not locked
							#  (2) there is no backlog OR this message is next in line.
							# if the message is listed in the backlog, we pull it out
							# so that we don't process the same message forever.
							if subscription_backlog:
								if message_in_backlog:
									# it SHOULD be first.  if it's not, something is wrong.
									assert self.message_backlog[subscription].index(message) == 0
									self.message_backlog[subscription].pop(0)
									
								if len(self.message_backlog[subscription]) == 0:
									del self.message_backlog[subscription]

						
							# find an idle thread and give it this message.
							# add a new thread if needed.
							# notice that we replace the message's return path
							# with an explicit COPY.  otherwise, it would be
							# a reference to the original, and if there were
							# multiple deliveries to be made, they wouldn't
							# be able to maintain independent delivery histories.

							logger().log(5, "Copying message...")
							newmsg = copy.copy(message)		# shallow copy of most things
							newmsg.return_path = copy.deepcopy(message.return_path)	# but deep copy the return path
							delivery = (newmsg, subscription)
							logger().log(5, "Finding a delivery thread...")
							dispatched = False
							for thread in self.delivery_threads:
								if not thread.busy:
									logger().log(5, " ... found one.  Now trying to transfer message & delivery info...")
									thread.deliveries.put_nowait(delivery)
									dispatched = True
									logger().log(5, " ... success.")
									break
							if not dispatched:
								thread = DeliveryThread(self)
								thread.deliveries.put_nowait(delivery)
								self.delivery_threads.append(thread)
								logger().debug("Created new thread for message delivery.")
						else:
							logger().log(5, "Message %s did not match subscription: %s", message.id, subscription)

						# need to make sure we remove expired subscriptions.
						if subscription.expiry < 0 or subscription.times_matched < subscription.expiry:
							subscriptions.append(subscription)
						else:
							logger().debug("Removed expired subscription: %s", subscription)
				
					self.subscriptions = subscriptions
					logger().log(5, "Subscriptions left: %s", self.subscriptions)
				finally:
					self.delivering = False
					self.subscription_lock.release()
					logger().log(5, "Released subscription lock.")
				
				if not matched:
					# if there were no matches and the message requests
					# delivery confirmation, send back a reply right away
					if message.id in self.pending_messages:
						delivery_msg = Message(subject="postmaster", delivered_to=[], in_reply_to=message.id)
						self.Send(delivery_msg)

					logger().debug("Message %s matched no subscriptions.  Discarding." % message.id)
					
					# if it's from the backlog, it's still there.
					# (messages from the queue were removed in the get_nowait().)
					# we need to remove it!
					for subscription in self.message_backlog:
						if message in self.message_backlog[subscription]:
							self.message_backlog[subscription].remove(message)
							break
			

			### END   for message in messages ###

#			logger().debug("Done handling messages.")

			# avoid busy-waiting.
			# backlogs aren't generally cleared this fast,
			# so we should only go right back around if 
			# we are getting NEW messages out of the queue.
			if not msg_from_queue:
				time.sleep(0.001)
				
			# check for moldy old messages in pending_messages and messages_awaiting_release
			# that have been around for too long.  they probably won't ever get responses,
			# so just get rid of them.  (we hold them for an hour before expunging.)
#			logger().debug("Pending messages check.")
			if len(self.pending_messages) > 0:
				with self.pending_message_lock:
					new_pending_messages = {}
					for pending_message_id in self.pending_messages:
						if time.time() - self.pending_messages[pending_message_id]["time_started"] < 3600:
							new_pending_messages[pending_message_id] = self.pending_messages[pending_message_id]
					self.pending_messages = new_pending_messages
			
			if len(self.messages_awaiting_release) > 0:
				with self.messages_awaiting_release_lock:
					new_msgs = {}
					for msg_id in self.messages_awaiting_release:
						if time.time() - self.messages_awaiting_release[msg_id] < 3600:
							new_msgs[msg_id] = self.messages_awaiting_release[msg_id]
					self.messages_awaiting_release = new_msgs
			
#			logger().debug("Checking socket.")
			try:
				# this will return the socket when it's got a client ready
#				logger().debug("trying SELECT")
				if select.select([self.listen_socket], [], [], 0)[0]:		
					certificate = None
					client_socket, client_address = self.listen_socket.accept()
				
					# we can discard the port number.  it's not important
					# since it will be a dynamic-use port (>32000) and
					# we can't contact that node there after this socket
					# has been closed.
					client_address = client_address[0]


					# if this is an SSL socket, get the other side's certificate
					if hasattr(client_socket, "getpeercert"):
						certificate = client_socket.getpeercert()					

					# unfortunately, the SSL wrapper gives the methods different names (argh...)
					if hasattr(client_socket, "read") and hasattr(client_socket, "write"):
						send = client_socket.write
						recv = client_socket.read
					else:
						send = client_socket.send
						recv = client_socket.recv

					msg = ""
					datalen = -1
					while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire msg
						data = recv(1024)
						datalen = len(data)
						msg += data
		
					if msg == "":
						logger().info("Blank message from '%s'.  Assuming pipe was broken and ignoring.", client_address)
						client_socket.close()
						continue
					elif msg == "ping":
						logger().debug("Responding to ping...")
						send("1")
						client_socket.shutdown(socket.SHUT_WR)
						continue
					elif len(msg) < len(MESSAGE_MAGIC) + CHECKSUM_BYTES:
						logger().info("Garbage message from %s (too short).  Message:\n%s", client_address, msg)
						logger().warning(" ==> Ignoring.")
						continue
					elif msg[:len(MESSAGE_MAGIC)] != MESSAGE_MAGIC:
						logger().info("Garbage message from %s (no message magic).  Message:\n%s", client_address, msg)
						logger().warning(" ==> Ignoring.")
						continue
					
					# verify that the message's checksum is really how long it is...
					# note that we use 7-bit (not 8-bit) 'bytes' because the socket protocol
					# can't handle strings with code points higher than 127...
					checksum_string = msg[len(MESSAGE_MAGIC)+1:len(MESSAGE_MAGIC)+CHECKSUM_BYTES]
					checksum = 0
					for char in checksum_string:
						checksum <<= 7
						checksum += ord(char)
					if len(msg) - len(MESSAGE_MAGIC) - CHECKSUM_BYTES != checksum:
						logger().info("Garbage message from %s (checksum [%d] doesn't match message length [%d]).  Message:\n%s", client_address, checksum, len(msg) - len(MESSAGE_MAGIC) - CHECKSUM_BYTES, msg)
						logger().warning(" ==> Suggesting client re-send.")
						send("RECV_ERR")
						client_socket.shutdown(socket.SHUT_WR)
						continue
					
					# strip off the magic bytes and checksum
					msg = msg[len(MESSAGE_MAGIC)+CHECKSUM_BYTES:]
					try:
						message =  cPickle.loads(msg)
					except cPickle.UnpicklingError:
						logger().info("Garbage message from %s containing the appropriate message magic and checksum.  Message:\n%s", client_address, msg)
			 			logger().warning("  ==> Ignoring.")
						continue
					except EOFError:
						logger().info("Broken pipe getting message.  Dropping.")
						continue
				
					if hasattr(message, "subject") and hasattr(message, "id") and hasattr(message, "return_path") and len(message.return_path) > 0:
						send("RECV_ACK %s" % message.id)
						client_socket.shutdown(socket.SHUT_WR)

						logger().info("RECEIVED:\n%s", str(message))
						logger().info(" ... from client at address '%s'", client_address)
						if certificate is not None:
							# the format of the certificate returned by getpeercert()
							# is *terrible*.  let's reformat it a bit.
							certificate_reformat = {}
							for item in certificate["subject"]:
								certificate_reformat[item[0][0]] = item[0][1]
							logger().info( " ... identifying themselves with security certificate commonName '%s'", certificate_reformat["commonName"] )
						
							message.sender_certificate = certificate_reformat

						# the delivery thread sending this message to us
						# should have appended an IPv4Address to return_path
						# containing the port number we should be contacting it at.
						# now we add the IP address as we see it from here.
						message.return_path[-1].set_host(client_address)
	#					print "message came from: %s" % message.return_path

						self.message_queue.put_nowait(message)
					else:
						logger().info("Incomplete message from client '%s':\n%s", client_address, message )
						logger().warning("  ==> Ignoring.")
				
					client_socket.close()
					
			except (socket.error, select.error), (errnum, msg):
				if errnum == errno.EINTR:		# the code for an interrupted system call
					logger().warning("Recv was interrupted by system call.  Will try again.")
					pass
				else:
					logger().exception("Error trying to receive incoming data:")
		logger().debug("Scheduler thread shut down.")	
				
	def Send(self, message):
		""" Send a message.
		
		    Puts the message into the message-send queue
		    so long as it's properly formed. """
		
		if not hasattr(message, "subject") and hasattr(message, "id"):
			raise MessageError("Message is badly formed.  Won't be sent...")
		
		logger().info("Adding message to queue:\n%s", message)
		
		self.message_queue.put_nowait(message)
		
	def SendTo(self, message, recipient_list, timeout=None, with_exception=False):
		""" This method is intended as a convenience tool
		    to address the cases where the run control
		    absolutely needs to send messages to specific
		    hosts who can't specify themselves in advance
		    (e.g., when the run control first starts up
		     it needs to advertise this fact to any clients
		     so that they can book forwarding subscriptions
		     appropriately).
		     
		    If you find yourself relying on it a lot, you're
		    probably not using the PostOffice functionality
		    properly (see the documentation on this module
		    at the top of the file)... """
		
		# mark the message as "for direct delivery only"
		message._direct_delivery = True
		
		# make one subscription for each recipient.
		# these subscriptions will only match this message,
		# and will expire after delivering it once.
		for recipient in recipient_list:
			recipient_subscr = Subscription(action=Subscription.FORWARD, delivery_address=recipient, expiry=1, other_attributes={"id": message.id})
			self.AddSubscription(recipient_subscr)

		try:
			responses = self.SendWithConfirmation(message, timeout, with_exception)
		except TimeoutError:
			responses = None
		
		# need to remove any subscriptions that didn't get erased by a delivery
		for recipient in recipient_list:
			recipient_subscr = Subscription(action=Subscription.FORWARD, delivery_address=recipient, expiry=1, other_attributes={"id": message.id})
			self.DropSubscription(recipient_subscr)
		
		if responses is None and with_exception:
			raise TimeoutError
		
		return responses
	
	def SendWithConfirmation(self, message, timeout=None, with_exception=False):
		""" Sends a message and then blocks until it gets
		    confirmation that it has been delivered (or
		    delivery failed) to all matching subscriptions,
		    unless the optional timeout is specified.
		    
		    If the message is delivered only to local objects
		    then this should return almost immediately. """

		if not hasattr(message, "subject") and hasattr(message, "id"):
			raise MessageError("Message is badly formed.  Won't be sent...")
			
		message.status_reports = True
		self.unconfirmed_messages[message.id] = {"deliveries": None, "time_started": time.time()}
		self.Send(message)
		
		#threading.enumerate()
		
		while True:
			if (timeout is not None) and (time.time() - self.unconfirmed_messages[message.id]["time_started"] > timeout):
				logger().debug("Timeout for message %s expired.", message.id)
				if with_exception:
					raise TimeoutError("Message %s send timed out...", message.id)
				else:
					break
			
			if self.unconfirmed_messages[message.id]["deliveries"] is not None:
				break
			
			time.sleep(0.001)

		if self.unconfirmed_messages[message.id]["deliveries"] is None:
			deliveries = []
		else:
			deliveries = self.unconfirmed_messages[message.id]["deliveries"]
			logger().debug("Confirmations for message %s received from all nodes.", message.id)
		
		del self.unconfirmed_messages[message.id]
		
		return deliveries
		
	
	def SendAndWaitForResponse(self, message, timeout=None, with_exception=False):
		""" Sends a message and waits for a response from the
		    remote end, with optional timeout. """
		
		if not hasattr(message, "subject") and hasattr(message, "id"):
			raise MessageError("Message is badly formed.  Won't be sent...")

		# book a subscription for all non-postmaster messages responding to this one
		response_subscr =  Subscription(in_reply_to=message.id, action=Subscription.DELIVER, delivery_address=self, postmaster_ok=False)
		self.AddSubscription(response_subscr)
		
		# also insert a handler for said message, since we want the post office itself
		# to do the handling, then pass the message back to the caller
		with self.handler_lock:
			self.handlers[response_subscr] = self._UnansweredMessages
		
		message.response_requested = True
		
		self.unanswered_messages[message.id] = {"messages": [], "time_started": time.time()}

		deliveries = self.SendWithConfirmation(message, timeout)
		response_messages = []

		logger().debug("Clearing message %s for delivery...", message.id)
		clear_msg = Message(subject="postmaster", in_reply_to=message.id, response_clear=True)
		self.Send(clear_msg)
		
		# obviously we don't want to continue to wait if the message was never delivered
		if len(deliveries) == 0:
			logger().debug("Message %s was not accepted for delivery anywhere.  Not waiting...", message.id)
		else:
			logger().debug("Waiting for %d responses from the following nodes: %s", len(deliveries), deliveries)
		
			# now, we wait.  the empty list in unanswered_messages will be
			# updated with messages when they are delivered
			# (this is done in the handling method).  we only wait for
			# replies from the nodes that actually took delivery
			# of the message (as returned by SendWithConfirmation()).
			# we can't guarantee the far end will send a message back
			# with the same id in "sender" as is in deliveries, so
			# we just wait until we get the same NUMBER of messages
			# back as there were recipients of the original message.
			while True:
				if timeout is not None and time.time() - self.unanswered_messages[message.id]["time_started"] > timeout:
					logger().debug("Timeout expired.")
					if with_exception:
						raise TimeoutError("Timed out waiting for responses...")
					else:
						break
			
				if len(self.unanswered_messages[message.id]["messages"]) >= len(deliveries):
					break
			
				time.sleep(0.01)
			response_messages = self.unanswered_messages[message.id]["messages"]

			logger().debug("All responses for message %s received.", message.id)
		
		# clean up
		self.DropSubscription(response_subscr)
		
		with self.handler_lock:
			del self.handlers[response_subscr]
		del self.unanswered_messages[message.id]
		
		logger().log(5, "Returning!")
		
		return response_messages
		
	def ForwardRequest(self, host, subscriptions):
		""" Contacts a remote node to request forwarding subscriptions. 
		
		    The forwarding subscriptions must already be assembled and 
		    ready to go (what is passed as the "subscriptions"
		    parameter is simply attached to the message and passed
		    along without inspection).  Note that this is expected
		    to be a LIST of subscriptions!  (The exception is that the
		    IP address portion of the "delivery_address" attribute
		    will be overridden on the receiving end to make sure 
		    that the message can get back where it came from.) """
		
		new_subscriptions = []
		for subscr in subscriptions:
			if not subscr.Validate():
				raise ValueError("Subscription's parameters are invalid: %s", subscr)
			new_subscriptions.append(copy.deepcopy(subscr))
		
		message = Message(subject="postmaster", remote_request="forward_request", subscriptions=new_subscriptions)

		forward_subscr = Subscription(subject="postmaster", action=Subscription.FORWARD, delivery_address=host, postmaster_ok=True, expiry=1, other_attributes={"id": message.id})
		self.AddSubscription(forward_subscr)
		
		self.Send(message)
		
	def ForwardCancel(self, host, subscriptions):
		""" Contacts a remote node to cancel forwarding subscriptions.
		
		    See the caveat for ForwardRequest().  """

		new_subscriptions = []
		for subscr in subscriptions:
			if not subscr.Validate():
				raise ValueError("Subscription's parameters are invalid: %s", self)
			new_subscriptions.append(copy.deepcopy(subscr))

		message = Message(subject="postmaster", remote_request="forward_cancel", subscriptions=new_subscriptions)

		forward_subscr = Subscription(subject="postmaster", action=Subscription.FORWARD, delivery_address=host, postmaster_ok=True, expiry=1, other_attributes={"id": message.id})
		self.AddSubscription(forward_subscr)
		
		self.Send(message)
		
		
	
	def _PostMasterMessages(self, message):
		""" The handler for messages with subject "postmaster". """

		logger().log(5, "Postmaster message: %s", message)
		
		# "delivered_to" messages are for delivery confirmation
		if hasattr(message, "delivered_to"):
			# be careful.  we need to make sure that the
			# pending_messages information doesn't change under our feet.
			# make a copy of it here (while protected by a lock).
			pending_info = None
			with self.pending_message_lock:
				if message.in_reply_to in self.pending_messages:
					pending_info = copy.deepcopy(self.pending_messages[message.in_reply_to])
		
			# if nothing's left in pending_messages, then this
			# is the final confirmation that responses have
			# been received from all nodes that had messages
			# forwarded to them.  
			# moreover, if this is the node from which the message
			# originated, we need to update the dictionary that
			# the main thread is waiting on so it knows we're done.
			if pending_info is None:
				if message.in_reply_to in self.unconfirmed_messages:
					self.unconfirmed_messages[message.in_reply_to]["deliveries"] = message.delivered_to
				
				return
			
			slots_left = 0
			matched = False
			
			for slot in pending_info["recipient_status"]:
				# locally-delivered messages never update this return path.
				if not matched and (   (len(message.return_path) == 0 and slot[0] is None and slot[1] is None) \
				                    or (len(message.return_path) > 0 and slot[0] == message.return_path[-1]) ):
					slot[1] = message.delivered_to
					matched = True
					
					logger().debug("Got confirmation for %s from %s.", message.in_reply_to, message.return_path)
					
					# if this message also wants a reply, we ensure
					# that any forwarding requests back to the previous node
					# will allow at least as many forwards as replies we're
					# expecting.
					if pending_info["response_requested"]:
						if pending_info["return_address"] is not None:
							response_subscr = Subscription(in_reply_to=message.in_reply_to, 
								                          action=Subscription.FORWARD, 
								                          delivery_address=pending_info["return_address"], 
								                          postmaster_ok=False, 
								                          expiry=len(message.delivered_to) )
							try:
								with self.subscription_lock:
									i = self.subscriptions.index(response_subscr)
									if self.subscriptions[i].expiry > 0:
										self.subscriptions[i].expiry += response_subscr.expiry
										logger().debug("Updated subscription %s to expire after %d forwards", self.subscriptions[i], self.subscriptions[i].expiry)
							# ValueError is thrown when the index() call above can't find a match
							except ValueError:
								self.AddSubscription(response_subscr)
								logger().debug("booked response subscription: %s", pprint.pformat(response_subscr))

						# set up a single-use subscription to forward the "response_clear"
						# message to the node who just told us they got a delivery confirmation.
						# that node will then release any responses it's holding
						if len(message.return_path) > 0:
							clear_subscr = Subscription( subject="postmaster", \
							                             in_reply_to=message.in_reply_to, \
								                        action=Subscription.FORWARD, \
								                        delivery_address=message.return_path[-1], \
								                        postmaster_ok=True, \
								                        expiry=1, \
								                        other_attributes={"response_clear": True} )
							self.AddSubscription(clear_subscr)
			
#					else:
#						print "didn't match: return path[-1][0] = %s; slot[0] = %s;  (bool: %s)" % (message.return_path[-1], slot[0], message.return_path[-1] == slot[0])
				
				if slot[1] is None:
					slots_left += 1
			### END for slot in pending_info["recipient_status"]

			# need to copy the updated status in.
			# otherwise the "received messages" count
			# never changes.
			with self.pending_message_lock:
				self.pending_messages[message.in_reply_to] = pending_info

#			print slots_left, self.pending_messages[message.in_reply_to]["recipient_status"]
			
			# if this was the last response we were waiting on,
			# it's go time.  we assemble the final list of end
			# recipients, then send a notification containing
			# that information to the upstream node.  if the
			# message originated here (it has no return address),
			# we don't need a special subscription (blanket
			# postmaster subscription covers it).
			#
			if slots_left == 0:
				logger().debug("Pending message status for message %s:\n%s", message.in_reply_to, pending_info)
				recipient_list = []
				for slot in pending_info["recipient_status"]:
					recipient_list.extend(slot[1])
				
				return_address = pending_info["return_address"]
				if return_address is not None:
					forward_subscr = Subscription(subject="postmaster", in_reply_to=message.in_reply_to, action=Subscription.FORWARD, delivery_address=return_address, expiry=1)
					self.AddSubscription(forward_subscr)
				
				with self.pending_message_lock:
					del self.pending_messages[message.in_reply_to]
				
				done_msg = Message(subject="postmaster", in_reply_to=message.in_reply_to, delivered_to=recipient_list)
				self.Send(done_msg)
				logger().debug("All confirmations for message %s received from upstream.  Sent single confirmation downstream...", message.in_reply_to)
			else:
				logger().debug("Message %s: still waiting for confirmation from %d nodes.", message.in_reply_to, slots_left)
				logger().debug("   recipient status list: %s", pending_info["recipient_status"])
						
			
		# "remote_request" messages, on the other hand, are
		# how remote nodes manage forwarding requests.
		elif hasattr(message, "remote_request") and len(message.return_path) > 0:
			# we first need to rewrite the subscription so that we
			# can be confident it will reach its destination: if the
			# recipient is behind a NAT firewall, for example, the
			# return address will look different on this end than
			# it did at the source.  however, we keep the port number
			# because only the listener knows what port it's listening at....
			for subscription in message.subscriptions:
				subscription.action = Subscription.FORWARD
				subscription.delivery_address = IPv4Address(message.return_path[-1].host, subscription.delivery_address.port)
				if message.remote_request == "forward_request":
					self.AddSubscription(subscription)
					logger().debug("Added forwarding subscription: %s", subscription)
				elif message.remote_request == "forward_cancel":
					self.DropSubscription(subscription)
					logger().debug("Dropped all forwarding subscriptions matching subscription: %s", subscription)
				
		# and response_clear messages are the signal that responses
		# to a particular message can be released because they will
		# be delivered back to the source ok.
		elif hasattr(message, "response_clear") and message.response_clear:
			with self.messages_awaiting_release_lock:
				if message.in_reply_to in self.messages_awaiting_release:
					del self.messages_awaiting_release[message.in_reply_to]
		
		else:
			logger().warning("Postmaster message was ignored!:\n%s", message)
	
	def _UnansweredMessages(self, message):
		""" The handler for messages in-reply-to a message that
		    is currently awaiting a reponse.
		    
		    Must be assigned as the handler for the message in
		    question (use the SendAndWaitForReponse() method
		    instead of manual assignment for best results). """

		if message.in_reply_to in self.unanswered_messages:
			self.unanswered_messages[message.in_reply_to]["messages"].append(message)
			logger().debug("Received message %s in answer to message %s", message.id, message.in_reply_to)
			
			logger().debug("Response count for message %s is now %d...", message.in_reply_to, len(self.unanswered_messages[message.in_reply_to]["messages"]))

			
	def AddSubscription(self, subscription):
		""" Add a subscription.
		
		    PLEASE use this method instead of directly
		    appending to the subscription list.  This
		    method uses a lock to protect the list
		    and make access thread-safe.   Moreover,
		    there are other things that need to 
		    happen (like the creation of a lock)
		    when a subscription joins the collection.  """
		
		logger().log(5, "Entering AddSubscription()")
		
		with self.subscription_lock:
			matched = False
			for sub in self.subscriptions:
				# don't mess around with the postmaster's subscription.
				if hasattr(sub, "_postmaster_subscription"):
					continue
			
				# subscriptions aren't allowed to overlap.
				# if there's already a more general one there,
				# you'll get a warning but no action; if the one you're
				# trying to add is more general, the old one
				# will be replaced.  (however, if there's already
				# a more general one AND both the new and the old
				# ones have expiries, the expiry of the subscription
				# to be left in the list will be incremented by the amount
				# of the new one.  this way you still get the behavior
				# you're expecting.  NOTE: if the new one has no expiry
				# and the old one does, this system won't work.  watch out!)
				#
				# notice that this structure ensures that equivalent
				# subscriptions will match the first 'if' first and
				# thus not be duplicated.
				if subscription in sub:
					logger().warning("Not adding duplicate subscription: %s", subscription)
					if subscription.expiry > 0 and sub.expiry >= 0:
						new_expiry = subscription.expiry + sub.expiry
						logger().warning("  ... but updating old subscription to expiry of %d.", new_expiry)
						sub.expiry = new_expiry
					matched = True
				elif sub in subscription:
					self.subscriptions.remove(sub)
					self.subscriptions.append(subscription)
					logger().warning("New subscription %s replaced less general one %s", subscription, sub)
					matched = True

			if not matched:
				self.subscriptions.append(subscription)
				self.delivery_locks[subscription] = threading.Lock()
				logger().debug("Booked subscription: %s", subscription)
		
		logger().log(5, "Exiting AddSubscription()")
	
	def DropSubscription(self, subscr_to_delete):
		""" Remove a subscription.
		
		    Note: this will remove ANY subscriptions that
		    are SUBSETS of this one, as well.  If you want
		    to leave the more general ones, make sure the
		    subscription you pass as an argument to this
		    method is specific! """

		# notice the lock.  this is very important
		# because otherwise this method is NOT thread-safe!
		logger().log(5, "Going to drop subscription: %s", subscr_to_delete)
		
		with self.subscription_lock:
			new_list = []
			for subscription in self.subscriptions:
				if subscription not in subscr_to_delete or hasattr(subscription, "_postmaster_subscription"):
					new_list.append(subscription)
				else:
					del self.delivery_locks[subscription]
					
					if subscription in self.message_backlog:
						del self.message_backlog[subscription]
						
					logger().debug("Dropped subscription: %s", subscription)

			self.subscriptions = new_list

		logger().log(5, "  ... done!")
		
	def Shutdown(self):
		""" Shut down the threads belonging to this object. 
		
		    Note that if you do this, you will never be
		    able to reuse this instance (its threads have
		    all been used).  Create a new PostOffice
		    in that case.  """

		# first shut down the scheduler thread
		self.time_to_quit = True
		if self.scheduler_thread.is_alive():
			logger().info("Shutting down scheduler...")
			self.scheduler_thread.join()

		if self.listen_socket:
			logger().info("Shutting down listening socket...")
			self.listen_socket.close()
		
		# now shut down the delivery threads
		self.delivering = False
		logger().info("Shutting down delivery threads...")
		for thread in self.delivery_threads:
			if not thread.is_alive():
				continue
				
			thread.deliveries.put((Message(subject="postmaster", _delivery_thread_quit=True), None))
			thread.join()

		# finally, shut down the thread inherited from the MessageTerminus
		logger().info("Shutting down the PostOffice's MessageTerminus...")
		self.Close()
		

class DeliveryThread(threading.Thread):
	""" A thread subtype for delivering messages.
	
	    Used by a PostOffice object (which keeps a pool
	    of these guys). """

	def __init__(self, postoffice):
		threading.Thread.__init__(self)
		
		self.deliveries = Queue.Queue()
		self.daemon = True
		
		self.postoffice = postoffice
		self.busy = False

		self.start()
	
	def run(self):
		while True:
			# this blocks on a message.
			# that's okay; it needs one to do anything anyway.
			message, subscription = self.deliveries.get()

			# this is how we shut down.
			if message.subject == "postmaster" and hasattr(message, "_delivery_thread_quit") and message._delivery_thread_quit == True:
				break
			
			self.busy = True

			# we'll want to keep track of whether a message
			# has already been delivered by this subscription:
			# that way we can try multiple times to deliver it
			# if delivery fails without it being delivered
			# multiple times to other destinations where delivery
			# succeeded...	
			#
			# notice, however, that we put it in the list BEFORE
			# it's actually been delivered.  this is because otherwise,
			# if the delivery here is not yet finished,
			# the scheduler could see this message again (if it's put
			# into a backlog for a different subscription) and
			# try to deliver it using this same subscription but
			# with a different delivery thread.  (that thread would
			# wait until it gets this subscription's lock, but it
			# would still wind up delivering the message again.)
			# this way, a message will not be used again for the
			# same subscription while this thread is dealing with
			# it unless this thread specifically disavows it.
			# as a consequence, though, we need to REMOVE the message
			# from the list if it can't be delivered (done at the end).
			logger().debug(" ... adding message %s to subscription 'messages_delivered' list: %s", message.id, subscription)
			# insert at front of list to make lookups quicker
			subscription.messages_delivered.insert(0, message.id)
			
			# if the message doesn't already have a return address,
			# then its return address is this post office.
			if message.return_address is None:
				message.return_address = self.postoffice.id
				
			# moreover, the next node (in the case where this
			# message is being forwarded) might need to know
			# how to contact us (i.e., in case of 'postmaster'
			# status updates).  since there's no way for the
			# other side to know which port we're listening on
			# from the *connection* details of our outbound
			# message, we need to specifically include it in
			# the return_path.  we leave the IP address part
			# of the return_path entry as None because the
			# receiving end will add our IP address as it
			# sees us (which might be different than what
			# we'd think from here) after receipt.  notice that
			# messages that are going to be delivered don't
			# update the return path (because one ALWAYS goes
			# through the local node for delivery). 
			if subscription.action != Subscription.DELIVER:
				message.return_path.append( IPv4Address(None, self.postoffice.listen_port) ) 
			
			# wait until it's safe to deliver this message
			try:
				logger().log(5, "Acquiring lock for subscription id %s (delivery): %s", subscription._id, subscription)
				self.postoffice.delivery_locks[subscription].acquire()
				logger().log(5, "Successfully acquired lock for subscription id %s (delivery)", subscription._id)
				while self.postoffice.delivering:
					time.sleep(0.001)

				start_time = time.time()
				delivered = False
				attempts = 1
				while not delivered and attempts < 4:
					logger().debug("Delivery attempt #%d for message %s to recipient %s:",
					               attempts, message.id, 
					               subscription.delivery_address if not hasattr(subscription.delivery_address, "id")
					                  else subscription.delivery_address.id)
					if subscription.action == Subscription.DELIVER:
						subscription.delivery_address._TakeDelivery(message)
				
						# we're done with this message.  log our success, then
						# (if requested) send a notification to the return address
						# that the message was delivered
						if subscription.delivery_address == self:
							logger().debug("DELIVERED to local post office: message %s.", message.id)
						else:
							logger().info( "DELIVERED to '%s': message %s", subscription.delivery_address.id, message.id )
							if hasattr(message, "status_reports") and message.status_reports == True:
								self.postoffice.Send(Message(subject="postmaster", in_reply_to=message.id, delivered_to=[subscription.delivery_address.id,]))
					
						delivered = True
							
					# 'postmaster' messages should never be forwarded...
					# ... unless the subscription specifically requests
					# that it wants 'postmaster' messages AND it either wants
					# replies for this particular message or it's a request
					# intended for a remote node
					elif subscription.action == Subscription.FORWARD:
						if (message.subject != "postmaster" or (subscription.subject == "postmaster" and ( subscription.in_reply_to == message.in_reply_to or hasattr(message, "remote_request")) ) ):
							logger().debug( "SENDING to post office at %s: message %s", subscription.delivery_address, message.id )
							try:
								s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
								s.settimeout(SOCKET_TIMEOUT)
					
								if self.postoffice.tls_cert is not None:
									sock = ssl.wrap_socket(s, certfile=tls_cert, keyfile=tls_key, ca_certs=tls_cafile, ssl_version=ssl.TLSv1, cert_reqs=ssl.CERT_REQUIRED)
								else:
									sock = s

								sock.connect( subscription.delivery_address.to_tuple() )
					
#								# unfortunately the SSL wrapper uses different method names ...
#								if hasattr(sock, "read") and hasattr(sock, "write"):
#									send = sock.write
#									recv = sock.read
#								else:
#									send = sock.send
#									recv = sock.recv
					
								# ah, the beauty of pickle.
								# we just send the entire message *object*
								# and pickle will rebuild it on the other side!
								message_text = cPickle.dumps(message)	# doesn't include the magic or checksum
								message_length = len(message_text)

								# use a checksum so that the receiving end knows that they've gotten the whole thing.
								# note that we use 7-bit (not 8-bit) 'bytes' because the socket protocol
								# can't handle characters with code points higher than 127...
								checksum_string = "".join( [chr((message_length >> shift_amt*7) & 0x7F) for shift_amt in range(7, -1, -1)] )
								
								message_string = "%s%s%s" % (MESSAGE_MAGIC, checksum_string, message_text)
								
								if message_length > 2**48:
									raise OverflowError("You really need to send a message bigger than 1 exobyte??  Sorry... No can do.")
									
								# send() might not send the whole thing.
								# it's our responsibility to make sure everything
								# is communicated.
								bytes_sent = 0
								while bytes_sent < len(message_string):
									bytes_sent += sock.send(message_string[bytes_sent:])
								sock.shutdown(socket.SHUT_WR)
								response = sock.recv(1024)
					
								if response == "RECV_ACK %s" % message.id:
									logger().info("FORWARDED to host %s: message %s", subscription.delivery_address, message.id)
									if hasattr(subscription, "failed_deliveries"):
										del subscription.failed_deliveries
										del subscription.first_failure_time
									delivered = True
								else:
									logger().warning(" ==> Message %s was not transmitted properly...", message.id)

							except socket.error:
								delivered = False
								logger().exception("Socket error:")
								logger().warning(" ==> Message %s was not transmitted to host %s.", message.id, subscription.delivery_address)
							
								# the post office will delete this subscription
								# after a sufficient number of failed deliveries
								# over a certain time period (configuration at 
								# top of file)
								if hasattr(subscription, "failed_deliveries"):
									subscription.failed_deliveries += 1
								else:
									subscription.failed_deliveries = 1
								subscription.first_failure_time = time.time()
									
							finally:
								sock.close()
							
						else:
							logger().info("NOT FORWARDING postmaster message %s.", message.id)
							break

					attempts += 1

				# if the message didn't go anywhere and we want a status report,
				# make sure that it's clear it wasn't delivered.
				if message.id in self.postoffice.pending_messages:
					nodelivery_msg = None
					with self.postoffice.pending_message_lock:
						if delivered:
							# add this location to the list of deliveries
							logger().log(5, "Acquired pending message lock...")
							if hasattr(subscription.delivery_address, "_TakeDelivery"):
								address = None
							else:
								address = subscription.delivery_address
							
							# if we are trying to send the same message to the same place,
							# we shouldn't be duplicating its status...
							delivery_status = [address, None]
							if delivery_status not in self.postoffice.pending_messages[message.id]["recipient_status"]:
								self.postoffice.pending_messages[message.id]["recipient_status"].append(delivery_status)
					
						else:					
							logger().info(" ==> Reporting delivery failed to %s...", subscription.delivery_address)
							for slot in self.postoffice.pending_messages[message.id]["recipient_status"]:
								if slot[0] == message.return_path[-1]:
									slot[1] = []
									break
			
							# we "forge" a message from this address indicating no deliveries there
							nodelivery_msg = Message(subject="postmaster", in_reply_to=message.id, delivered_to=[])
							nodelivery_msg.return_path = [ copy.deepcopy(subscription.delivery_address), ]
							
					# note: can't do this within the 'with' block above
					# because _PostMasterMessages also wants that same lock...
					# ...  ==> deadlock.
					if nodelivery_msg is not None:
						self.postoffice._PostMasterMessages(nodelivery_msg)
						logger().debug(" ==> returned from handling 'forged' message.")
				
				if delivered:
					# make sure the list size doesn't grow indefinitely
					if len(subscription.messages_delivered) > 1000:
						subscription.messages_delivered.pop()
				else:
					# if the message WASN'T able to be delivered, we MUST
					# remove it from the 'delivered' list so that it can
					# be retried if necessary.
					subscription.messages_delivered.remove(message.id)
						

			finally:
				self.postoffice.delivery_locks[subscription].release()
				logger().log(5, "Released lock for subscription id %s (delivery): %s", subscription._id, subscription)		

			self.busy = False
			
			logger().log(5, "Done handling message %s.  Time spent: %f seconds.", message.id, time.time()-start_time)


class Error(Exception):
	pass
	
class TimeoutError(Exception):
	pass
	
class MessageError(Exception):
	pass

class SubscriptionError(Exception):
	pass

class SocketError(Error):
	pass
