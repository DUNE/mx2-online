"""
   NetworkTypes.py:
    Classes for custom network work.
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    June-October 2010
                    
   Address all complaints to the management.
"""
import socket
import threading

class Checksum(object):
	""" Static-method-only class containing methods for calculating and unpacking checksums. """

	# note that this class uses 7-bit (not 8-bit) 'bytes' because the socket protocol
	# can't handle characters with code points higher than 127...

	@staticmethod
	def UnpackChecksum(checksum_string):
		checksum = 0
		for char in checksum_string:
			checksum <<= 7
			checksum += ord(char)

		return checksum
	
	@staticmethod
	def PackChecksum(value):
		return "".join( [chr((value >> shift_amt*7) & 0x7F) for shift_amt in range(7, -1, -1)] )
	

class IPv4Address(object):
	""" An IPv4 address wrapper that does intelligent things
	    like translate DNS-resolvable names to IP addresses. """
	def __init__(self, host, port):
		self.set_host(host)
		self.set_port(port)
		
	def __cmp__(self, other):
		if self.host == other.host:
			if self.port == other.port:	
				return 0
			return -1 if self.port < other.port else 1
		
		return  -1 if self.host < other.host else 1
	
		
	def __eq__(self, other):
		if hasattr(other, "__iter__"):
			try:
				other = IPv4Address.from_iter(other)
			except (TypeError, ValueError):
				return False

		if not hasattr(other, "host") or not hasattr(other, "port"):
			return False

		return other.host == self.host and other.port == self.port
		
	def __hash__(self):
		return hash("%s:%s" % (self.host, self.port))
		
	def __repr__(self):
		return "%s:%s" % (self.host, self.port)
		
	def set_host(self, host):
		# None is allowed for not-yet-fully-configured addresses
		if host is None:
			self.host = None
			return
			
		if not isinstance(host, str):
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
		
		if isinstance(lst, str):
			raise TypeError("lst must not be a string!")
		
		if not hasattr(lst, "__iter__"):
			raise TypeError("lst must be an iterable type!")
		
		if len(lst) != 2:
			raise ValueError("lst must be of the form ['host', port]")
		
		return IPv4Address(lst[0], lst[1])
		
class SerializedSocket(object):
	""" A socket that can be locked for atomic use via a threading.Lock. """

	def __init__(self, *args, **kwargs):
		# unless lock_when_used is False,
		# the lock will be acquired (blocking if necessary!)
		# whenever a socket method is used
	
		if "lock_when_used" in kwargs:
			self._lock_when_used = kwargs["lock_when_used"]
			del kwargs["lock_when_used"]
		else:
			self._lock_when_used = True
	
		self._lock = threading.Lock()
		
		# you can specify your own socket if you want
		self._socket = None
		if "socket" in kwargs:
			self._socket = kwargs["socket"]
		else:
			self._socket = socket.socket(*args, **kwargs)

	# context management ('with' statement) methods
	def __enter__(self):
		self.acquire()

	def __exit__(self, typ, value, traceback):
		self.release()

	# reproduce the Lock methods
	def acquire(self):
		self._lock.acquire()

	def release(self):
		self._lock.release()
		
		
	# interface to the socket
	def __getattr__(self, attr):
		""" Provides the socket interface to the SerializedSocket object.

		The SerializedSocket class is a wrapper around an internal '_socket' element, which contains the actual socket.
		For it to work transparently, method and attribute lookups that apply to the internal '_socket'
		need to be passed along to it.  This method does that.

		Note that __getattr__() is ONLY called when regular attribute lookup fails: so if this class
		happens to shadow a method in the '_socket' by giving it the same name, then this class's
		version is the only one that will be called.
		"""
		
		if hasattr(self._socket, attr):
			try:
				if self._lock_when_used:
					self.acquire()
					
				return getattr(self._socket, attr)

			# we want to return the attribute error for me,
			# the top-level object, not my socket object
			except AttributeError:
				pass

			# always release the lock!
			finally:
				if self._lock_when_used:
					self.release()

		# this is ok since __getattr__ is only called
		# when normal attribute lookup fails.
		raise AttributeError("'%s' object has no attribute '%s'" % (type(self), attr))

