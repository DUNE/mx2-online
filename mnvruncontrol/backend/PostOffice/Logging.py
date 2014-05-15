"""
   Logging.py:
    Basic structure for the logging of the PostOffice.
   
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    June-October 2010
                    
   Address all complaints to the management.
"""

import logging

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
