"""
  Events.py:
  Errors used by the run control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Nov. 2010
                    
   Address all complaints to the management.
"""

class AlertError(Exception):
	pass

class ConfigurationError(Exception):
	pass
	
class FileError(Exception):
	pass
	
class NodeError(Exception):
	pass
	
class RunError(Exception):
	pass
