"""
  PostOffice:
   A package providing a relatively versatile message delivery system.
   
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
"""
__all__ = ["Configuration", "Envelope", "Errors", "Logging", "NetworkTypes", "Routing"]