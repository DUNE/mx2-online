"""
   Routing.py:
    Classes that actually send or receive Messages.
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    June-October 2010
                    
   Address all complaints to the management.
"""

import copy
import cPickle
import errno
import pprint
import Queue
import select
import socket
import ssl
import threading
import time
import uuid
import warnings

from mnvruncontrol.backend.PostOffice import Configuration
from mnvruncontrol.backend.PostOffice import Envelope
from mnvruncontrol.backend.PostOffice import Errors
from mnvruncontrol.backend.PostOffice import NetworkTypes

from mnvruncontrol.backend.PostOffice.Logging import logger

# mute the UnicodeWarning that sometimes comes up
# when a non-PostOffice client tries to send us
# whatever they want over a socket.  (port scanners,
# spambots, etc.)  those messages don't match our
# message template, so they're thrown out anyway.
warnings.filterwarnings(action="ignore", category=UnicodeWarning)

######################################
#              CLASSES               #
######################################

class MessageTerminus(object):
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
		
		self.delivery_thread = threading.Thread(target=self._MailboxMonitor, name="terminus/"+str(self.id))
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
			time.sleep(Configuration.NON_BUSY_WAIT_INTERVAL)	# avoid busy-waiting
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
				logger().log(Configuration.PO_EXTRA_VERBOSE, "MessageTerminus acquired handler lock.")
				matched = False
				for subscription in self.handlers:
					if subscription.MessageMatch(message, for_delivery=False):
						logger().log(Configuration.PO_EXTRA_VERBOSE, " ....message %s is about to be handled using subscription: %s", message.id, subscription)
						self.handlers[subscription](message)
						logger().log(Configuration.PO_EXTRA_VERBOSE, " ... message %s was handled successfully.", message.id)
						matched = True
				
					# need to make sure we remove expired subscriptions.
					if subscription.expiry < 0 or subscription.times_matched < subscription.expiry:
						handlers[subscription] = self.handlers[subscription]
					else:
						logger().debug("MessageTerminus %s dropped subscription handler (expired): %s", self.id, subscription)
				
				logger().log(Configuration.PO_EXTRA_VERBOSE, "MessageTerminus matched message %s to a subscription: %s", message.id, matched)
			
				self.handlers = handlers
			logger().log(Configuration.PO_EXTRA_VERBOSE, "MessageTerminus released handler lock.")
					
	def AddHandler(self, subscription, handler):
		""" Add a handler for messages.
		
		    PLEASE use this method instead of directly
		    appending to the handler list.  This
		    method uses a lock to protect the list
		    and make access thread-safe. """

		with self.handler_lock:
			if subscription in self.handlers:
				raise Errors.SubscriptionError("Not adding duplicate message handler: %s" % str(subscription))

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
		
		logger().log(Configuration.PO_EXTRA_VERBOSE, "MessageTerminus %s received message:\n%s", self.id, message)
		
		self.mailbox.put_nowait(message)

class _PostOfficeSocketManager(object):
	""" Performs the low-level socket communications.  Used internally by PostOffice. """
	
	# prepare a template so that we can ensure consistency.
	# the only thing that will be substituted in later is the message id.
	ACKNOWLEDGEMENT_TEXT = "%sRECV_ACK={0}%s" % (Configuration.MESSAGE_MAGIC["begin"], Configuration.MESSAGE_MAGIC["end"])
	
	def __init__(self, postoffice, listen_port=None, listen_socket=None, tls_cert=None, tls_key=None, tls_cafile=None):
	
		for prop in ("postoffice", "listen_port", "listen_socket", "tls_cert", "tls_key", "tls_cafile"):
			setattr(self, prop, locals()[prop])
		
		# the sessions we currently have in use
		self.open_inbound_sessions = []   # initiated by clients externally
		self.open_outbound_sessions = []  # initiated by us, here

		self.listener_thread = threading.Thread(target=self._Listen, name="socketmanager/listener")
		self.listener_thread.daemon = True
		
		self._last_garbage_collection = 0
		
		self._started = False
		self.time_to_quit = False
	
	def _AcceptConnection(self):
		""" Accept and queue incoming socket communications. """
	
		# we can discard the port number.  it's not important
		# since it will be a dynamic-use port (>32000) and
		# we can't contact that node there after this socket
		# has been closed.
		client_socket, client_address = self.listen_socket.accept()
		client_address = client_address[0]
		
		logger().debug("accepted connection on fd %d from client at: %s", self.listen_socket.fileno(), client_address)
		logger().debug("  new socket fd: %d", client_socket.fileno())

		certificate = None

		# if this is an SSL socket, get the other side's certificate
		if hasattr(client_socket, "getpeercert"):
			certificate = client_socket.getpeercert()					

			# the format of the certificate returned by getpeercert()
			# is *terrible*.  let's reformat it a bit.
			certificate_reformat = {}
			for item in certificate["subject"]:
				certificate_reformat[item[0][0]] = item[0][1]
			certificate = certificate_reformat
		
		session = _SocketSession(client_socket, client_address, certificate)
		self.open_inbound_sessions.append(session)
		
	def _DoGarbageCollection(self):
		""" Cleans up any stale open sessions.
		
		    A session is 'stale' if its last incoming data was read
		    more than Configuration.STALE_SOCKET_TTL seconds ago.  """
	
		sessions_to_remove = []
		now = time.time()
		for session in self.open_inbound_sessions + self.open_outbound_sessions:
			if now - session.last_read_time > Configuration.STALE_SOCKET_TTL:
				sessions_to_remove.append(session)
			
		for session in sessions_to_remove:
			logger().debug("Removing stale session: %s", session)
			self.open_inbound_sessions.remove(session)
		
		self._last_garbage_collection = time.time()
	
	def IsConfigured(self):
		# want either listen_port or listen_socket to be None, but not both, and not neither
		return (self.listen_port or self.listen_socket) != (self.listen_port and self.listen_socket)
	
	def _Listen(self):
		""" The method that runs the incoming socket communication
		    service.  (Outgoing socket communication is handled
		    via DeliveryThread objects.)
		    
		    It should be run in its own thread to ensure it doesn't
		    block things up while it waits for socket traffic (this is
		    arranged by default by the constructor). """

		logger().debug("Postoffice %s socket listener starting.", self.postoffice.id)
		finished_client_sessions = []
		while not self.time_to_quit:
			# necessary so that a connection that is not explicitly broken
			# but which goes stale is removed, thus forcing a client to
			# start fresh (rather than potentially starting a new message
			# in the middle of an old one).
			if time.time() - self._last_garbage_collection > Configuration.SOCKET_GARBAGE_COLLECTION_INTERVAL:
				self._DoGarbageCollection()


			# select returns a 3-tuple:
			#  ( [list of readers ready], [list of writers ready], [list of error state] )
			# we only will do something when we have readers ready.
			# note by supplying the last argument to select(),
			# we ask it to wait until it has a reader ready or
			# NON_BUSY_WAIT_INTERVAL seconds, whichever is shorter.
			potential_readers = [self.listen_socket,] + self.open_inbound_sessions
			socks_ready = select.select(potential_readers, [], [], Configuration.NON_BUSY_WAIT_INTERVAL)[0]
			if len(socks_ready) == 0:
				continue
			
			# first check if there are any new connections pending
			# and handle them if so.  (they'll get added to the open_inbound_sessions list,
			# so they will be read out next go-round of the scheduler.)
			if self.listen_socket in socks_ready:
				self._AcceptConnection()
				socks_ready.remove(self.listen_socket)
			
			# now read the waiting data out of the listener sockets.
			for sock in socks_ready:
				try:
					finished = self._ReadSocket(sock)
				except (socket.error, select.error), (errnum, msg):
					if errnum == errno.EINTR:		# the code for an interrupted system call
						logger().warning("Recv was interrupted by system call.  Will try again.")
					else:
						logger().exception("Error trying to receive incoming data:")
					continue
				
				if finished is None:
					self.open_inbound_sessions.remove(sock)
				elif finished:
					finished_client_sessions.append(sock)

			# next deal with the messages that have
			# been completely received.
			while len(finished_client_sessions) > 0:
				session = finished_client_sessions.pop()

				msg_text = session.message_data.pop(0)
				message = self._ReconstructMessage(msg_text, session)

				if message is None:
					logger().info("Ignoring garbage message with appropriate magic from %s.  Text received:\n%s", session.conn_info, msg_text)
					continue

				session.send(_PostOfficeSocketManager.ACKNOWLEDGEMENT_TEXT.format(message.id))

				logger().info("RECEIVED:\n%s", str(message))
				logger().info(" ... from client at address '%s'", session.conn_info)

				# pass the reconstructed message back to the parent PostOffice for processing.				
				self.postoffice.message_queue.put_nowait(message)

			
		logger().debug("PostOffice listener thread shut down.")	

	def _ReadSocket(self, session):
		""" Read a chunk of data from a socket, respecting the PostOffice begin- and end-message protocol.
		
		    The return value of this method specifies whether
		    the end of the message was found.  The special value
		    None indicates that the socket was closed and no
		    more messages will ever come from this session. """
	
		assert hasattr(session, "data_buffer")
	
		logger().debug("Reading from session: %s", session)
	
		# non-blocking read.  read only what's there!
		data = session.recv(Configuration.SOCKET_DATA_CHUNK_SIZE, socket.MSG_DONTWAIT)

		# a read of 0 bytes signifies the client
		# has closed the socket.
		if len(data) == 0:
			session.close()
			return None

		# if we don't have any data already for this socket,
		# we need to look for the magic bytes (they signal "message start").
		# if the data doesn't begin that way, it's not a PostOffice communication;
		# it wasn't intended for us, so we just close the socket.
		if len(session.data_buffer) == 0 and not data.startswith(Configuration.MESSAGE_MAGIC["begin"]):
			logger().info("Garbage incoming from %s.  Text:\n%s", session.conn_info, data)
			logger().warning(" ==> Ignoring and closing connection to host: %s", session.conn_info)
			session.shutdown(socket.SHUT_RDWR)
			session.close()
			return None
		
		session.data_buffer += data

		# now we look for the message-end magic string.
		# push all complete messages into the queue for unpacking.
		n_msgs = len(session.message_data)
		while True:
			end_pos = session.data_buffer.find(Configuration.MESSAGE_MAGIC["end"])
			if end_pos < 0:
				break
				
			end_pos += len(Configuration.MESSAGE_MAGIC["end"])
			# we found a message-end string: so pull it out.
			# leave any more in the buffer for the next time...
			session.message_data.append(session.data_buffer[:end_pos])
			session.data_buffer = session.data_buffer[end_pos:]
		
		return len(session.message_data) > n_msgs

	def _ReconstructMessage(self, msg, session):
		""" Attempt to rebuild a text stream into whatever was Pickled at transmission time. """

		# strip off the message magic... (which it must have, otherwise the message would've been jettisoned by now)
		assert msg[:len(Configuration.MESSAGE_MAGIC["begin"])] == Configuration.MESSAGE_MAGIC["begin"]
		msg = msg[len(Configuration.MESSAGE_MAGIC["begin"]):]
		assert msg[-len(Configuration.MESSAGE_MAGIC["end"]):] == Configuration.MESSAGE_MAGIC["end"]
		msg = msg[:-len(Configuration.MESSAGE_MAGIC["end"])]
	
		# verify that the message's checksum is really how long it is...
		checksum_string = msg[:Configuration.CHECKSUM_BYTES]
		checksum = NetworkTypes.Checksum.UnpackChecksum(checksum_string)
	
		# strip off the checksum too
		calc_checksum = len(msg) - Configuration.CHECKSUM_BYTES
		if calc_checksum != checksum:
			logger().debug("Message length different than checksum: length = %d; checksum = %d; checksum string", calc_checksum, checksum)
			return None
		msg = msg[Configuration.CHECKSUM_BYTES:]

		try:
			message =  cPickle.loads(msg)
		except (cPickle.UnpicklingError, TypeError, EOFError):
			return None

		if hasattr(message, "subject") and hasattr(message, "id") and hasattr(message, "return_path") and len(message.return_path) > 0:
			if session.certificate is not None:
				message.sender_certificate = session.certificate

			# the delivery thread sending this message to us
			# should have appended an IPv4Address to return_path
			# containing the port number we should be contacting it at.
			# now we add the IP address as we see it from here.
			message.return_path[-1].set_host(session.conn_info)
	
		return message
	
	def Shutdown(self):
		""" Shut down the threads belonging to this _PostOfficeSocketManager. 
		
		    Note that if you do this, you will never be
		    able to reuse this instance (its threads have
		    all been used).  Create a new _PostOfficeSocketManager
		    in that case.  """

		# first shut down the scheduler thread
		self.time_to_quit = True
		logger().info("Checking post office listener thread for shutdown...")
		if self.listener_thread.is_alive():
			self.listener_thread.join()
		logger().info("  ... shut down.")

		if self.listen_socket:
			logger().info("Shutting down listening socket...")
			self.listen_socket.close()

	def StartListening(self):
		""" Start up the various listener services.
		
		    You should only ever call this externally if
		    you didn't provide either a listen_port or
		    a listen_socket (because you want to delay
		    listening). """
	
		if self._started:
			return
	
		logger().debug("socket manager listening starting.")
		
		if (self.listen_port is None and self.listen_socket is None) or (self.listen_port is not None and self.listen_socket is not None):
			raise AttributeError("You must specify one or the other of 'listen_port' and 'listen_socket', but not both.")

		if self.listen_socket is not None:
			self.listen_port = self.listen_socket.getsockname()[1]
			logger().info("Using provided socket.  Listening at port %d.", self.listen_port)
		else:
			logger().info("Building new socket for PostOffice socket manager.")
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
				listen_socket.listen(Configuration.SOCKET_MAX_BACKLOG)				

				if self.tls_cert is not None:
					self.listen_socket = ssl.wrap_socket(
						listen_socket,
						server_side=True,
						certfile=self.tls_cert,
						keyfile=self.tls_key,
						ca_certs=self.tls_cafile,
						ssl_version=ssl.PROTOCOL_TLSv1,
						cert_reqs=ssl.CERT_REQUIRED
					)
				else:
					self.listen_socket = listen_socket
			except socket.error:
				logger().exception("Error while trying to configure & bind listening socket:")
				logger().fatal("Can't get a socket.")
				raise
		
		self.listen_socket.settimeout(Configuration.SOCKET_TIMEOUT)
		self.listener_thread.start()
		
		self._started = True

	def Transmit(self, message, ipv4address):
		""" Transmit message text to another PostOffice over an outgoing socket. """
	
		transmitted = False

		# ah, the beauty of pickle.
		# we just send the entire message *object*
		# and pickle will rebuild it on the other side!
		message_text = cPickle.dumps(message)	# doesn't include the magic or checksum

		# use a checksum so that the receiving end knows that they've gotten the whole thing.
		message_length = len(message_text)
		message_string = "%s%s%s%s" % (
			Configuration.MESSAGE_MAGIC["begin"],
			NetworkTypes.Checksum.PackChecksum(message_length),
			message_text,
			Configuration.MESSAGE_MAGIC["end"],
		)
		
		if message_length > 2**48:
			raise OverflowError("You really need to send a message bigger than 1 exobyte??  Sorry... No can do.")
	
		session = None
		# first see if we already have an open socket to use for this connection
		for s in self.open_outbound_sessions:
			if s.conn_info == ipv4address:
				session = s
				logger().debug("Using existing session: %s", s)
				break
		try:
			# if not, make one
			if session is None:
				logger().debug("Making new session for socket to host: %s", ipv4address)
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.settimeout(Configuration.SOCKET_TIMEOUT)

				if self.tls_cert is not None:
					sock = ssl.wrap_socket(
						sock,
						certfile=self.tls_cert,
						keyfile=self.tls_key,
						ca_certs=self.tls_cafile,
						ssl_version=ssl.PROTOCOL_TLSv1,
						cert_reqs=ssl.CERT_REQUIRED
					)

				sock.connect( ipv4address.to_tuple() )
				session = _SocketSession(sock=sock, client_address=ipv4address)
				self.open_outbound_sessions.append(session)
			
			# use of the 'with' statement serializes access to this socket
			# (since the _SocketSession type wraps the socket in a serializable package).
			# that means we can guarantee our message isn't interrupted
			# by another one while we're sending it.
			logger().log(5, "getting session lock:")
			with session:
				remove_session = False
				logger().log(5, "got session lock.")
				# send() might not send the whole thing.
				# it's our responsibility to make sure everything
				# is transmitted.
				bytes_sent = 0
				while bytes_sent < len(message_string):
					bytes_sent += session.send(message_string[bytes_sent:])
				response = session.recv(Configuration.SOCKET_DATA_CHUNK_SIZE)

				if response == _PostOfficeSocketManager.ACKNOWLEDGEMENT_TEXT.format(message.id):
					transmitted = True
				elif response == "":   # this means the socket was broken.  POs always respond immediately...
					logger().debug("Broken pipe for session: %s", session)
					remove_session = True
				else:
					logger().debug("Couldn't understand the response from '%s'.  Will try again.  Response was: '%s'", session.conn_info, response)

		except socket.error:
			logger().exception("Socket error:")
			remove_session = True

		if remove_session and session in self.open_outbound_sessions:
			logger().warning("Removing expired session: %s", session)
			self.open_outbound_sessions.remove(session)
			logger().debug(" Current sessions:")

		return transmitted
		
	
	
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
		
		self._socket_manager = _PostOfficeSocketManager(self, listen_port, listen_socket, tls_cert, tls_key, tls_cafile)
		
		self.id = uuid.uuid4()
		
		logger().debug("Created PostOffice with id %s", self.id)

		# now the message holders
		self.message_queue        = Queue.Queue()  # "inbox" for messages which need to be delivered or forwarded.  processed in _Schedule()
		self.pending_messages     = {}  # messages waiting for further information (delivery confirmation, etc.).  used by _Schedule().
		self.unconfirmed_messages = {}  # countdown collections of which messages are still awaiting confirmation.  messages are cleared from SendWithConfirmation when they disappear from this list
		self.unanswered_messages  = {}  # countdown collections of which messages are still awaiting responses.  messages are cleared by SnedAndWaitForResponse when they disappear from this list
		self.message_backlog      = {}  # messages whose subscriptions match but can't be delivered/forwarded (socket temporarily unavailable, another subscription using the channel, etc.).  periodically cleaned.
		self.pending_message_lock = threading.Lock()

		# subscriptions come with one for "postmaster" messages
		# already included (delivers to this object!).  it has
		# a special attribute so that we can differentiate it
		# from others added later
		postmaster_subscription = Envelope.Subscription(
			subject="postmaster",
			action=Envelope.Subscription.DELIVER,
			delivery_address=self,
			postmaster_ok=True
		)
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
		self.scheduler_thread = threading.Thread(target=self._Schedule, name="postoffice/scheduler")
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
		
		# keep track of how many messages we're waiting for confirmation
		# and/or responses for.  unless you pass "force=True" to the
		# SendWithConfirmation and/or SendAndWaitForResponse methods,
		# you can only wait for one at a time.  (if you use the 'force'
		# parameter, you assume responsibility for any deadlocks that
		# may occur!)
		self._wait_for_confirmation_count = 0
		self._wait_for_response_count = 0
		self._abort_message_wait = False
		
		self._started = False
		self.time_to_quit = False

		if self._socket_manager.IsConfigured():
			self.Startup()	

	### some properties
	
	@property
	def listen_port(self):
		return self._socket_manager.listen_port

	def listen_socket(self):
		return self._socket_manager.listen_socket
	
	####

	def AbortMessageWait(self):
		""" Abort a SendWithConfirmation or SendAndWaitForResponse.
		
		    Note that you will still get something back from the
		    SendAndWaitForResponse method when you do this: it
		    may just wind up being incomplete.  Be careful if you
		    are relying on getting a particular number of responses
		    in the code that follows!
		    
		    Also note that this will abort ALL waits that are in
		    progress (i.e., if you have passed force=True to one
		    of the wait methods)."""
	
		logger().info("Requested to abort message waits...")
		self._abort_message_wait = True
		while self._wait_for_confirmation_count > 0 and self._wait_for_response_count > 0:
			time.sleep(Configuration.NON_BUSY_WAIT_INTERVAL)
		self._abort_message_wait = False
		logger().info("Message waits aborted.")
			
	def Publish(self, message):
		""" Publish a message.
		
		    Puts the message into the message-send queue
		    so long as it's properly formed. """
		
		if not hasattr(message, "subject") and hasattr(message, "id"):
			raise Errors.MessageError("Message is badly formed.  Won't be sent...")
		
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
			recipient_subscr = Envelope.Subscription(
				action=Envelope.Subscription.FORWARD,
				delivery_address=recipient,
				expiry=1,
				other_attributes={"id": message.id}
			)
			self.AddSubscription(recipient_subscr)

		try:
			responses = self.SendWithConfirmation(message, timeout, with_exception)
		except Errors.TimeoutError:
			responses = None
		
		# need to remove any subscriptions that didn't get erased by a delivery
		for recipient in recipient_list:
			recipient_subscr = Envelope.Subscription(
				action=Envelope.Subscription.FORWARD,
				delivery_address=recipient,
				expiry=1,
				other_attributes={"id": message.id}
			)
			self.DropSubscription(recipient_subscr)
		
		if responses is None and with_exception:
			raise Errors.TimeoutError
		
		return responses
	
	def SendWithConfirmation(self, message, timeout=None, with_exception=False, force=False):
		""" Sends a message and then blocks until it gets
		    confirmation that it has been delivered (or
		    delivery failed) to all matching subscriptions,
		    unless the optional timeout is specified.
		    
		    If the message is delivered only to local objects
		    then this should return almost immediately. """

		if not hasattr(message, "subject") and hasattr(message, "id"):
			raise Errors.MessageError("Message is badly formed.  Won't be sent...")
			
		if self._wait_for_confirmation_count > 0 and not force:
			raise Errors.AlreadyWaitingError("SendWithConfirmation can't wait for multiple messages simultaneously.")

		self._wait_for_confirmation_count += 1
			
		message.status_reports = True
		self.unconfirmed_messages[message.id] = {"deliveries": None, "time_started": time.time()}
		self.Publish(message)
		
		#threading.enumerate()
		
		while True:
			if timeout is not None \
			   and (time.time() - self.unconfirmed_messages[message.id]["time_started"] > timeout) \
			   and not self._abort_message_wait:
				logger().debug("Timeout for message %s expired.", message.id)
				if with_exception:
					raise Errors.TimeoutError("Message %s send timed out...", message.id)
				else:
					break
			
			if self.unconfirmed_messages[message.id]["deliveries"] is not None:
				break
			
			time.sleep(Configuration.NON_BUSY_WAIT_INTERVAL)

		if self.unconfirmed_messages[message.id]["deliveries"] is None:
			deliveries = []
		else:
			deliveries = self.unconfirmed_messages[message.id]["deliveries"]
			logger().debug("Confirmations for message %s received from all nodes.", message.id)
		
		del self.unconfirmed_messages[message.id]

		self._wait_for_confirmation_count -= 1
		
		return deliveries

	def _Schedule(self):
		""" The method that assigns outgoing messages to delivery threads,
		    dispatches locally deliverable messages to their recipients,
		    and manages subscriptions. 
		    
		    It should be run in its own thread to ensure it doesn't
		    block things up while it waits for messages (this is
		    arranged by default by the constructor). """
		
		logger().debug("Entering PostOffice scheduling loop.")
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
					logger().log(Configuration.PO_EXTRA_VERBOSE, "Message %s is in-reply-to a message that hasn't been released yet (%s).  Putting back into the queue to retry...", message.id, message.in_reply_to)
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
						if hasattr(message, "response_requested") and message.response_requested:
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
					
					logger().log(Configuration.PO_EXTRA_VERBOSE, "Acquired global subscription lock for scheduling loop.")
#						logger().log(Configuration.PO_EXTRA_VERBOSE, "Subscriptions to check: \n%s", pprint.pformat(self.subscriptions))

					# normally this would be two of the same "for" loop
					# to prevent race conditions between the adding of items
					# to the pending_messages list and the sending of messages,
					# but the message delivery threads all wait until self.delivering
					# is False before continuing anyway.
					subscriptions = []				
					for subscription in self.subscriptions:
						logger().log(Configuration.PO_EXTRA_VERBOSE, "Considering subscription: %s", subscription)
						# remove any subscriptions that are undeliverable
						if hasattr(subscription, "failed_deliveries") \
						   and subscription.failed_deliveries >= 3 \
						   and time.time() - subscription.first_failure_time > Configuration.SUBSCRIPTION_TTL:
							logger().info("Subscription %s has exceeded the maximum number of delivery failures and will be dropped.", subscription)
							if subscription in self.message_backlog:
								del self.message_backlog[subscription]
							continue
							
						if subscription.MessageMatch(message):
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
									logger().log(Configuration.PO_EXTRA_VERBOSE, "Message %s trying to get pending message lock...", message.id)
									with self.pending_message_lock:	 
										logger().log(Configuration.PO_EXTRA_VERBOSE, "Message %s acquired pending message lock.", message.id)

										self.pending_messages[message.id]["recipient_status"].append( [address, None] )
										logger().debug("Added address %s to message %s recipient-waiting list.", address, message.id)
							
							# if the subscription is locked, or there is a queue
							# of messages waiting to be sent using this subscription,
							# this message needs to wait.
							# notice that we test for the presence of the lock by trying
							# to acquire it!
							logger().log(Configuration.PO_EXTRA_VERBOSE, "Trying to acquire lock for subscription id %s (scheduling): %s", subscription._id, subscription)
							acquired_lock = self.delivery_locks[subscription].acquire(False)		# non-blocking acquire()
							subscription_backlog = subscription in self.message_backlog
							message_in_backlog = None if not subscription_backlog else (message in self.message_backlog[subscription])
							message_index = None if not message_in_backlog else self.message_backlog[subscription].index(message)
							
							if not acquired_lock:
								logger().log(Configuration.PO_EXTRA_VERBOSE, "Failed to acquire lock id %s (scheduling).", subscription._id)
							else:
								logger().log(Configuration.PO_EXTRA_VERBOSE, "Successfully acquired lock id %s (scheduling).", subscription._id)
							
							logger().log(Configuration.PO_EXTRA_VERBOSE, "Backlog status: got lock = %s, this subscription has backlog = %s, this message in backlog = %s, message index in backlog = %s", acquired_lock, subscription_backlog, message_in_backlog, message_index)
							
							if not acquired_lock \
							   or ( subscription_backlog and ( (not message_in_backlog) or message_index > 0 ) ) :
								if acquired_lock and subscription_backlog:
									position = len(self.message_backlog[subscription]) if not message_in_backlog \
									           else message_index
									logger().log(Configuration.PO_EXTRA_VERBOSE, " ... but subscription %s has %d other messages in line for delivery first.  Putting message %s into backlog.", subscription, position, message.id)
								elif not acquired_lock:
									logger().log(Configuration.PO_EXTRA_VERBOSE, " ... but subscription %s is currently locked.  Putting message %s into backlog.", subscription, message.id)
								
								if not subscription_backlog:
									self.message_backlog[subscription] = []
								
								# make sure that this message is delivered in the order it was received!
								if not message_in_backlog:
									logger().log(Configuration.PO_EXTRA_VERBOSE, "Backlog before: %s", self.message_backlog[subscription])
									self.message_backlog[subscription].append(message)
									logger().log(Configuration.PO_EXTRA_VERBOSE, "Backlog after: %s", self.message_backlog[subscription])
								
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
							logger().log(Configuration.PO_EXTRA_VERBOSE, "Releasing lock for subscription id %s (scheduling): %s", subscription._id, subscription)
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

							logger().log(Configuration.PO_EXTRA_VERBOSE, "Copying message...")
							newmsg = copy.copy(message)		# shallow copy of most things
							newmsg.return_path = copy.deepcopy(message.return_path)	# but deep copy the return path
							delivery = (newmsg, subscription)
							logger().log(Configuration.PO_EXTRA_VERBOSE, "Finding a delivery thread...")
							dispatched = False
							for thread in self.delivery_threads:
								if not thread.busy:
									logger().log(Configuration.PO_EXTRA_VERBOSE, " ... found one.  Now trying to transfer message & delivery info...")
									thread.deliveries.put_nowait(delivery)
									dispatched = True
									logger().log(Configuration.PO_EXTRA_VERBOSE, " ... success.")
									break
							if not dispatched:
								thread = DeliveryThread(self)
								thread.deliveries.put_nowait(delivery)
								self.delivery_threads.append(thread)
								logger().debug("Created new thread for message delivery.")
						else:  # if message matched subscription
							logger().log(Configuration.PO_EXTRA_VERBOSE, "Message %s did not match subscription: %s", message.id, subscription)

						# need to make sure we remove expired subscriptions.
						if subscription.expiry < 0 or subscription.times_matched < subscription.expiry:
							subscriptions.append(subscription)
						else:
							logger().debug("Removed expired subscription: %s", subscription)
				
					self.subscriptions = subscriptions
					logger().log(Configuration.PO_EXTRA_VERBOSE, "Subscriptions left: %s", self.subscriptions)
				finally:
					self.delivering = False
					self.subscription_lock.release()
					logger().log(Configuration.PO_EXTRA_VERBOSE, "Released global subscription lock (scheduling loop).")
				
				if not matched:
					# if there were no matches and the message requests
					# delivery confirmation, send back a reply right away
					if message.id in self.pending_messages:
						delivery_msg = Envelope.Message(subject="postmaster", delivered_to=[], in_reply_to=message.id)
						self.Publish(delivery_msg)

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
				time.sleep(Configuration.NON_BUSY_WAIT_INTERVAL)
				
			# check for moldy old messages in pending_messages and messages_awaiting_release
			# that have been around for too long.  they probably won't ever get responses,
			# so just get rid of them.  (we hold them for an hour before expunging.)
#			logger().debug("Pending messages check.")
			if len(self.pending_messages) > 0:
				with self.pending_message_lock:
					new_pending_messages = {}
					for pending_message_id in self.pending_messages:
						if time.time() - self.pending_messages[pending_message_id]["time_started"] < Configuration.PENDING_MSG_TTL:
							new_pending_messages[pending_message_id] = self.pending_messages[pending_message_id]
					self.pending_messages = new_pending_messages
			
			if len(self.messages_awaiting_release) > 0:
				with self.messages_awaiting_release_lock:
					new_msgs = {}
					for msg_id in self.messages_awaiting_release:
						if time.time() - self.messages_awaiting_release[msg_id] < Configuration.PENDING_MSG_TTL:
							new_msgs[msg_id] = self.messages_awaiting_release[msg_id]
					self.messages_awaiting_release = new_msgs

		### END while not self.time_to_quit ###

		logger().debug("Scheduler thread shut down.")	
		
	
	def SendAndWaitForResponse(self, message, timeout=None, with_exception=False, force=False):
		""" Sends a message and waits for a response from the
		    remote end, with optional timeout. """
		
		if not hasattr(message, "subject") and hasattr(message, "id"):
			raise Errors.MessageError("Message is badly formed.  Won't be sent...")

		if self._wait_for_response_count > 0 and not force:
			raise Errors.AlreadyWaitingError("SendAndWaitForResponse can't wait for multiple messages simultaneously.")
				
		self._wait_for_response_count += 1

		# book a subscription for all non-postmaster messages responding to this one
		response_subscr =  Envelope.Subscription(
			in_reply_to=message.id,
			action=Envelope.Subscription.DELIVER,
			delivery_address=self,
			postmaster_ok=False
		)
		self.AddSubscription(response_subscr)
		
		# also insert a handler for said message, since we want the post office itself
		# to do the handling, then pass the message back to the caller
		with self.handler_lock:
			self.handlers[response_subscr] = self._UnansweredMessages
		
		message.response_requested = True
		
		self.unanswered_messages[message.id] = {"messages": [], "time_started": time.time()}

		deliveries = self.SendWithConfirmation(message, timeout, with_exception=with_exception, force=force)
		response_messages = []

		logger().debug("Clearing responses to message %s for delivery...", message.id)
		clear_msg = Envelope.Message(subject="postmaster", in_reply_to=message.id, response_clear=True)
		self.Publish(clear_msg)
		
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
				if timeout is not None \
				   and time.time() - self.unanswered_messages[message.id]["time_started"] > timeout \
				   and not self._abort_message_wait:
					logger().debug("Timeout expired.")
					if with_exception:
						raise Errors.TimeoutError("Timed out waiting for responses...")
					else:
						break
			
				if len(self.unanswered_messages[message.id]["messages"]) >= len(deliveries):
					break
			
				time.sleep(Configuration.NON_BUSY_WAIT_INTERVAL)
			response_messages = self.unanswered_messages[message.id]["messages"]

			logger().debug("All responses for message %s received.", message.id)
		
		# clean up
		self.DropSubscription(response_subscr)
		
		with self.handler_lock:
			del self.handlers[response_subscr]
		del self.unanswered_messages[message.id]
		
		self._wait_for_response_count -= 1

		logger().log(Configuration.PO_EXTRA_VERBOSE, "Returning!")
		
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
		
		message = Envelope.Message(subject="postmaster", remote_request="forward_request", subscriptions=new_subscriptions)

		forward_subscr = Envelope.Subscription(
			subject="postmaster",
			action=Envelope.Subscription.FORWARD,
			delivery_address=host,
			postmaster_ok=True,
			expiry=1,
			other_attributes={"id": message.id}
		)
		self.AddSubscription(forward_subscr)
		
		self.Publish(message)
		
	def ForwardCancel(self, host, subscriptions, with_confirmation=False):
		""" Contacts a remote node to cancel forwarding subscriptions.
		
		    See the caveat for ForwardRequest().  """

		new_subscriptions = []
		for subscr in subscriptions:
			if not subscr.Validate():
				raise ValueError("Subscription's parameters are invalid: %s", self)
			new_subscriptions.append(copy.deepcopy(subscr))

		message = Envelope.Message(subject="postmaster", remote_request="forward_cancel", subscriptions=new_subscriptions)

		forward_subscr = Envelope.Subscription(
			subject="postmaster",
			action=Envelope.Subscription.FORWARD,
			delivery_address=host,
			postmaster_ok=True,
			expiry=1,
			other_attributes={"id": message.id}
		)
		self.AddSubscription(forward_subscr)
		
		if with_confirmation:
			self.SendWithConfirmation(message, timeout=10)
		else:
			self.Publish(message)
		
		
	
	def _PostMasterMessages(self, message):
		""" The handler for messages with subject "postmaster". """

		logger().log(Configuration.PO_EXTRA_VERBOSE, "Postmaster message: %s", message)
		
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
							response_subscr = Envelope.Subscription(
								in_reply_to=message.in_reply_to, 
								action=Envelope.Subscription.FORWARD, 
								delivery_address=pending_info["return_address"], 
								postmaster_ok=False, 
								expiry=len(message.delivered_to)
							)
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
							clear_subscr = Envelope.Subscription(
								subject="postmaster",
								in_reply_to=message.in_reply_to,
								action=Envelope.Subscription.FORWARD,
								delivery_address=message.return_path[-1],
								postmaster_ok=True,
								expiry=1,
								other_attributes={"response_clear": True}
							)
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
					forward_subscr = Envelope.Subscription(
						subject="postmaster",
						in_reply_to=message.in_reply_to,
						action=Envelope.Subscription.FORWARD,
						delivery_address=return_address,
						expiry=1
					)
					self.AddSubscription(forward_subscr)
				
				with self.pending_message_lock:
					del self.pending_messages[message.in_reply_to]
				
				done_msg = Envelope.Message(subject="postmaster", in_reply_to=message.in_reply_to, delivered_to=recipient_list)
				self.Publish(done_msg)
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
				subscription.action = Envelope.Subscription.FORWARD
				subscription.delivery_address = NetworkTypes.IPv4Address(message.return_path[-1].host, subscription.delivery_address.port)
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
		
		logger().log(Configuration.PO_EXTRA_VERBOSE, "Entering AddSubscription()")
		
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
		
		logger().log(Configuration.PO_EXTRA_VERBOSE, "Exiting AddSubscription()")
	
	def DropSubscription(self, subscr_to_delete):
		""" Remove a subscription.
		
		    Note: this will remove ANY subscriptions that
		    are SUBSETS of this one, as well.  If you want
		    to leave the more general ones, make sure the
		    subscription you pass as an argument to this
		    method is specific! """

		logger().log(Configuration.PO_EXTRA_VERBOSE, "Going to drop subscription: %s", subscr_to_delete)

		# notice the lock.  this is very important
		# because otherwise this method is NOT thread-safe!
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

		logger().log(Configuration.PO_EXTRA_VERBOSE, "  ... done!")

	def Startup(self):
		""" Start up PostOffice message handling. """
	
		if self._started:
			return
		
		self._socket_manager.StartListening()
		
		self.scheduler_thread.start()
		
		self._started = True

	def Shutdown(self):
		""" Shut down this PostOffice.
		
		    Note that if you shut this instance down, you cannot reuse it after that.
		    Create a new one if you subsequently need to send messages. """

		self.time_to_quit = True

		logger().info("Shutting down the PostOffice's socket manager...")	
		self._socket_manager.Shutdown()
	
		# wait for the scheduler to shut down too
		logger().info("Waiting for the scheduler thread to finish...")	
		self.scheduler_thread.join()

		# now shut down the delivery threads
		self.delivering = False
		logger().info("Shutting down delivery threads...")
		for thread in self.delivery_threads:
			if not thread.is_alive():
				continue
				
			thread.Shutdown()
			thread.join()
	
		# finally, shut down the thread inherited from the MessageTerminus
		logger().info("Shutting down the PostOffice's MessageTerminus...")
		self.Close()
		
		logger().info("PostOffice %s shut down successfully.", self.id)


class DeliveryThread(threading.Thread):
	""" A thread subtype for delivering messages.
	
	    Used by a PostOffice object (which keeps a pool
	    of these guys). """

	def __init__(self, postoffice):
		threading.Thread.__init__(self, name="postoffice/delivery")
		
		self.deliveries = Queue.Queue()
		self.daemon = True
		
		self.postoffice = postoffice
		self.busy = False

		self._shutdown = False

		self.start()

	def _CheckDeliveryStatus(self, message, subscription, delivered):
		nodelivery_msg = None
		with self.postoffice.pending_message_lock:
			if delivered:
				# add this location to the list of deliveries
				logger().log(Configuration.PO_EXTRA_VERBOSE, "Acquired pending message lock...")
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
				nodelivery_msg = Envelope.Message(subject="postmaster", in_reply_to=message.id, delivered_to=[])
				nodelivery_msg.return_path = [ copy.deepcopy(subscription.delivery_address), ]
				
		# note: can't do this within the 'with' block above
		# because _PostMasterMessages also wants that same lock...
		# ...  ==> deadlock.
		if nodelivery_msg is not None:
			self.postoffice._PostMasterMessages(nodelivery_msg)
			logger().debug(" ==> returned from handling 'forged' message.")

		
	def _DeliverMessage(self, message, subscription):
		""" Transfers a message to a MessageTerminus for delivery. """
		
		subscription.delivery_address._TakeDelivery(message)

		# we're done with this message.  log our success, then
		# (if requested) send a notification to the return address
		# that the message was delivered
		if subscription.delivery_address == self:
			logger().debug("DELIVERED to local post office: message %s.", message.id)
		else:
			logger().info( "DELIVERED to '%s': message %s", subscription.delivery_address.id, message.id )
			if hasattr(message, "status_reports") and message.status_reports == True:
				self.postoffice.Publish(Envelope.Message(subject="postmaster", in_reply_to=message.id, delivered_to=[subscription.delivery_address.id,]))
	
		return True
	
		
	
	def run(self):
		""" The master scheduler method. """
		
		while True:
			# this blocks on a message.
			# that's okay; it needs one to do anything anyway.
			item = self.deliveries.get()

			# this is how we shut down.
			if self._shutdown:
				break
			
			message, subscription = item
			
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
			if subscription.action != Envelope.Subscription.DELIVER:
				message.return_path.append( NetworkTypes.IPv4Address(None, self.postoffice._socket_manager.listen_port) ) 
			
			# wait until it's safe to deliver this message
			try:
				logger().log(Configuration.PO_EXTRA_VERBOSE, "Acquiring lock for subscription id %s (delivery): %s", subscription._id, subscription)
				self.postoffice.delivery_locks[subscription].acquire()
				logger().log(Configuration.PO_EXTRA_VERBOSE, "Successfully acquired lock for subscription id %s (delivery)", subscription._id)
				while self.postoffice.delivering:
					time.sleep(Configuration.NON_BUSY_WAIT_INTERVAL)

				start_time = time.time()
				delivered = False
				attempts = 1
				while not delivered and attempts < Configuration.MAX_DELIVERY_ATTEMPTS:
					logger().debug(
						"Delivery attempt #%d for message %s to recipient %s:",
			               attempts, message.id, 
			               subscription.delivery_address if not hasattr(subscription.delivery_address, "id") else subscription.delivery_address.id
					)
					if subscription.action == Envelope.Subscription.DELIVER:
						delivered = self._DeliverMessage(message, subscription)
							
					# 'postmaster' messages should never be forwarded...
					# ... unless the subscription specifically requests
					# that it wants 'postmaster' messages AND it either wants
					# replies for this particular message or it's a request
					# intended for a remote node
					elif subscription.action == Envelope.Subscription.FORWARD:
						if message.subject != "postmaster" \
								or (subscription.subject == "postmaster" and ( subscription.in_reply_to == message.in_reply_to or hasattr(message, "remote_request")) ):

							logger().debug( "SENDING to post office at %s: message %s", subscription.delivery_address, message.id )
							delivered = self.postoffice._socket_manager.Transmit(message, subscription.delivery_address)

							if delivered:
								logger().info("FORWARDED to host %s: message %s", subscription.delivery_address, message.id)
								if hasattr(subscription, "failed_deliveries"):
									del subscription.failed_deliveries
									del subscription.first_failure_time
							else:
								logger().warning(" ==> Message %s was not transmitted to host %s.", message.id, subscription.delivery_address)
		
								# the post office will delete this subscription
								# after a sufficient number of failed deliveries
								# over a certain time period (see Configuration module)
								if hasattr(subscription, "failed_deliveries"):
									subscription.failed_deliveries += 1
								else:
									subscription.failed_deliveries = 1
									subscription.first_failure_time = time.time()
								logger().debug("Subscription %s has %d delivery failures...", subscription, subscription.failed_deliveries)
				
							
						else:
							logger().info("NOT FORWARDING postmaster message %s.", message.id)
							break

					attempts += 1

				# if the message didn't go anywhere and we want a status report,
				# make sure that it's clear it wasn't delivered.
				if message.id in self.postoffice.pending_messages:
					self._CheckDeliveryStatus(message, subscription, delivered)
				
				if delivered:
					# make sure the list size doesn't grow indefinitely
					if len(subscription.messages_delivered) > Configuration.MAX_RETAINED_DELIVERED_MGS:
						subscription.messages_delivered.pop()
				else:
					# if the message WASN'T able to be delivered, we MUST
					# remove it from the 'delivered' list so that it can
					# be retried if necessary.
					subscription.messages_delivered.remove(message.id)
						

			finally:
				if subscription in self.postoffice.delivery_locks:
					self.postoffice.delivery_locks[subscription].release()
				logger().log(Configuration.PO_EXTRA_VERBOSE, "Released lock for subscription id %s (delivery): %s", subscription._id, subscription)		

			self.busy = False
			
			logger().log(Configuration.PO_EXTRA_VERBOSE, "Done handling message %s.  Time spent: %f seconds.", message.id, time.time()-start_time)
			
	def Shutdown(self):
		""" Sends the "shutdown" signal to the thread if it's still running. """
		
		if self.is_alive:
			self._shutdown = True
			
			# put a dummy message in the queue in case there are no others
			# (otherwise, nothing would happen since the scheduler blocks
			#  until it gets a message)
			self.deliveries.put( Envelope.Message(subject="postmaster", _delivery_thread_quit=True) )

class _SocketSession(NetworkTypes.SerializedSocket):
	""" An object which maintains the state of an open PostOffice socket connection. """

	def __init__(self, sock, client_address, certificate=None):
		assert isinstance(sock, socket.socket)
		
		self.conn_info = client_address
		self.certificate = certificate

		self.data_buffer = ""
		self.message_data = []  # multiple messages are possible
		self.last_read_time = 0	
		
		super(_SocketSession, self).__init__(socket=sock)

	def __repr__(self):
		return "TCP socket session with host: %s" % self.conn_info
		
	def recv(self, *args, **kwargs):
		""" Pass the recv on to the socket, updating our time now """
		
		self.last_read_time = time.time()
		return self._socket.recv(*args, **kwargs)
	
	def send(self, *args, **kwargs):
		self.last_read_time = time.time()
		return self._socket.send(*args, **kwargs)
