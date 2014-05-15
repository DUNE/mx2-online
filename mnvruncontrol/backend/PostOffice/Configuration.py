"""
   Configuration.py:
    Configurable constants.
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    June-October 2010
                    
   Address all complaints to the management.
"""

# we use a 'magic' set of bytes at the beginning of
# every PostOffice message sent over the socket
# to indicate that they're really from a PostOffice.
# (obviously this can be spoofed, but it will prevent
# accidental reconstruction of a socket communication
# that was sent by some other service -- e.g., a port scanner.)
MESSAGE_MAGIC = {
	"begin": u"%PO_BEGIN_MSG%",
	"end": u"%PO_END_MSG%",
}
CHECKSUM_BYTES = 8

# socket parameters
SOCKET_TIMEOUT   = 1.5    # how long a socket is given to connect, in seconds
SOCKET_DATA_CHUNK_SIZE = 1024  # size of chunks to read/write through sockets, in bytes
SOCKET_MAX_BACKLOG = 5    # maximum number of back-logged socket connections to allow

# logging
PO_EXTRA_VERBOSE = 5  # log level of extra-verbose stream

# lifetimes of various PostOffice objects
PENDING_MSG_TTL = 300   # time a message can be in pending (i.e., awaiting delivery confirmation or response) status, in seconds
SUBSCRIPTION_TTL = 60   # time a subscription can have delivery failures before it's deleted, in seconds
STALE_SOCKET_TTL = 60   # length of time a socket session with an unfinished message lives before it is closed, in seconds

# PostOffice thresholds
MAX_DELIVERY_ATTEMPTS = 5          # maximum number of times a delivery thread will attempt to deliver a message before giving up
MAX_RETAINED_DELIVERED_MGS = 1000  # maximum number of message IDs to store in the "messages delivered" list

# etc.
NON_BUSY_WAIT_INTERVAL = 0.001  # amount of time to wait between interations in busy-loops, in seconds
# how often to check for stale socket sessions
# (i.e., sessions with an unfinished message with no transmissions in STALE_SOCKET_TTL seconds),
# in seconds
SOCKET_GARBAGE_COLLECTION_INTERVAL = 5*60

