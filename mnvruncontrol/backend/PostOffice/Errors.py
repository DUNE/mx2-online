"""
   Errors.py:
    PostOffice custom error types

   Original author: J. Wolcott (jwolcott@fnal.gov)
                    June-October 2010
                    
   Address all complaints to the management.
"""

class Error(Exception):
	pass

class AlreadyWaitingError(Exception):
	pass
	
class TimeoutError(Exception):
	pass
	
class MessageError(Exception):
	pass

class SubscriptionError(Exception):
	pass

class SocketError(Error):
	pass
